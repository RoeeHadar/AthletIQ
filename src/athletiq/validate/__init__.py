# Implements: FR-013, OPS-002
"""ETL validation report (FR-013)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ValidationReport:
    """Counts and skip reasons for a load run."""

    teams_seen: int = 0
    teams_loaded: int = 0
    teams_skipped: int = 0
    games_seen: int = 0
    games_loaded: int = 0
    games_skipped: int = 0
    team_stats_upserted: int = 0
    players_loaded: int = 0
    player_stats_upserted: int = 0
    odds_loaded: int = 0
    skip_reasons: list[str] = field(default_factory=list)
    required_seasons: list[int] = field(default_factory=list)
    batch_id: str | None = None

    def add_skip(self, reason: str) -> None:
        self.skip_reasons.append(reason)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
