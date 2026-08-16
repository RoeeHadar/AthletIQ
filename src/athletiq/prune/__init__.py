# Implements: DR-001, ADR-006, ADR-017 — fixture-window helper only (live NBA is not age-pruned)
"""Prune curated games/stats outside the active season window."""

from __future__ import annotations

from athletiq.provider.seasons import active_season_years


def seasons_to_prune(present: set[int], *, depth: int = 3) -> list[int]:
    """Return season years present in curated data but outside the active window."""
    active = set(active_season_years(depth=depth))
    return sorted(present - active)
