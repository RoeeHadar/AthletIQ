# Implements: FR-001, FR-016, FR-017, FR-018, FR-021, CON-007, ADR-006, CR-004, CR-005
"""Recorded-payload provider for CI / local offline ingest (NFR-003)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["response"] if isinstance(data, dict) and "response" in data else data)


class FixtureProvider:
    """Reads teams/games/players/odds JSON from a fixtures directory."""

    def __init__(self, fixtures_dir: Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)

    def leagues(self) -> list[str]:
        found = {"nba"}
        for path in self.fixtures_dir.glob("games_wnba_*.json"):
            if path.is_file():
                found.add("wnba")
                break
        return sorted(found)

    def available_seasons(self, league: str = "nba") -> list[int]:
        seasons: list[int] = []
        if league == "nba":
            for path in self.fixtures_dir.glob("games_*.json"):
                if path.name.startswith("games_wnba_"):
                    continue
                try:
                    seasons.append(int(path.stem.rsplit("_", 1)[-1]))
                except ValueError:
                    continue
        else:
            for path in self.fixtures_dir.glob(f"games_{league}_*.json"):
                try:
                    seasons.append(int(path.stem.rsplit("_", 1)[-1]))
                except ValueError:
                    continue
        return sorted(set(seasons))

    def fetch_teams(self) -> list[dict[str, Any]]:
        return _read(self.fixtures_dir / "teams.json")

    def fetch_games(self, season: int, league: str = "nba") -> list[dict[str, Any]]:
        if league == "nba":
            path = self.fixtures_dir / f"games_{season}.json"
        else:
            path = self.fixtures_dir / f"games_{league}_{season}.json"
        return _read(path)

    def fetch_players(self) -> list[dict[str, Any]]:
        return _read(self.fixtures_dir / "players.json")

    def fetch_player_game_stats(self) -> list[dict[str, Any]]:
        return _read(self.fixtures_dir / "player_game_stats.json")

    def fetch_odds_snapshots(self) -> list[dict[str, Any]]:
        return _read(self.fixtures_dir / "odds_snapshots.json")
