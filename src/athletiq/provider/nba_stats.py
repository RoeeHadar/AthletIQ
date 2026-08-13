# Implements: FR-001, CON-007, ADR-011, CR-002 — live HTTP adapter (not used in CI)
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
from athletiq.provider.seasons import active_season_years

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
    """Map API row to parse_game-shaped dict, or None if unusable."""
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
    if home_pts is None or away_pts is None:
        return None
    season = season_start_year(tip)
    return {
        "id": str(gid),
        "date": tip.isoformat(),
        "season": season,
        "status": "Finished",
        "teams": {
            "home": {"id": home, "name": NBA_TEAM_NAMES.get(home, home)},
            "away": {"id": away, "name": NBA_TEAM_NAMES.get(away, away)},
        },
        "scores": {"home": {"total": int(home_pts)}, "away": {"total": int(away_pts)}},
    }


class NbaStatsApiProvider:
    """Pages newest-first; filters into AthletIQ season start years (ADR-011)."""

    def __init__(
        self,
        *,
        seasons: list[int] | None = None,
        season_depth: int = 2,
        base_url: str = DEFAULT_BASE,
        page_size: int = PAGE_SIZE,
        get_json: Callable[[str], dict[str, Any]] | None = None,
        pause_seconds: float = PAGE_PAUSE_SECONDS,
    ) -> None:
        self._seasons = seasons if seasons is not None else active_season_years(depth=season_depth)
        self._base_url = base_url.rstrip("/")
        self._page_size = page_size
        self._get_json = get_json or self._http_get
        self._pause = pause_seconds
        self._games_by_season: dict[int, list[dict[str, Any]]] = {s: [] for s in self._seasons}
        self._teams: list[dict[str, Any]] = []
        self._loaded = False

    def fetch_teams(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._teams)

    def fetch_games(self, season: int) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._games_by_season.get(season, []))

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        wanted = set(self._seasons)
        earliest = date(min(self._seasons), 9, 1)
        seen_ids: set[str] = set()
        page = 1
        pages = 1
        while page <= pages:
            payload = self._get_json(
                f"{self._base_url}/api/games?{urlencode({'page': page, 'pageSize': self._page_size})}"
            )
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
                if tip.date() >= earliest:
                    all_before_window = False
                gid = str(mapped["id"])
                if gid in seen_ids:
                    continue
                seen_ids.add(gid)
                season = int(mapped["season"])
                if season in wanted:
                    self._games_by_season[season].append(mapped)
            logger.info(
                "nba-stats page=%s/%s kept=%s",
                page,
                pages,
                sum(len(v) for v in self._games_by_season.values()),
            )
            if not rows or (mapped_on_page > 0 and all_before_window):
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
