# Implements: DR-001, ADR-017, CR-005 — season window helpers (live NBA uncapped)
"""Completed-season window helpers."""

from __future__ import annotations

from datetime import date


def active_season_years(
    *,
    as_of: date | None = None,
    depth: int = 3,
) -> list[int]:
    """Return the most recent `depth` completed NBA season start years.

    Used by fixture/CI windows. Live `--provider nba-stats` does not clamp
    (ADR-017). `depth` has no maximum.
    """
    if depth < 1:
        raise ValueError("depth must be >= 1")
    as_of = as_of or date.today()
    if as_of.month >= 9:
        latest_completed = as_of.year - 1
    else:
        latest_completed = as_of.year - 2
    return [latest_completed - i for i in range(depth)]


def is_season_in_window(season: int, active: list[int]) -> bool:
    return season in active
