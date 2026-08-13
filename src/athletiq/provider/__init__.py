# Implements: FR-001, CON-007, ADR-002
"""Provider adapter boundary."""

from __future__ import annotations

from athletiq.provider.base import ProviderClient
from athletiq.provider.fixture import FixtureProvider
from athletiq.provider.seasons import active_season_years, is_season_in_window

__all__ = [
    "ProviderClient",
    "FixtureProvider",
    "active_season_years",
    "is_season_in_window",
]
