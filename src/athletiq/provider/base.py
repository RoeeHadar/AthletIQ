# Implements: FR-001, CON-007, ADR-011
"""Provider client interface (live NBA Stats API or fixtures behind adapter)."""

from __future__ import annotations

from typing import Any, Protocol


class ProviderClient(Protocol):
    """Minimal NBA data surface used by ingest."""

    def fetch_teams(self) -> list[dict[str, Any]]:
        """Return team records (provider-shaped dicts)."""

    def fetch_games(self, season: int) -> list[dict[str, Any]]:
        """Return game records for a season label (start year)."""
