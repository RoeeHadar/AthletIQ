# Implements: FR-002, FR-013
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
