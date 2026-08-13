# Implements: FR-009, FR-014, ADR-008, ADR-001
"""Postgres-backed GameRepo / FeatureRepo — persistence adapters only."""

from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from athletiq.features.builder import FeatureRow
from athletiq.features.postgres import PostgresFeatureStore


class PostgresGameRepo:
    """Read games for API predict — no feature engineering."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    @classmethod
    def connect(cls, database_url: str) -> PostgresGameRepo:
        return cls(psycopg.connect(database_url, row_factory=dict_row))

    def close(self) -> None:
        self._conn.close()

    def get_game(self, game_id: int) -> dict[str, Any] | None:
        row = self._conn.execute(
            """
            SELECT game_id, home_team_id, away_team_id, provider_game_id
            FROM games WHERE game_id = %s
            """,
            (game_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "game_id": int(row["game_id"]),
            "home_team_id": int(row["home_team_id"]),
            "away_team_id": int(row["away_team_id"]),
            "provider_game_id": str(row["provider_game_id"]),
        }

    def resolve_provider_game_id(self, provider_game_id: str) -> int | None:
        row = self._conn.execute(
            "SELECT game_id FROM games WHERE provider_game_id = %s",
            (provider_game_id,),
        ).fetchone()
        if row is None:
            return None
        return int(row["game_id"])


class PostgresFeatureRepo:
    """Read FeatureRow by (game_id, feature_version) for API."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn
        self._store = PostgresFeatureStore(conn)

    @classmethod
    def connect(cls, database_url: str) -> PostgresFeatureRepo:
        return cls(psycopg.connect(database_url, row_factory=dict_row))

    def close(self) -> None:
        self._conn.close()

    def get_features(self, game_id: int, feature_version: str) -> FeatureRow | None:
        return self._store.get(game_id, feature_version)
