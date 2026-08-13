# Implements: FR-003
"""In-memory analytics matching SQL semantics for exact fixture tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlayerGameLine:
    player_id: int
    full_name: str
    season: int
    points: int
    game_start_time: datetime


@dataclass(frozen=True)
class TeamGameLine:
    team_id: int
    points_for: int
    game_start_time: datetime


def top_scorers_by_season(
    lines: list[PlayerGameLine],
    season: int,
) -> list[tuple[int, str, int, int]]:
    """Return (player_id, full_name, season, points) ordered by points DESC, name ASC."""
    totals: dict[tuple[int, str], int] = {}
    for line in lines:
        if line.season != season:
            continue
        key = (line.player_id, line.full_name)
        totals[key] = totals.get(key, 0) + line.points
    rows = [
        (pid, name, season, pts) for (pid, name), pts in totals.items()
    ]
    rows.sort(key=lambda r: (-r[3], r[1]))
    return rows


def rolling_team_points_last_n(
    lines: list[TeamGameLine],
    *,
    cutoff: datetime,
    window: int,
) -> dict[int, float]:
    """Mean points_for over up to `window` prior games with tip < cutoff, per team."""
    by_team: dict[int, list[TeamGameLine]] = {}
    for line in lines:
        if line.game_start_time >= cutoff:
            continue
        by_team.setdefault(line.team_id, []).append(line)
    out: dict[int, float] = {}
    for team_id, games in by_team.items():
        games_sorted = sorted(games, key=lambda g: g.game_start_time, reverse=True)
        selected = games_sorted[:window]
        if not selected:
            continue
        out[team_id] = sum(g.points_for for g in selected) / len(selected)
    return out
