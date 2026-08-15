# TEST-002
"""TEST-002 — schema contract + migrations (Postgres when available)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "database" / "schema.sql"
MIGRATIONS = ROOT / "database" / "migrations"


def test_migrations_dir_finds_sql() -> None:
    from athletiq.db.migrate import migrations_dir

    names = {p.name for p in migrations_dir().glob("*.sql")}
    assert "001_initial.sql" in names
    assert "002_cr004_league_players_odds.sql" in names
    text = SCHEMA.read_text(encoding="utf-8")
    assert "BIGSERIAL" in text
    assert "game_id" in text
    assert "UUID" not in text.upper().replace("BIGSERIAL", "")  # avoid false positive
    # stronger: no uuid type
    assert " uuid" not in text.lower()
    assert "UUID" not in text


def test_schema_declares_required_indexes() -> None:
    text = SCHEMA.read_text(encoding="utf-8")
    for name in (
        "idx_games_start",
        "idx_games_season",
        "idx_team_game_stats_team_game",
        "idx_player_game_stats_player_game",
        "idx_player_game_stats_team_game",
        "idx_features_version_game",
        "idx_games_league",
        "idx_odds_snapshots_game",
    ):
        assert name in text


def test_schema_declares_dr002_tables() -> None:
    text = SCHEMA.read_text(encoding="utf-8")
    for table in (
        "schema_migrations",
        "teams",
        "players",
        "games",
        "player_game_stats",
        "team_game_stats",
        "features",
        "odds_snapshots",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in text


def test_migration_001_and_002_exist() -> None:
    assert (MIGRATIONS / "001_initial.sql").is_file()
    assert (MIGRATIONS / "002_cr004_league_players_odds.sql").is_file()


def _pg_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")


@pytest.fixture(scope="module")
def database_url() -> str:
    url = _pg_url()
    if not url:
        pytest.skip("TEST_DATABASE_URL / DATABASE_URL not set — skipping live Postgres TEST-002")
    try:
        import psycopg

        with psycopg.connect(url) as conn:
            conn.execute("SELECT 1")
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Postgres unreachable ({exc})")
    return url


def test_apply_migrations_idempotent(database_url: str) -> None:
    from athletiq.db import apply_migrations

    first = apply_migrations(database_url)
    assert "001_initial" in first
    assert "002_cr004_league_players_odds" in first

    second = apply_migrations(database_url)
    assert second == first

    import psycopg

    with psycopg.connect(database_url) as conn:
        tables = {
            r[0]
            for r in conn.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            ).fetchall()
        }
        for name in (
            "teams",
            "players",
            "games",
            "player_game_stats",
            "team_game_stats",
            "features",
            "odds_snapshots",
            "model_registry",
            "schema_migrations",
        ):
            assert name in tables

        # BIGINT identity / FK types
        cols = conn.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'games'
              AND column_name IN ('game_id', 'home_team_id', 'away_team_id')
            """
        ).fetchall()
        types = {c[0]: c[1] for c in cols}
        assert types["game_id"] == "bigint"
        assert types["home_team_id"] == "bigint"

        indexes = {
            r[0]
            for r in conn.execute(
                "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
            ).fetchall()
        }
        assert "idx_games_start" in indexes
        assert "idx_features_version_game" in indexes
