# Implements: FR-009, FR-014, FR-020, FR-024, FR-025, ADR-008, ADR-001, ADR-016, CR-005
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
            SELECT g.game_id, g.home_team_id, g.away_team_id, g.provider_game_id, g.league,
                   g.home_score, g.away_score, g.status, g.game_start_time, g.home_win,
                   ht.name AS home_team_name, ht.abbreviation AS home_team_abbreviation,
                   at.name AS away_team_name, at.abbreviation AS away_team_abbreviation
            FROM games g
            LEFT JOIN teams ht ON ht.team_id = g.home_team_id
            LEFT JOIN teams at ON at.team_id = g.away_team_id
            WHERE g.game_id = %s
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
            "league": str(row.get("league") or "nba"),
            "home_score": row.get("home_score"),
            "away_score": row.get("away_score"),
            "status": str(row.get("status") or "unknown"),
            "game_start_time": row.get("game_start_time"),
            "home_win": row.get("home_win"),
            "home_team_name": row.get("home_team_name"),
            "home_team_abbreviation": row.get("home_team_abbreviation"),
            "away_team_name": row.get("away_team_name"),
            "away_team_abbreviation": row.get("away_team_abbreviation"),
        }

    def list_upcoming(self, *, limit: int = 20) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT g.game_id, g.league, g.game_start_time, g.status, g.home_score, g.away_score,
                   ht.name AS home_team_name, at.name AS away_team_name
            FROM games g
            LEFT JOIN teams ht ON ht.team_id = g.home_team_id
            LEFT JOIN teams at ON at.team_id = g.away_team_id
            WHERE g.status = 'scheduled'
              AND g.home_score IS NULL AND g.away_score IS NULL
              AND g.game_start_time > NOW()
            ORDER BY g.game_start_time ASC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_in_progress(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT g.game_id, g.league, g.status, g.home_score, g.away_score, g.game_start_time,
                   ht.name AS home_team_name, at.name AS away_team_name
            FROM games g
            LEFT JOIN teams ht ON ht.team_id = g.home_team_id
            LEFT JOIN teams at ON at.team_id = g.away_team_id
            WHERE g.status = 'in_progress'
            ORDER BY g.game_start_time ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]

    def latest_synthetic_odds(self, game_id: int) -> float | None:
        row = self._conn.execute(
            """
            SELECT implied_p_home_win
            FROM odds_snapshots
            WHERE game_id = %s AND source = 'synthetic'
            ORDER BY captured_at DESC
            LIMIT 1
            """,
            (game_id,),
        ).fetchone()
        if row is None:
            return None
        return float(row["implied_p_home_win"])

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
