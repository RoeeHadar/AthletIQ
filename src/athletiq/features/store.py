# Implements: FR-004, ADR-008
"""Feature persistence keyed by (game_id, feature_version)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from athletiq.features.builder import FeatureRow


class FeatureStore(Protocol):
    def upsert(self, row: FeatureRow) -> None: ...

    def get(self, game_id: int, feature_version: str) -> FeatureRow | None: ...

    def count(self) -> int: ...


@dataclass
class InMemoryFeatureStore:
    _rows: dict[tuple[int, str], FeatureRow] = field(default_factory=dict)

    def upsert(self, row: FeatureRow) -> None:
        self._rows[(row.game_id, row.feature_version)] = row

    def get(self, game_id: int, feature_version: str) -> FeatureRow | None:
        return self._rows.get((game_id, feature_version))

    def count(self) -> int:
        return len(self._rows)

    def iter_rows(self) -> list[FeatureRow]:
        return list(self._rows.values())
