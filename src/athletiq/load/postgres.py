# Implements: FR-002, FR-017, FR-018, DR-003, DR-004, CON-002, ADR-001, CR-004
"""PostgreSQL curated store — persistence adapter only (no feature engineering)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from athletiq.load.store import StoredGame, StoredTeam
from athletiq.validate.parse import (
    GameRecord,
    OddsSnapshotRecord,
    PlayerGameStatRecord,
    PlayerRecord,
    TeamRecord,
)


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
            INSERT INTO teams (provider_team_id, name, abbreviation, conference, division, sport, league)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (league, provider_team_id) DO UPDATE SET
                name = EXCLUDED.name,
                abbreviation = EXCLUDED.abbreviation,
                conference = EXCLUDED.conference,
                division = EXCLUDED.division,
                sport = EXCLUDED.sport,
                updated_at = NOW()
            RETURNING team_id
            """,
            (
                team.provider_team_id,
                team.name,
                team.abbreviation,
                team.conference,
                team.division,
                team.sport,
                team.league,
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
                home_score, away_score, home_win, status, sport, league
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (league, provider_game_id) DO UPDATE SET
                season = EXCLUDED.season,
                game_start_time = EXCLUDED.game_start_time,
                home_team_id = EXCLUDED.home_team_id,
                away_team_id = EXCLUDED.away_team_id,
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                home_win = EXCLUDED.home_win,
                status = EXCLUDED.status,
                sport = EXCLUDED.sport,
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
                game.sport,
                game.league,
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
                   home_team_id, away_team_id, home_score, away_score, home_win, status,
                   sport, league
            FROM games
            ORDER BY league, provider_game_id
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
                sport=str(r.get("sport") or "basketball"),
                league=str(r.get("league") or "nba"),
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

    def upsert_player(self, player: PlayerRecord, team_id: int | None) -> int:
        row = self._conn.execute(
            """
            INSERT INTO players (provider_player_id, full_name, team_id, league)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (league, provider_player_id) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                team_id = EXCLUDED.team_id,
                updated_at = NOW()
            RETURNING player_id
            """,
            (player.provider_player_id, player.full_name, team_id, player.league),
        ).fetchone()
        assert row is not None
        return int(row["player_id"])

    def upsert_player_game_stats(
        self,
        *,
        game_id: int,
        player_id: int,
        team_id: int,
        stat: PlayerGameStatRecord,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO player_game_stats (
                game_id, player_id, team_id, minutes, points,
                rebounds, assists, steals, blocks, turnovers
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (game_id, player_id) DO UPDATE SET
                team_id = EXCLUDED.team_id,
                minutes = EXCLUDED.minutes,
                points = EXCLUDED.points,
                rebounds = EXCLUDED.rebounds,
                assists = EXCLUDED.assists,
                steals = EXCLUDED.steals,
                blocks = EXCLUDED.blocks,
                turnovers = EXCLUDED.turnovers,
                updated_at = NOW()
            """,
            (
                game_id,
                player_id,
                team_id,
                stat.minutes,
                stat.points,
                stat.rebounds,
                stat.assists,
                stat.steals,
                stat.blocks,
                stat.turnovers,
            ),
        )

    def upsert_odds_snapshot(self, game_id: int, snap: OddsSnapshotRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO odds_snapshots (
                game_id, captured_at, source, implied_p_home_win
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (game_id, source, captured_at) DO UPDATE SET
                implied_p_home_win = EXCLUDED.implied_p_home_win,
                updated_at = NOW()
            """,
            (game_id, snap.captured_at, snap.source, snap.implied_p_home_win),
        )

    def iter_player_game_stats(self) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT pgs.game_id, pgs.player_id, pgs.team_id, pgs.minutes, pgs.points,
                   g.game_start_time
            FROM player_game_stats pgs
            JOIN games g ON g.game_id = pgs.game_id
            """
        ).fetchall()
        return [
            {
                "game_id": int(r["game_id"]),
                "player_id": int(r["player_id"]),
                "team_id": int(r["team_id"]),
                "minutes": float(r["minutes"]) if r["minutes"] is not None else None,
                "points": r["points"],
                "game_start_time": r["game_start_time"],
            }
            for r in rows
        ]

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

    def get_team_by_provider(
        self, provider_team_id: str, league: str = "nba"
    ) -> StoredTeam | None:
        row = self._conn.execute(
            """
            SELECT team_id, provider_team_id, name, abbreviation, conference, division, league
            FROM teams WHERE provider_team_id = %s AND league = %s
            """,
            (provider_team_id, league),
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
                league=str(row.get("league") or league),
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

    def _unique_ok(table: str, *needles: str) -> bool:
        names = by_table.get(table, [])
        table_indexes = [i for i in indexes if i.startswith(f"{table}_") or table in i]
        hay = list(names) + table_indexes
        return any(any(n in item for n in needles) for item in hay)

    teams_ok = _unique_ok("teams", "provider_team", "league_provider")
    games_ok = _unique_ok("games", "provider_game", "league_provider")
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
