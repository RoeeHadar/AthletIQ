# TEST-006
"""TEST-006 — leakage, home orientation, cold start, train/serve contract."""

from __future__ import annotations

from datetime import datetime, timezone

from athletiq.features import (
    FEATURE_VERSION,
    MIN_PRIOR_GAMES,
    InMemoryFeatureStore,
    PlayerGameHistory,
    TeamGameHistory,
    build_feature_row,
    preprocess_for_model,
)


def _tip(day: int) -> datetime:
    return datetime(2024, 1, day, 12, 0, tzinfo=timezone.utc)


def _hist(team_id: int, day: int, *, won: bool, pf: int, pa: int) -> TeamGameHistory:
    return TeamGameHistory(
        team_id=team_id,
        game_start_time=_tip(day),
        won=won,
        points_for=pf,
        points_against=pa,
        season=2023,
    )


def test_no_leakage_from_future_games() -> None:
    tip = _tip(10)
    history = [
        _hist(1, 1, won=True, pf=100, pa=90),
        _hist(1, 15, won=True, pf=200, pa=50),  # after tip — must not enter
    ]
    row = build_feature_row(
        game_id=99,
        tip=tip,
        season=2023,
        home_team_id=1,
        away_team_id=2,
        history=history,
        label_home_win=1,
    )
    # Only day-1 game → cold start path; pts_for should reflect 100 not 200
    assert row.payload["home_pts_for_l5"] == 100.0
    assert row.label_home_win == 1  # ML-002 home orientation


def test_cold_start_when_fewer_than_min_prior() -> None:
    tip = _tip(20)
    history = [_hist(1, d, won=True, pf=100, pa=90) for d in range(1, 1 + (MIN_PRIOR_GAMES - 1))]
    row = build_feature_row(
        game_id=1,
        tip=tip,
        season=2023,
        home_team_id=1,
        away_team_id=2,
        history=history,
    )
    assert row.used_cold_start_home is True
    assert len(history) < MIN_PRIOR_GAMES


def test_l5_when_enough_history() -> None:
    tip = _tip(30)
    history = [
        _hist(1, d, won=(d % 2 == 0), pf=90 + d, pa=100)
        for d in range(1, 12)
    ]
    row = build_feature_row(
        game_id=2,
        tip=tip,
        season=2023,
        home_team_id=1,
        away_team_id=2,
        history=history,
    )
    assert row.used_cold_start_home is False
    # L5 = days 7..11 (last 5 before tip 30)
    last5 = history[-5:]
    expected_wr = sum(1 for g in last5 if g.won) / 5
    assert abs(row.payload["home_wr_l5"] - expected_wr) < 1e-9


def test_train_serve_preprocess_contract() -> None:
    tip = _tip(10)
    history = [_hist(1, 1, won=True, pf=110, pa=100), _hist(2, 2, won=False, pf=95, pa=100)]
    row = build_feature_row(
        game_id=7,
        tip=tip,
        season=2023,
        home_team_id=1,
        away_team_id=2,
        history=history,
        label_home_win=0,
    )
    v_train = preprocess_for_model(row, feature_version=FEATURE_VERSION)
    v_api = preprocess_for_model(
        {"payload": row.payload},
        feature_version=FEATURE_VERSION,
    )
    assert v_train == v_api
    assert len(v_train) == 22


def test_feature_store_unique_key() -> None:
    store = InMemoryFeatureStore()
    tip = _tip(10)
    row = build_feature_row(
        game_id=5,
        tip=tip,
        season=2023,
        home_team_id=1,
        away_team_id=2,
        history=[],
    )
    store.upsert(row)
    store.upsert(row)  # idempotent same key
    assert store.count() == 1
    assert store.get(5, FEATURE_VERSION) is not None


def test_player_aggregates_ignore_post_tip_lines() -> None:
    tip = _tip(10)
    history = [_hist(1, 1, won=True, pf=100, pa=90)]
    players = [
        PlayerGameHistory(
            player_id=7,
            team_id=1,
            game_start_time=_tip(1),
            minutes=30.0,
            points=12.0,
        ),
        PlayerGameHistory(
            player_id=7,
            team_id=1,
            game_start_time=_tip(15),
            minutes=40.0,
            points=40.0,
        ),
    ]
    row = build_feature_row(
        game_id=50,
        tip=tip,
        season=2023,
        home_team_id=1,
        away_team_id=2,
        history=history,
        player_history=players,
    )
    assert row.payload["home_top5_l5_pts"] == 12.0
    assert row.payload["home_top5_l5_min"] == 30.0
    assert row.payload["away_top5_l5_pts"] == 0.0
