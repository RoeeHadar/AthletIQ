# Implements: DR-001 — active history window (2 Must / ≤3 Should)
"""Completed-season window helpers."""

from __future__ import annotations

from datetime import date


def active_season_years(
    *,
    as_of: date | None = None,
    depth: int = 2,
) -> list[int]:
    """Return the most recent `depth` completed NBA season start years.

    NBA seasons are labeled by the year they start (e.g. 2023-24 → 2023).
    A season is treated as completed once the calendar year after tip-off
    has begun (simple MVP rule: if as_of.month >= 9, latest completed start
    year is as_of.year - 1; else as_of.year - 2).
    """
    if depth < 1:
        raise ValueError("depth must be >= 1")
    if depth > 3:
        # Should(3) is the MVP max; callers may still request 3.
        depth = 3
    as_of = as_of or date.today()
    if as_of.month >= 9:
        latest_completed = as_of.year - 1
    else:
        latest_completed = as_of.year - 2
    return [latest_completed - i for i in range(depth)]


def is_season_in_window(season: int, active: list[int]) -> bool:
    return season in active
