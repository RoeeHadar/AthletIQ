# Implements: FR-002, FR-013, FR-017, FR-018, CR-004
"""Validate provider-shaped records; skip noisy rows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TeamRecord:
    provider_team_id: str
    name: str
    abbreviation: str | None = None
    conference: str | None = None
    division: str | None = None
    sport: str = "basketball"
    league: str = "nba"


@dataclass(frozen=True)
class GameRecord:
    provider_game_id: str
    season: int
    game_start_time: datetime
    home_provider_team_id: str
    away_provider_team_id: str
    home_score: int | None = None
    away_score: int | None = None
    home_win: bool | None = None
    status: str = "unknown"
    sport: str = "basketball"
    league: str = "nba"


@dataclass(frozen=True)
class PlayerRecord:
    provider_player_id: str
    full_name: str
    provider_team_id: str | None = None
    league: str = "nba"


@dataclass(frozen=True)
class PlayerGameStatRecord:
    provider_game_id: str
    provider_player_id: str
    provider_team_id: str
    league: str = "nba"
    minutes: float | None = None
    points: int | None = None
    rebounds: int | None = None
    assists: int | None = None
    steals: int | None = None
    blocks: int | None = None
    turnovers: int | None = None


@dataclass(frozen=True)
class OddsSnapshotRecord:
    provider_game_id: str
    captured_at: datetime
    source: str
    implied_p_home_win: float
    league: str = "nba"


def parse_team(raw: dict[str, Any]) -> TeamRecord | str:
    """Return TeamRecord or skip reason string."""
    tid = raw.get("id")
    name = raw.get("name")
    if tid is None or name is None or str(name).strip() == "":
        return "team missing id or name"
    return TeamRecord(
        provider_team_id=str(tid),
        name=str(name).strip(),
        abbreviation=(str(raw["code"]) if raw.get("code") is not None else None),
        conference=(str(raw["conference"]) if raw.get("conference") is not None else None),
        division=(str(raw["division"]) if raw.get("division") is not None else None),
        sport=str(raw.get("sport") or "basketball"),
        league=str(raw.get("league") or "nba").lower(),
    )


def parse_game(raw: dict[str, Any], *, default_season: int | None = None) -> GameRecord | str:
    """Return GameRecord or skip reason string."""
    gid = raw.get("id")
    if gid is None:
        return "game missing id"
    teams = raw.get("teams") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    home_id = home.get("id")
    away_id = away.get("id")
    if home_id is None or away_id is None:
        return "game missing home/away team id"
    if home_id == away_id:
        return "game home and away team identical"

    date_raw = raw.get("date")
    if not date_raw:
        return "game missing date"
    try:
        tip = datetime.fromisoformat(str(date_raw).replace("Z", "+00:00"))
    except ValueError:
        return "game invalid date"

    season = raw.get("season", default_season)
    if season is None:
        # Infer from tip year (MVP heuristic aligned with season labeling).
        season = tip.year if tip.month >= 9 else tip.year - 1
    try:
        season_i = int(season)
    except (TypeError, ValueError):
        return "game invalid season"

    scores = raw.get("scores") or {}
    home_score = _score(scores.get("home"))
    away_score = _score(scores.get("away"))
    home_win: bool | None = None
    if home_score is not None and away_score is not None:
        home_win = home_score > away_score

    status = str(raw.get("status") or "unknown")
    return GameRecord(
        provider_game_id=str(gid),
        season=season_i,
        game_start_time=tip,
        home_provider_team_id=str(home_id),
        away_provider_team_id=str(away_id),
        home_score=home_score,
        away_score=away_score,
        home_win=home_win,
        status=status,
        sport=str(raw.get("sport") or "basketball"),
        league=str(raw.get("league") or "nba").lower(),
    )


def _score(node: Any) -> int | None:
    if node is None:
        return None
    if isinstance(node, dict):
        total = node.get("total")
        return int(total) if total is not None else None
    try:
        return int(node)
    except (TypeError, ValueError):
        return None


def parse_player(raw: dict[str, Any]) -> PlayerRecord | str:
    pid = raw.get("id")
    name = raw.get("name") or raw.get("full_name")
    if pid is None or name is None or str(name).strip() == "":
        return "player missing id or name"
    team = raw.get("team") or {}
    team_id = raw.get("team_id") or team.get("id")
    return PlayerRecord(
        provider_player_id=str(pid),
        full_name=str(name).strip(),
        provider_team_id=str(team_id) if team_id is not None else None,
        league=str(raw.get("league") or "nba").lower(),
    )


def parse_player_game_stat(raw: dict[str, Any]) -> PlayerGameStatRecord | str:
    gid = raw.get("game_id") or raw.get("provider_game_id")
    pid = raw.get("player_id") or raw.get("provider_player_id")
    tid = raw.get("team_id") or raw.get("provider_team_id")
    if gid is None or pid is None or tid is None:
        return "player_game_stat missing game/player/team id"
    minutes = raw.get("minutes")
    try:
        minutes_f = float(minutes) if minutes is not None else None
    except (TypeError, ValueError):
        minutes_f = None
    return PlayerGameStatRecord(
        provider_game_id=str(gid),
        provider_player_id=str(pid),
        provider_team_id=str(tid),
        league=str(raw.get("league") or "nba").lower(),
        minutes=minutes_f,
        points=_score(raw.get("points")),
        rebounds=_score(raw.get("rebounds")),
        assists=_score(raw.get("assists")),
        steals=_score(raw.get("steals")),
        blocks=_score(raw.get("blocks")),
        turnovers=_score(raw.get("turnovers")),
    )


def parse_odds_snapshot(raw: dict[str, Any]) -> OddsSnapshotRecord | str:
    gid = raw.get("game_id") or raw.get("provider_game_id")
    captured = raw.get("captured_at") or raw.get("date")
    p = raw.get("implied_p_home_win")
    if gid is None or captured is None or p is None:
        return "odds snapshot missing game_id, captured_at, or implied_p_home_win"
    try:
        tip = datetime.fromisoformat(str(captured).replace("Z", "+00:00"))
    except ValueError:
        return "odds snapshot invalid captured_at"
    try:
        p_f = float(p)
    except (TypeError, ValueError):
        return "odds snapshot invalid implied_p_home_win"
    if not 0.0 <= p_f <= 1.0:
        return "odds snapshot implied_p_home_win out of range"
    source = str(raw.get("source") or "synthetic")
    return OddsSnapshotRecord(
        provider_game_id=str(gid),
        captured_at=tip,
        source=source,
        implied_p_home_win=p_f,
        league=str(raw.get("league") or "nba").lower(),
    )
