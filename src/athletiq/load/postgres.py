# Implements: FR-002, DR-003, CON-002, ADR-001
"""PostgreSQL curated store — persistence adapter only (no feature engineering)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from athletiq.load.store import StoredGame, StoredTeam
from athletiq.validate.parse import GameRecord, TeamRecord


class PostgresCuratedStore:
    """CuratedStore backed by Postgres. Caller owns connection lifecycle / transactions."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    @classmethod
    def connect(cls, database_url: str) -> PostgresCuratedStore:
        conn = psycopg.connect(database_url, row_factory=dict_row)
        return cls(conn)

    def close(self) -> None:
        self._conn.close()

    def transaction(self):
        """Explicit transaction boundary for load-stage multi-row work."""
        return self._conn.transaction()

    def upsert_team(self, team: TeamRecord) -> int:
        row = self._conn.execute(
            """
            INSERT INTO teams (provider_team_id, name, abbreviation, conference, division)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (provider_team_id) DO UPDATE SET
                name = EXCLUDED.name,
                abbreviation = EXCLUDED.abbreviation,
                conference = EXCLUDED.conference,
                division = EXCLUDED.division,
                updated_at = NOW()
            RETURNING team_id
            """,
            (
                team.provider_team_id,
                team.name,
                team.abbreviation,
                team.conference,
                team.division,
            ),
        ).fetchone()
        assert row is not None
        return int(row["team_id"])

    def upsert_game(self, game: GameRecord, home_team_id: int, away_team_id: int) -> int:
        row = self._conn.execute(
            """
            INSERT INTO games (
                provider_game_id, season, game_start_time,
                home_team_id, away_team_id,
                home_score, away_score, home_win, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (provider_game_id) DO UPDATE SET
                season = EXCLUDED.season,
                game_start_time = EXCLUDED.game_start_time,
                home_team_id = EXCLUDED.home_team_id,
                away_team_id = EXCLUDED.away_team_id,
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                home_win = EXCLUDED.home_win,
                status = EXCLUDED.status,
                updated_at = NOW()
            RETURNING game_id
            """,
            (
                game.provider_game_id,
                game.season,
                game.game_start_time,
                home_team_id,
                away_team_id,
                game.home_score,
                game.away_score,
                game.home_win,
                game.status,
            ),
        ).fetchone()
        assert row is not None
        return int(row["game_id"])

    def upsert_team_game_stats(
        self,
        *,
        game_id: int,
        team_id: int,
        is_home: bool,
        points_for: int | None,
        points_against: int | None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO team_game_stats (game_id, team_id, is_home, points_for, points_against)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (game_id, team_id) DO UPDATE SET
                is_home = EXCLUDED.is_home,
                points_for = EXCLUDED.points_for,
                points_against = EXCLUDED.points_against,
                updated_at = NOW()
            """,
            (game_id, team_id, is_home, points_for, points_against),
        )

    def count_teams(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM teams").fetchone()
        assert row is not None
        return int(row["n"])

    def count_games(self, season: int | None = None) -> int:
        if season is None:
            row = self._conn.execute("SELECT COUNT(*) AS n FROM games").fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM games WHERE season = %s", (season,)
            ).fetchone()
        assert row is not None
        return int(row["n"])

    def count_team_game_stats(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM team_game_stats").fetchone()
        assert row is not None
        return int(row["n"])

    def iter_games(self) -> list[StoredGame]:
        rows = self._conn.execute(
            """
            SELECT game_id, provider_game_id, season, game_start_time,
                   home_team_id, away_team_id, home_score, away_score, home_win, status
            FROM games
            ORDER BY provider_game_id
            """
        ).fetchall()
        out: list[StoredGame] = []
        for r in rows:
            tip = r["game_start_time"]
            if isinstance(tip, datetime) and tip.tzinfo is None:
                tip = tip.replace(tzinfo=None)
            rec = GameRecord(
                provider_game_id=str(r["provider_game_id"]),
                season=int(r["season"]),
                game_start_time=tip,
                home_provider_team_id="",  # not required for feature build from internal ids
                away_provider_team_id="",
                home_score=r["home_score"],
                away_score=r["away_score"],
                home_win=r["home_win"],
                status=str(r["status"] or "unknown"),
            )
            out.append(
                StoredGame(
                    game_id=int(r["game_id"]),
                    record=rec,
                    home_team_id=int(r["home_team_id"]),
                    away_team_id=int(r["away_team_id"]),
                )
            )
        return out

    def team_stat(self, game_id: int, team_id: int) -> dict | None:
        row = self._conn.execute(
            """
            SELECT is_home, points_for, points_against
            FROM team_game_stats
            WHERE game_id = %s AND team_id = %s
            """,
            (game_id, team_id),
        ).fetchone()
        if row is None:
            return None
        return {
            "is_home": bool(row["is_home"]),
            "points_for": row["points_for"],
            "points_against": row["points_against"],
        }

    def get_team_by_provider(self, provider_team_id: str) -> StoredTeam | None:
        row = self._conn.execute(
            """
            SELECT team_id, provider_team_id, name, abbreviation, conference, division
            FROM teams WHERE provider_team_id = %s
            """,
            (provider_team_id,),
        ).fetchone()
        if row is None:
            return None
        return StoredTeam(
            team_id=int(row["team_id"]),
            record=TeamRecord(
                provider_team_id=str(row["provider_team_id"]),
                name=str(row["name"]),
                abbreviation=row["abbreviation"],
                conference=row["conference"],
                division=row["division"],
            ),
        )


def verify_curated_constraints(conn: psycopg.Connection) -> dict[str, Any]:
    """Assert named uniqueness constraints the app depends on exist."""
    rows = conn.execute(
        """
        SELECT c.conname, c.contype, t.relname AS table_name
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        JOIN pg_namespace n ON t.relnamespace = n.oid
        WHERE n.nspname = 'public'
          AND c.contype IN ('p', 'u')
        """
    ).fetchall()
    by_table: dict[str, list[str]] = {}
    for r in rows:
        # dict_row or tuple
        if isinstance(r, dict):
            table, name = r["table_name"], r["conname"]
        else:
            name, _ctype, table = r[0], r[1], r[2]
        by_table.setdefault(table, []).append(name)

    # UNIQUE on provider ids may be named via UNIQUE constraint or unique index.
    indexes = {
        r[0] if not isinstance(r, dict) else r["indexname"]
        for r in conn.execute(
            "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
        ).fetchall()
    }

    teams_ok = any("provider_team" in n for n in by_table.get("teams", [])) or any(
        "provider_team" in i for i in indexes
    )
    games_ok = any("provider_game" in n for n in by_table.get("games", [])) or any(
        "provider_game" in i for i in indexes
    )
    stats_ok = "team_game_stats_pkey" in by_table.get("team_game_stats", []) or any(
        "team_game_stats_pkey" == n for n in by_table.get("team_game_stats", [])
    )
    # PRIMARY KEY (game_id, team_id) typically named team_game_stats_pkey
    if not stats_ok:
        stats_ok = "team_game_stats" in by_table and any(
            "pkey" in n for n in by_table["team_game_stats"]
        )
    features_ok = any("pkey" in n for n in by_table.get("features", []))

    missing = []
    if not teams_ok:
        missing.append("teams.provider_team_id UNIQUE")
    if not games_ok:
        missing.append("games.provider_game_id UNIQUE")
    if not stats_ok:
        missing.append("team_game_stats (game_id, team_id) PK")
    if not features_ok:
        missing.append("features (game_id, feature_version) PK")
    if missing:
        raise AssertionError(f"missing required constraints: {missing}")
    return {"ok": True, "tables": sorted(by_table)}
