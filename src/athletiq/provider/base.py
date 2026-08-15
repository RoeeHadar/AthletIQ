# Implements: FR-001, CON-007, ADR-011, CR-004
"""Provider client interface (live NBA Stats API or fixtures behind adapter)."""

from __future__ import annotations

from typing import Any, Protocol


class ProviderClient(Protocol):
    """Minimal basketball data surface used by ingest."""

    def leagues(self) -> list[str]:
        """Leagues this provider can emit (e.g. nba, wnba)."""

    def fetch_teams(self) -> list[dict[str, Any]]:
        """Return team records (provider-shaped dicts)."""

    def fetch_games(self, season: int, league: str = "nba") -> list[dict[str, Any]]:
        """Return game records for a season label (start year) and league."""

    def fetch_players(self) -> list[dict[str, Any]]:
        """Return player records (empty if the provider has no box-score grain)."""

    def fetch_player_game_stats(self) -> list[dict[str, Any]]:
        """Return player-game box scores (empty if unavailable)."""

    def fetch_odds_snapshots(self) -> list[dict[str, Any]]:
        """Return synthetic or recorded odds snapshots (empty if none)."""
