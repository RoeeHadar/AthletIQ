# Postgres store integration (TEST_DATABASE_URL)
"""Postgres curated + feature store integration (TEST_DATABASE_URL only)."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from athletiq.db.migrate import apply_migrations
from athletiq.features.builder import FEATURE_VERSION, FeatureRow
from athletiq.features.postgres import PostgresFeatureStore
from athletiq.load.postgres import PostgresCuratedStore, verify_curated_constraints
from athletiq.validate.parse import GameRecord, TeamRecord

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL required (test-only DB; never use default DATABASE_URL for wipe/migrate tests)",
)


@pytest.fixture
def test_db_url() -> str:
    url = os.environ["TEST_DATABASE_URL"]
    default = os.environ.get("DATABASE_URL")
    if default and url == default and "test" not in url.lower():
        pytest.skip(
            "Refusing destructive Postgres tests when TEST_DATABASE_URL == DATABASE_URL "
            "without 'test' in the URL"
        )
    apply_migrations(url)
    return url


def test_named_constraints_exist(test_db_url: str) -> None:
    store = PostgresCuratedStore.connect(test_db_url)
    try:
        verify_curated_constraints(store._conn)
    finally:
        store.close()


def test_curated_upsert_idempotent_and_update(test_db_url: str) -> None:
    store = PostgresCuratedStore.connect(test_db_url)
    try:
        with store.transaction():
            home = store.upsert_team(
                TeamRecord(provider_team_id="t-home-i", name="Home", abbreviation="HOM")
            )
            away = store.upsert_team(
                TeamRecord(provider_team_id="t-away-i", name="Away", abbreviation="AWY")
            )
            gid = store.upsert_game(
                GameRecord(
                    provider_game_id="g-idem-2",
                    season=2023,
                    game_start_time=datetime(2023, 10, 1, tzinfo=timezone.utc),
                    home_provider_team_id="t-home-i",
                    away_provider_team_id="t-away-i",
                    home_score=100,
                    away_score=90,
                    home_win=True,
                    status="Finished",
                ),
                home_team_id=home,
                away_team_id=away,
            )
            store.upsert_team_game_stats(
                game_id=gid,
                team_id=home,
                is_home=True,
                points_for=100,
                points_against=90,
            )
            n_teams = store.count_teams()
            n_games = store.count_games()
            n_stats = store.count_team_game_stats()

            home2 = store.upsert_team(
                TeamRecord(provider_team_id="t-home-i", name="Home", abbreviation="HOM")
            )
            assert home2 == home
            gid2 = store.upsert_game(
                GameRecord(
                    provider_game_id="g-idem-2",
                    season=2023,
                    game_start_time=datetime(2023, 10, 1, tzinfo=timezone.utc),
                    home_provider_team_id="t-home-i",
                    away_provider_team_id="t-away-i",
                    home_score=100,
                    away_score=90,
                    home_win=True,
                    status="Finished",
                ),
                home_team_id=home,
                away_team_id=away,
            )
            assert gid2 == gid
            assert store.count_teams() == n_teams
            assert store.count_games() == n_games
            assert store.count_team_game_stats() == n_stats

            store.upsert_game(
                GameRecord(
                    provider_game_id="g-idem-2",
                    season=2023,
                    game_start_time=datetime(2023, 10, 1, tzinfo=timezone.utc),
                    home_provider_team_id="t-home-i",
                    away_provider_team_id="t-away-i",
                    home_score=110,
                    away_score=95,
                    home_win=True,
                    status="Final",
                ),
                home_team_id=home,
                away_team_id=away,
            )
            assert store.count_games() == n_games
            games = {g.record.provider_game_id: g for g in store.iter_games()}
            assert games["g-idem-2"].record.home_score == 110
            assert games["g-idem-2"].record.status == "Final"
    finally:
        store.close()


def test_load_transaction_rollback(test_db_url: str) -> None:
    probe = PostgresCuratedStore.connect(test_db_url)
    before = probe.count_teams()
    probe.close()

    store = PostgresCuratedStore.connect(test_db_url)
    try:
        with store.transaction():
            store.upsert_team(
                TeamRecord(provider_team_id="t-rollback", name="Rollback", abbreviation="RB")
            )
            store._conn.execute(
                "INSERT INTO teams (provider_team_id, name) VALUES (%s, %s)",
                ("t-rollback-bad", None),
            )
        pytest.fail("expected transaction to fail")
    except Exception:
        pass
    finally:
        store.close()

    store2 = PostgresCuratedStore.connect(test_db_url)
    try:
        assert store2.count_teams() == before
        assert store2.get_team_by_provider("t-rollback") is None
    finally:
        store2.close()


def test_feature_store_round_trip_feature_row_contract(test_db_url: str) -> None:
    curated = PostgresCuratedStore.connect(test_db_url)
    try:
        with curated.transaction():
            home = curated.upsert_team(
                TeamRecord(provider_team_id="t-feat-h", name="H", abbreviation="H")
            )
            away = curated.upsert_team(
                TeamRecord(provider_team_id="t-feat-a", name="A", abbreviation="A")
            )
            gid = curated.upsert_game(
                GameRecord(
                    provider_game_id="g-feat",
                    season=2024,
                    game_start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
                    home_provider_team_id="t-feat-h",
                    away_provider_team_id="t-feat-a",
                    home_score=1,
                    away_score=0,
                    home_win=True,
                    status="Finished",
                ),
                home_team_id=home,
                away_team_id=away,
            )
    finally:
        curated.close()

    store = PostgresFeatureStore.connect(test_db_url)
    try:
        row = FeatureRow(
            game_id=gid,
            feature_version=FEATURE_VERSION,
            label_home_win=1,
            payload={"home_wr_l5": 0.6, "away_wr_l5": 0.4},
            used_cold_start_home=True,
            used_cold_start_away=False,
        )
        with store.transaction():
            store.upsert(row)
            store.upsert(row)
            assert store.count() >= 1
            got = store.get(gid, FEATURE_VERSION)
        assert got is not None
        assert got.game_id == row.game_id
        assert got.feature_version == row.feature_version
        assert got.label_home_win == row.label_home_win
        assert got.payload == row.payload
        assert got.used_cold_start_home == row.used_cold_start_home
        assert got.used_cold_start_away == row.used_cold_start_away
    finally:
        store.close()
