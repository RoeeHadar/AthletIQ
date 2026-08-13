# Implements: FR-004, ADR-008
"""PostgreSQL feature store — dumb persistence of FeatureRow contract fields."""

from __future__ import annotations

import json
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from athletiq.features.builder import FeatureRow


def _to_envelope(row: FeatureRow) -> dict[str, Any]:
    """Store FeatureRow contract fields inside JSONB (schema column is `payload`)."""
    return {
        "values": dict(row.payload),
        "label_home_win": row.label_home_win,
        "used_cold_start_home": row.used_cold_start_home,
        "used_cold_start_away": row.used_cold_start_away,
    }


def _from_envelope(game_id: int, feature_version: str, raw: Any) -> FeatureRow:
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise ValueError("feature payload must be a JSON object")
    # Backward-compatible: bare feature-key maps (no envelope).
    if "values" in raw:
        values = dict(raw["values"])
        return FeatureRow(
            game_id=game_id,
            feature_version=feature_version,
            label_home_win=raw.get("label_home_win"),
            payload={k: float(v) for k, v in values.items()},
            used_cold_start_home=bool(raw.get("used_cold_start_home", False)),
            used_cold_start_away=bool(raw.get("used_cold_start_away", False)),
        )
    return FeatureRow(
        game_id=game_id,
        feature_version=feature_version,
        label_home_win=None,
        payload={k: float(v) for k, v in raw.items()},
        used_cold_start_home=False,
        used_cold_start_away=False,
    )


class PostgresFeatureStore:
    """FeatureStore keyed by (game_id, feature_version). No feature engineering."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    @classmethod
    def connect(cls, database_url: str) -> PostgresFeatureStore:
        return cls(psycopg.connect(database_url, row_factory=dict_row))

    def close(self) -> None:
        self._conn.close()

    def transaction(self):
        return self._conn.transaction()

    def upsert(self, row: FeatureRow) -> None:
        env = _to_envelope(row)
        self._conn.execute(
            """
            INSERT INTO features (game_id, feature_version, payload)
            VALUES (%s, %s, %s)
            ON CONFLICT (game_id, feature_version) DO UPDATE SET
                payload = EXCLUDED.payload,
                created_at = features.created_at
            """,
            (row.game_id, row.feature_version, Jsonb(env)),
        )

    def get(self, game_id: int, feature_version: str) -> FeatureRow | None:
        row = self._conn.execute(
            """
            SELECT game_id, feature_version, payload
            FROM features
            WHERE game_id = %s AND feature_version = %s
            """,
            (game_id, feature_version),
        ).fetchone()
        if row is None:
            return None
        return _from_envelope(int(row["game_id"]), str(row["feature_version"]), row["payload"])

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM features").fetchone()
        assert row is not None
        return int(row["n"])
