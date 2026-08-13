# TEST-014
"""TEST-014 — published pin/artifact identity ↔ API load (same on-disk pin)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from api.app.main import create_app
from api.app.state import AppState, InMemoryFeatureRepo, InMemoryGameRepo
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from athletiq.features import FEATURE_KEYS, FEATURE_VERSION, FeatureRow
from athletiq.ml.publish import ModelMetadata, load_pin, publish_artifacts


def _publish(artifacts: Path) -> dict:
    rng = np.random.default_rng(7)
    X = rng.normal(size=(40, len(FEATURE_KEYS)))
    y = (X[:, 0] > 0).astype(int)
    model = LogisticRegression(max_iter=200).fit(X, y)
    meta = ModelMetadata(
        model_version="test014-lr-v1",
        feature_version=FEATURE_VERSION,
        dataset_version="test-014",
        code_commit="test-014",
        training_config={"C": 1.0},
        metrics={"validation": {}, "test": {"log_loss": 0.4}},
        selection={"rule": "validation_log_loss", "used_test_for_selection": False},
        model_family="logistic_regression",
    )
    publish_artifacts(artifacts_dir=artifacts, model=model, metadata=meta)
    return load_pin(artifacts)


def _row(game_id: int, version: str, *, fill: float = 0.5) -> FeatureRow:
    payload = {k: fill for k in FEATURE_KEYS}
    return FeatureRow(
        game_id=game_id,
        feature_version=version,
        label_home_win=1,
        payload=payload,
        used_cold_start_home=False,
        used_cold_start_away=False,
    )


def _client(artifacts: Path, features: InMemoryFeatureRepo):
    state = AppState(
        artifacts_dir=artifacts,
        games=InMemoryGameRepo(
            games={
                1: {"home_team_id": 10, "away_team_id": 20},
                2: {"home_team_id": 11, "away_team_id": 21},
            },
            by_provider={},
        ),
        features=features,
        db_ping=lambda: True,
    )
    loaded = state.load_pin()
    assert loaded is not None
    return TestClient(create_app(state)), loaded


def test_pin_artifact_path_identity_and_predict_success(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    pin = _publish(artifacts)
    art_path = artifacts / pin["artifact"]
    meta_path = artifacts / pin["metadata"]
    assert art_path.is_file()
    assert meta_path.is_file()

    features = InMemoryFeatureRepo(rows={(1, FEATURE_VERSION): _row(1, FEATURE_VERSION)})
    client, loaded = _client(artifacts, features)

    # Artifact identity: loaded model is the pin-referenced file (path/name), not merely version string.
    assert loaded.artifact_name == pin["artifact"]
    assert loaded.model_version == pin["model_version"]
    assert loaded.feature_version == pin["feature_version"]

    model_res = client.get("/v1/model")
    assert model_res.status_code == 200
    model_body = model_res.json()
    assert model_body["model_version"] == pin["model_version"]
    assert model_body["feature_version"] == pin["feature_version"]
    assert model_body["dataset_version"] == "test-014"

    pred = client.get("/v1/predict", params={"game_id": "1"})
    assert pred.status_code == 200
    pred_body = pred.json()
    assert pred_body["model_version"] == pin["model_version"]
    assert pred_body["feature_version"] == pin["feature_version"]
    assert pred_body["dataset_version"] == "test-014"
    # Same on-disk pin drives both endpoints
    assert pred_body["model_version"] == model_body["model_version"]
    assert pred_body["feature_version"] == model_body["feature_version"]


def test_wrong_feature_version_not_used(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _publish(artifacts)
    # Only vN-1 for correct game_id
    features = InMemoryFeatureRepo(rows={(1, "team_l5_l10_v0"): _row(1, "team_l5_l10_v0")})
    client, _loaded = _client(artifacts, features)
    pred = client.get("/v1/predict", params={"game_id": "1"})
    assert pred.status_code == 404
    assert pred.json()["error"]["code"] == "features_not_found"


def test_correct_version_wrong_game_not_used(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    _publish(artifacts)
    # Correct feature_version only for a different game_id
    features = InMemoryFeatureRepo(rows={(2, FEATURE_VERSION): _row(2, FEATURE_VERSION)})
    client, _loaded = _client(artifacts, features)
    pred = client.get("/v1/predict", params={"game_id": "1"})
    assert pred.status_code == 404
    assert pred.json()["error"]["code"] == "features_not_found"
