# Implements: FR-004, ML-001, ML-002, ML-008, ADR-008
"""Feature builder — only pre-tip information; home designated team."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

FEATURE_VERSION = "team_l5_l10_v1"
MIN_PRIOR_GAMES = 5

# Stable vector key order for train/serve (ML-008 contract).
FEATURE_KEYS: tuple[str, ...] = (
    "home_wr_l5",
    "home_wr_l10",
    "home_diff_l5",
    "home_diff_l10",
    "home_pts_for_l5",
    "home_pts_for_l10",
    "home_pts_against_l5",
    "home_pts_against_l10",
    "home_season_wr",
    "away_wr_l5",
    "away_wr_l10",
    "away_diff_l5",
    "away_diff_l10",
    "away_pts_for_l5",
    "away_pts_for_l10",
    "away_pts_against_l5",
    "away_pts_against_l10",
    "away_season_wr",
)


@dataclass(frozen=True)
class TeamGameHistory:
    """One completed team game appearance before a tip."""

    team_id: int
    game_start_time: datetime
    won: bool
    points_for: int
    points_against: int
    season: int


@dataclass(frozen=True)
class FeatureRow:
    game_id: int
    feature_version: str
    label_home_win: int | None
    payload: dict[str, float]
    used_cold_start_home: bool
    used_cold_start_away: bool


def _prior_for_team(
    history: list[TeamGameHistory],
    *,
    team_id: int,
    tip: datetime,
) -> list[TeamGameHistory]:
    prior = [
        h
        for h in history
        if h.team_id == team_id and h.game_start_time < tip
    ]
    prior.sort(key=lambda h: h.game_start_time)
    return prior


def _window_stats(games: list[TeamGameHistory], n: int) -> dict[str, float]:
    window = games[-n:] if len(games) >= n else games
    if not window:
        return {
            "wr": 0.0,
            "diff": 0.0,
            "pts_for": 0.0,
            "pts_against": 0.0,
        }
    wins = sum(1 for g in window if g.won)
    return {
        "wr": wins / len(window),
        "diff": sum(g.points_for - g.points_against for g in window) / len(window),
        "pts_for": sum(g.points_for for g in window) / len(window),
        "pts_against": sum(g.points_against for g in window) / len(window),
    }


def _season_wr(games: list[TeamGameHistory], season: int) -> float:
    season_games = [g for g in games if g.season == season]
    if not season_games:
        return 0.0
    return sum(1 for g in season_games if g.won) / len(season_games)


def _team_block(
    prior: list[TeamGameHistory],
    *,
    season: int,
    prefix: str,
) -> tuple[dict[str, float], bool]:
    cold = len(prior) < MIN_PRIOR_GAMES
    if cold:
        # Season-to-date aggregates stand in for sparse L5/L10.
        season_games = [g for g in prior if g.season == season]
        stats = _window_stats(season_games, len(season_games) or 1)
        block = {
            f"{prefix}_wr_l5": stats["wr"],
            f"{prefix}_wr_l10": stats["wr"],
            f"{prefix}_diff_l5": stats["diff"],
            f"{prefix}_diff_l10": stats["diff"],
            f"{prefix}_pts_for_l5": stats["pts_for"],
            f"{prefix}_pts_for_l10": stats["pts_for"],
            f"{prefix}_pts_against_l5": stats["pts_against"],
            f"{prefix}_pts_against_l10": stats["pts_against"],
            f"{prefix}_season_wr": _season_wr(prior, season),
        }
        return block, True

    s5 = _window_stats(prior, 5)
    s10 = _window_stats(prior, 10)
    block = {
        f"{prefix}_wr_l5": s5["wr"],
        f"{prefix}_wr_l10": s10["wr"],
        f"{prefix}_diff_l5": s5["diff"],
        f"{prefix}_diff_l10": s10["diff"],
        f"{prefix}_pts_for_l5": s5["pts_for"],
        f"{prefix}_pts_for_l10": s10["pts_for"],
        f"{prefix}_pts_against_l5": s5["pts_against"],
        f"{prefix}_pts_against_l10": s10["pts_against"],
        f"{prefix}_season_wr": _season_wr(prior, season),
    }
    return block, False


def build_feature_row(
    *,
    game_id: int,
    tip: datetime,
    season: int,
    home_team_id: int,
    away_team_id: int,
    history: list[TeamGameHistory],
    label_home_win: int | None = None,
    feature_version: str = FEATURE_VERSION,
) -> FeatureRow:
    """Build features using only games with tip strictly before `tip` (ML-001)."""
    home_prior = _prior_for_team(history, team_id=home_team_id, tip=tip)
    away_prior = _prior_for_team(history, team_id=away_team_id, tip=tip)
    home_block, cold_h = _team_block(home_prior, season=season, prefix="home")
    away_block, cold_a = _team_block(away_prior, season=season, prefix="away")
    payload = {**home_block, **away_block}
    return FeatureRow(
        game_id=game_id,
        feature_version=feature_version,
        label_home_win=label_home_win,
        payload=payload,
        used_cold_start_home=cold_h,
        used_cold_start_away=cold_a,
    )


def feature_vector(payload: dict[str, float], *, version: str = FEATURE_VERSION) -> list[float]:
    """Map payload → ordered vector for a feature_version (train/serve contract)."""
    if version != FEATURE_VERSION:
        raise ValueError(f"unsupported feature_version: {version}")
    return [float(payload[k]) for k in FEATURE_KEYS]


def preprocess_for_model(
    row: FeatureRow | dict[str, Any],
    *,
    feature_version: str = FEATURE_VERSION,
) -> list[float]:
    """API/training shared preprocessing entrypoint (ML-008)."""
    if isinstance(row, FeatureRow):
        if row.feature_version != feature_version:
            raise ValueError("feature_version mismatch")
        return feature_vector(row.payload, version=feature_version)
    payload = row.get("payload") or row
    return feature_vector(dict(payload), version=feature_version)
