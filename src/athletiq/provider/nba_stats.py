# Implements: FR-001, FR-021, FR-027, CON-007, ADR-011, ADR-017, CR-002, CR-005 — live HTTP adapter (not used in CI)
"""No-key NBA Stats API client (api.server.nbaapi.com)."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from datetime import date, datetime
from typing import Any, Callable
from urllib.parse import urlencode

from athletiq.provider.retry import parse_retry_after, retry_with_backoff

logger = logging.getLogger("athletiq.provider")

DEFAULT_BASE = "https://api.server.nbaapi.com"
PAGE_SIZE = 100
PAGE_PAUSE_SECONDS = 0.15

# Common historical / alternate abbreviations → current id.
_ALIASES = {
    "PHO": "PHX",
    "BRK": "BKN",
    "CHO": "CHA",
    "NJN": "BKN",
    "NOH": "NOP",
    "NOK": "NOP",
}

NBA_TEAM_NAMES: dict[str, str] = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "LA Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards",
}


class HttpError(RuntimeError):
    def __init__(self, status: int, body: str, retry_after: str | None = None) -> None:
        super().__init__(f"HTTP {status}")
        self.status = status
        self.body = body
        self.retry_after = retry_after


def season_start_year(tip: datetime) -> int:
    """AthletIQ season label: year the NBA season starts (Oct)."""
    return tip.year if tip.month >= 9 else tip.year - 1


def normalize_team_code(raw: str) -> str:
    code = str(raw).strip().upper()
    return _ALIASES.get(code, code)


def to_provider_game(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Map API row to parse_game-shaped dict, or None if unusable.

    Null scores are kept (FR-021). Status is not hardcoded Finished (ADR-015).
    Non-NBA / unmappable teams are still skipped.
    """
    gid = raw.get("gameId") or raw.get("id")
    if gid is None:
        return None
    home = normalize_team_code(str(raw.get("homeTeam") or ""))
    away = normalize_team_code(str(raw.get("visitorTeam") or raw.get("awayTeam") or ""))
    if home not in NBA_TEAM_NAMES or away not in NBA_TEAM_NAMES or home == away:
        return None
    date_raw = raw.get("date")
    if not date_raw:
        return None
    try:
        tip = datetime.fromisoformat(str(date_raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    home_pts = raw.get("homePts")
    away_pts = raw.get("visitorPts")
    home_total = int(home_pts) if home_pts is not None else None
    away_total = int(away_pts) if away_pts is not None else None
    season = season_start_year(tip)
    clock = raw.get("gameStatusText") or raw.get("clock")
    return {
        "id": str(gid),
        "date": tip.isoformat(),
        "season": season,
        "status": map_game_status(raw, home_total, away_total),
        "clock": clock if clock and str(clock).strip() and "final" not in str(clock).lower() else None,
        "teams": {
            "home": {"id": home, "name": NBA_TEAM_NAMES.get(home, home)},
            "away": {"id": away, "name": NBA_TEAM_NAMES.get(away, away)},
        },
        "scores": {"home": {"total": home_total}, "away": {"total": away_total}},
        "playerGameBasicStats": list(raw.get("playerGameBasicStats") or []),
    }


def map_game_status(raw: dict[str, Any], home_pts: int | None, away_pts: int | None) -> str:
    text = str(raw.get("gameStatusText") or raw.get("status") or "").strip().lower()
    if text in {"finished", "final", "closed"} or "final" in text:
        return "Finished"
    if any(token in text for token in ("q1", "q2", "q3", "q4", "ot", "halftime", "live", "in progress")):
        return "in_progress"
    if home_pts is None or away_pts is None:
        return "scheduled"
    return "Finished"


def _minutes_to_float(raw: Any) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).strip()
    if ":" in text:
        minutes, _, seconds = text.partition(":")
        try:
            return float(minutes) + float(seconds) / 60.0
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None


def to_player_game_stats(mapped_game: dict[str, Any]) -> list[dict[str, Any]]:
    """Map per-game boxes on a mapped nba-stats row into parse_player_game_stat shape."""
    boxes = mapped_game.get("playerGameBasicStats") or []
    if not isinstance(boxes, list):
        return []
    gid = mapped_game.get("id")
    home_id = ((mapped_game.get("teams") or {}).get("home") or {}).get("id")
    away_id = ((mapped_game.get("teams") or {}).get("away") or {}).get("id")
    out: list[dict[str, Any]] = []
    for box in boxes:
        if not isinstance(box, dict):
            continue
        pid = box.get("playerId") or box.get("personId") or box.get("id")
        name = box.get("playerName") or box.get("name") or box.get("full_name")
        if pid is None or not name:
            continue
        team_raw = box.get("teamTricode") or box.get("team") or box.get("teamAbbr") or ""
        team = normalize_team_code(str(team_raw)) if team_raw else ""
        if team not in NBA_TEAM_NAMES:
            if home_id and away_id:
                is_home = bool(box.get("isHome") or box.get("home"))
                team = str(home_id if is_home else away_id)
            else:
                continue
        if team not in NBA_TEAM_NAMES:
            continue
        out.append(
            {
                "id": str(pid),
                "name": str(name).strip(),
                "game_id": str(gid),
                "player_id": str(pid),
                "team_id": team,
                "league": "nba",
                "minutes": _minutes_to_float(box.get("min") or box.get("minutes")),
                "points": box.get("pts") if box.get("pts") is not None else box.get("points"),
            }
        )
    return out


class NbaStatsApiProvider:
    """Pages newest-first. Live NBA history is uncapped unless `seasons` is set (ADR-017)."""

    def __init__(
        self,
        *,
        seasons: list[int] | None = None,
        season_depth: int = 3,
        base_url: str = DEFAULT_BASE,
        page_size: int = PAGE_SIZE,
        get_json: Callable[[str], dict[str, Any]] | None = None,
        pause_seconds: float = PAGE_PAUSE_SECONDS,
        max_pages: int | None = None,
    ) -> None:
        self._wanted = set(seasons) if seasons is not None else None
        self._season_depth = season_depth
        self._base_url = base_url.rstrip("/")
        self._page_size = page_size
        self._get_json = get_json or self._http_get
        self._pause = pause_seconds
        self._max_pages = max_pages
        self._games_by_season: dict[int, list[dict[str, Any]]] = {}
        self._players: dict[str, dict[str, Any]] = {}
        self._player_game_stats: list[dict[str, Any]] = []
        self._teams: list[dict[str, Any]] = []
        self._loaded = False

    def leagues(self) -> list[str]:
        return ["nba"]

    def available_seasons(self, league: str = "nba") -> list[int]:
        if league != "nba":
            return []
        self._ensure_loaded()
        return sorted(self._games_by_season)

    def fetch_teams(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._teams)

    def fetch_games(self, season: int, league: str = "nba") -> list[dict[str, Any]]:
        if league != "nba":
            return []
        self._ensure_loaded()
        return list(self._games_by_season.get(season, []))

    def fetch_players(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._players.values())

    def fetch_player_game_stats(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._player_game_stats)

    def fetch_odds_snapshots(self) -> list[dict[str, Any]]:
        return []

    def fetch_newest_pages(self, *, pages: int = 1) -> list[dict[str, Any]]:
        """Board poll: map newest pages only (ADR-015). Does not page all history."""
        mapped: list[dict[str, Any]] = []
        for page in range(1, max(1, pages) + 1):
            payload = self._get_json(self._games_url(page))
            rows = list(payload.get("data") or [])
            for raw in rows:
                game = to_provider_game(raw)
                if game is not None:
                    mapped.append(game)
        return mapped

    def _games_url(self, page: int) -> str:
        return (
            f"{self._base_url}/api/games?"
            f"{urlencode({'page': page, 'pageSize': self._page_size, 'include': 'playerGameBasicStats'})}"
        )

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        seen_ids: set[str] = set()
        page = 1
        pages = 1
        earliest = None
        if self._wanted:
            earliest = date(min(self._wanted), 9, 1)
        while page <= pages:
            if self._max_pages is not None and page > self._max_pages:
                break
            payload = self._get_json(self._games_url(page))
            rows = list(payload.get("data") or [])
            pagination = payload.get("pagination") or {}
            pages = int(pagination.get("pages") or page)
            mapped_on_page = 0
            all_before_window = True
            for raw in rows:
                mapped = to_provider_game(raw)
                if mapped is None:
                    continue
                mapped_on_page += 1
                tip = datetime.fromisoformat(mapped["date"])
                if earliest is None or tip.date() >= earliest:
                    all_before_window = False
                gid = str(mapped["id"])
                if gid in seen_ids:
                    continue
                seen_ids.add(gid)
                season = int(mapped["season"])
                if self._wanted is not None and season not in self._wanted:
                    continue
                self._games_by_season.setdefault(season, []).append(mapped)
                for stat in to_player_game_stats(mapped):
                    self._player_game_stats.append(stat)
                    pid = str(stat["player_id"])
                    self._players[pid] = {
                        "id": pid,
                        "name": stat["name"],
                        "team_id": stat["team_id"],
                        "league": "nba",
                    }
            logger.info(
                "nba-stats page=%s/%s kept=%s",
                page,
                pages,
                sum(len(v) for v in self._games_by_season.values()),
            )
            if not rows:
                break
            if earliest is not None and mapped_on_page > 0 and all_before_window:
                break
            page += 1
            if page <= pages and self._pause > 0:
                time.sleep(self._pause)
        self._teams = [
            {"id": code, "name": name, "code": code}
            for code, name in sorted(NBA_TEAM_NAMES.items())
        ]
        self._loaded = True

    def _http_get(self, url: str) -> dict[str, Any]:
        def operation() -> dict[str, Any]:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json", "User-Agent": "AthletIQ/0.1"},
                method="GET",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                body = exc.read().decode("utf-8", errors="replace")
                raise HttpError(exc.code, body, retry_after) from exc

        def is_retryable(exc: BaseException) -> bool:
            if isinstance(exc, HttpError):
                return exc.status in {408, 425, 429, 500, 502, 503, 504}
            return isinstance(exc, (TimeoutError, urllib.error.URLError))

        def get_retry_after(exc: BaseException) -> float | None:
            if isinstance(exc, HttpError):
                return parse_retry_after(exc.retry_after)
            return None

        return retry_with_backoff(
            operation,
            is_retryable=is_retryable,
            get_retry_after=get_retry_after,
        )
