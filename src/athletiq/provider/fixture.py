# Implements: FR-001, CON-007, ADR-002
"""Recorded-payload provider for CI / local offline ingest (NFR-003)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FixtureProvider:
    """Reads `teams.json` and `games_{season}.json` from a fixtures directory."""

    def __init__(self, fixtures_dir: Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)

    def fetch_teams(self) -> list[dict[str, Any]]:
        path = self.fixtures_dir / "teams.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data["response"] if isinstance(data, dict) and "response" in data else data)

    def fetch_games(self, season: int) -> list[dict[str, Any]]:
        path = self.fixtures_dir / f"games_{season}.json"
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data["response"] if isinstance(data, dict) and "response" in data else data)
