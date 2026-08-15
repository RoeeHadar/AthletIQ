# TEST-015 … TEST-019 (CR-004)
"""League fixtures, player load, synthetic odds, pin routing, Comp A UI."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from api.app.main import create_app
from api.app.state import AppState, InMemoryFeatureRepo, InMemoryGameRepo
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from athletiq.features import FEATURE_KEYS, FEATURE_VERSION, FeatureRow
from athletiq.ingest import ingest_raw
from athletiq.load import load_raw_batch
from athletiq.ml.publish import ModelMetadata, publish_artifacts
from athletiq.provider.fixture import FixtureProvider
from athletiq.provider.seasons import active_season_years

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "provider"
STATIC = ROOT / "api" / "static"


def test_season_depth_three_includes_2022() -> None:
    seasons = active_season_years(as_of=__import__("datetime").date(2026, 3, 1), depth=3)
    assert seasons == [2024, 2023, 2022]


def test_fixture_has_wnba_players_and_odds() -> None:
    assert (FIXTURES / "games_2022.json").is_file()
    assert (FIXTURES / "games_wnba_2023.json").is_file()
    assert (FIXTURES / "players.json").is_file()
    assert (FIXTURES / "odds_snapshots.json").is_file()
    teams = json.loads((FIXTURES / "teams.json").read_text(encoding="utf-8"))
    leagues = {t.get("league", "nba") for t in teams["response"]}
    assert leagues == {"nba", "wnba"}


def test_ingest_and_load_wnba_players_odds(tmp_path: Path) -> None:
    batch = ingest_raw(
        FixtureProvider(FIXTURES),
        tmp_path / "raw",
        seasons=[2023, 2024],
        batch_id="cr004",
    )
    assert (batch / "games_wnba_2023.json").is_file()
    assert (batch / "players.json").is_file()
    store, report = load_raw_batch(batch, required_seasons=[2023, 2024])
    leagues = {g.record.league for g in store.iter_games()}
    assert "nba" in leagues and "wnba" in leagues
    assert report.players_loaded >= 10
    assert report.player_stats_upserted >= 1
    assert report.odds_loaded >= 1
    n_player_stats = len(store.iter_player_game_stats())
    load_raw_batch(batch, store, required_seasons=[2023, 2024])
    assert len(store.iter_player_game_stats()) == n_player_stats


def test_synthetic_odds_on_predict(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, len(FEATURE_KEYS)))
    y = (X[:, 0] > 0).astype(int)
    model = LogisticRegression(max_iter=200).fit(X, y)
    publish_artifacts(
        artifacts_dir=artifacts,
        model=model,
        metadata=ModelMetadata(
            model_version="odds-lr-v1",
            feature_version=FEATURE_VERSION,
            dataset_version="t017",
            code_commit="t",
            training_config={},
            metrics={},
            selection={"rule": "t", "used_test_for_selection": False},
            model_family="logistic_regression",
        ),
    )
    games = InMemoryGameRepo(
        games={1: {"home_team_id": 1, "away_team_id": 2, "league": "nba"}},
        odds={1: 0.55},
    )
    features = InMemoryFeatureRepo(
        rows={
            (1, FEATURE_VERSION): FeatureRow(
                game_id=1,
                feature_version=FEATURE_VERSION,
                label_home_win=1,
                payload={k: 0.0 for k in FEATURE_KEYS},
                used_cold_start_home=False,
                used_cold_start_away=False,
            )
        }
    )
    state = AppState(
        artifacts_dir=artifacts,
        games=games,
        features=features,
        db_ping=lambda: True,
    )
    state.load_pin()
    client = TestClient(create_app(state))
    body = client.get("/v1/predict", params={"game_id": "1"}).json()
    assert body["market_p_home_win"] == 0.55
    assert body["market_source"] == "synthetic"
    assert body["league"] == "nba"

    games.odds.clear()
    body2 = client.get("/v1/predict", params={"game_id": "1"}).json()
    assert body2["market_p_home_win"] is None


def test_per_league_pin_routing(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    rng = np.random.default_rng(1)
    X = rng.normal(size=(40, len(FEATURE_KEYS)))
    y = (X[:, 0] > 0).astype(int)
    nba = LogisticRegression(max_iter=200).fit(X, y)
    wnba = LogisticRegression(max_iter=200).fit(X, 1 - y)
    for version, model in (("nba-lr-v1", nba), ("wnba-lr-v1", wnba)):
        publish_artifacts(
            artifacts_dir=artifacts,
            model=model,
            metadata=ModelMetadata(
                model_version=version,
                feature_version=FEATURE_VERSION,
                dataset_version="t018",
                code_commit="t",
                training_config={},
                metrics={},
                selection={"rule": "t", "used_test_for_selection": False},
                model_family="logistic_regression",
            ),
            pin_name=f"{version}.pin.json",
        )
    pin = {
        "schema": "athletiq.pins.v2",
        "default_league": "nba",
        "pins": {
            "nba": {
                "model_version": "nba-lr-v1",
                "feature_version": FEATURE_VERSION,
                "artifact": "nba-lr-v1.joblib",
                "metadata": "nba-lr-v1.json",
            },
            "wnba": {
                "model_version": "wnba-lr-v1",
                "feature_version": FEATURE_VERSION,
                "artifact": "wnba-lr-v1.joblib",
                "metadata": "wnba-lr-v1.json",
            },
        },
    }
    (artifacts / "selected_pin.json").write_text(json.dumps(pin), encoding="utf-8")
    row = FeatureRow(
        game_id=1,
        feature_version=FEATURE_VERSION,
        label_home_win=1,
        payload={k: 0.0 for k in FEATURE_KEYS},
        used_cold_start_home=False,
        used_cold_start_away=False,
    )
    features = InMemoryFeatureRepo(
        rows={(1, FEATURE_VERSION): row, (2, FEATURE_VERSION): row}
    )
    games = InMemoryGameRepo(
        games={
            1: {"home_team_id": 1, "away_team_id": 2, "league": "nba"},
            2: {"home_team_id": 3, "away_team_id": 4, "league": "wnba"},
        }
    )
    state = AppState(
        artifacts_dir=artifacts,
        games=games,
        features=features,
        db_ping=lambda: True,
    )
    state.load_pin()
    client = TestClient(create_app(state))
    nba_body = client.get("/v1/predict", params={"game_id": "1"}).json()
    wnba_body = client.get("/v1/predict", params={"game_id": "2"}).json()
    assert nba_body["model_version"] == "nba-lr-v1"
    assert wnba_body["model_version"] == "wnba-lr-v1"
    assert client.get("/v1/model", params={"league": "wnba"}).json()["model_version"] == "wnba-lr-v1"

    del state._models["wnba"]
    r = client.get("/v1/predict", params={"game_id": "2"})
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "model_unavailable"


def test_comp_a_ui_has_league_and_market_p_not_a_book() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "Game ID" in html
    assert "AthletIQ" in html
    assert 'id="league"' in html
    assert 'id="split"' in html
    assert "TAKE" in html
    assert "home_team_name" in js
    assert "home_team_abbreviation" in js
    assert "Market P" in js or "market_p_home_win" in js
    assert "synthetic" in js.lower()
    lowered = (html + js).lower()
    assert "stake" not in lowered
    assert "payout" not in lowered
    assert "wager" not in lowered
    assert "moneyline" not in lowered

    client = TestClient(create_app(AppState()))
    page = client.get("/")
    assert page.status_code == 200
    assert "text/html" in page.headers.get("content-type", "")
    assert "Game ID" in page.text
    assert 'id="league"' in page.text
    assert 'id="split"' in page.text
