# TEST-008, TEST-014
"""TEST-008 / TEST-014 — API contract, errors, pin↔artifact consistency."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from api.app.main import create_app
from api.app.state import AppState, InMemoryFeatureRepo, InMemoryGameRepo
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from athletiq.features import FEATURE_KEYS, FEATURE_VERSION, FeatureRow
from athletiq.ml.publish import ModelMetadata, publish_artifacts

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "api" / "openapi.yaml"


def _train_tiny_model(artifacts: Path) -> None:
    # Vector matching FEATURE_KEYS
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, len(FEATURE_KEYS)))
    y = (X[:, 0] > 0).astype(int)
    model = LogisticRegression(max_iter=200).fit(X, y)
    meta = ModelMetadata(
        model_version="demo-lr-v1",
        feature_version=FEATURE_VERSION,
        dataset_version="api-test",
        code_commit="test",
        training_config={"C": 1.0},
        metrics={"validation": {}, "test": {}},
        selection={"rule": "test", "used_test_for_selection": False},
        model_family="logistic_regression",
    )
    publish_artifacts(artifacts_dir=artifacts, model=model, metadata=meta)


def _feature_row(game_id: int, version: str = FEATURE_VERSION) -> FeatureRow:
    payload = {k: 0.0 for k in FEATURE_KEYS}
    payload["home_wr_l5"] = 0.7
    payload["away_wr_l5"] = 0.4
    return FeatureRow(
        game_id=game_id,
        feature_version=version,
        label_home_win=1,
        payload=payload,
        used_cold_start_home=False,
        used_cold_start_away=False,
    )


def _client(tmp_path: Path, *, with_model: bool = True, with_db: bool = True) -> TestClient:
    artifacts = tmp_path / "artifacts"
    if with_model:
        _train_tiny_model(artifacts)
    games = InMemoryGameRepo(
        games={1: {"home_team_id": 10, "away_team_id": 20}},
        by_provider={"prov-1": 1},
    )
    features = InMemoryFeatureRepo(rows={(1, FEATURE_VERSION): _feature_row(1)})
    state = AppState(
        artifacts_dir=artifacts if with_model else tmp_path / "missing",
        games=games if with_db else None,
        features=features if with_db else None,
        db_ping=(lambda: True) if with_db else (lambda: False),
    )
    if with_model:
        state.load_pin()
    app = create_app(state)
    return TestClient(app)


def test_openapi_cites_no_hard_slo() -> None:
    text = OPENAPI.read_text(encoding="utf-8")
    assert "No hard latency SLO" in text or "NFR-004" in text
    assert "No application auth" in text or "ADR-009" in text


def test_health_ok_and_model_unavailable(tmp_path: Path) -> None:
    client = _client(tmp_path, with_model=True)
    assert client.get("/v1/health").status_code == 200

    bad = _client(tmp_path / "b", with_model=False, with_db=True)
    # force missing artifacts
    r = bad.get("/v1/health")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "model_unavailable"


def test_health_db_unavailable(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _train_tiny_model(artifacts)
    state = AppState(
        artifacts_dir=artifacts,
        games=InMemoryGameRepo(),
        features=InMemoryFeatureRepo(),
        db_ping=lambda: False,
    )
    state.load_pin()
    client = TestClient(create_app(state))
    r = client.get("/v1/health")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "db_unavailable"


def test_predict_success_lineage_matches_pin(tmp_path: Path) -> None:
    client = _client(tmp_path)
    r = client.get("/v1/predict", params={"game_id": "1"})
    assert r.status_code == 200
    body = r.json()
    assert body["model_version"] == "demo-lr-v1"
    assert body["feature_version"] == FEATURE_VERSION
    assert "p_home_win" in body
    assert body["home_win_pred"] == (body["p_home_win"] >= 0.5)
    assert body["home_team_name"] is None
    assert body["home_team_abbreviation"] is None
    assert body["away_team_name"] is None
    assert body["away_team_abbreviation"] is None

    model = client.get("/v1/model").json()
    assert model["model_version"] == body["model_version"]
    assert model["feature_version"] == body["feature_version"]


def test_predict_game_not_found_and_features_not_found(tmp_path: Path) -> None:
    client = _client(tmp_path)
    r = client.get("/v1/predict", params={"game_id": "999"})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "game_not_found"

    # game exists, wrong feature version pin simulation
    artifacts = tmp_path / "art2"
    _train_tiny_model(artifacts)
    games = InMemoryGameRepo(games={2: {"home_team_id": 1, "away_team_id": 2}})
    features = InMemoryFeatureRepo(rows={(2, "other_version"): _feature_row(2, "other_version")})
    state = AppState(artifacts_dir=artifacts, games=games, features=features, db_ping=lambda: True)
    state.load_pin()
    client2 = TestClient(create_app(state))
    r2 = client2.get("/v1/predict", params={"game_id": "2"})
    assert r2.status_code == 404
    assert r2.json()["error"]["code"] == "features_not_found"
    assert r2.json()["error"]["details"]["feature_version"] == FEATURE_VERSION


def test_predict_includes_team_identity_from_game_row(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _train_tiny_model(artifacts)
    games = InMemoryGameRepo(
        games={
            1: {
                "home_team_id": 10,
                "away_team_id": 20,
                "home_team_name": "Boston Celtics",
                "home_team_abbreviation": "BOS",
                "away_team_name": "Los Angeles Lakers",
                "away_team_abbreviation": "LAL",
                "league": "nba",
            }
        }
    )
    features = InMemoryFeatureRepo(rows={(1, FEATURE_VERSION): _feature_row(1)})
    state = AppState(
        artifacts_dir=artifacts,
        games=games,
        features=features,
        db_ping=lambda: True,
    )
    state.load_pin()
    body = TestClient(create_app(state)).get("/v1/predict", params={"game_id": "1"}).json()
    assert body["home_team_name"] == "Boston Celtics"
    assert body["home_team_abbreviation"] == "BOS"
    assert body["away_team_name"] == "Los Angeles Lakers"
    assert body["away_team_abbreviation"] == "LAL"


def test_predict_invalid_and_model_unavailable(tmp_path: Path) -> None:
    client = _client(tmp_path)
    r = client.get("/v1/predict")
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "invalid_request"

    bad = _client(tmp_path / "x", with_model=False)
    r2 = bad.get("/v1/predict", params={"game_id": "1"})
    assert r2.status_code == 503
    assert r2.json()["error"]["code"] == "model_unavailable"


def test_no_auth_dependency_on_app(tmp_path: Path) -> None:
    app = create_app(AppState())
    # No HTTPBearer / OAuth middleware registered
    assert app.user_middleware == [] or all(
        "Authentication" not in str(m) for m in app.user_middleware
    )
    # Routes callable without Authorization header
    client = _client(tmp_path)
    assert client.get("/v1/model").status_code == 200
    assert "Authorization" not in client.get("/v1/model").request.headers


def test_demo_ui_index_is_html(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.get("/")
    assert res.status_code == 200
    assert res.headers.get("cache-control") == "no-store"
    assert "text/html" in res.headers.get("content-type", "")
    assert "AthletIQ" in res.text
    assert "Game ID" in res.text
    assert "TAKE" in res.text
    assert "/v1/predict" in res.text
    css = client.get("/static/app.css")
    assert css.status_code == 200

