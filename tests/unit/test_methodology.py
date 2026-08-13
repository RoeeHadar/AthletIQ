# TEST-012
"""TEST-012 — model card methodology + /v1/model disclosure alignment."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from api.app.main import create_app
from api.app.methodology import METHODOLOGY, MODEL_CARD_REF
from api.app.state import AppState, InMemoryFeatureRepo, InMemoryGameRepo
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from athletiq.features import FEATURE_KEYS, FEATURE_VERSION, FeatureRow
from athletiq.ml.publish import ModelMetadata, publish_artifacts

ROOT = Path(__file__).resolve().parents[2]
MODEL_CARD = ROOT / "docs" / "06-design" / "model-card.md"


def _client(tmp_path: Path) -> TestClient:
    artifacts = tmp_path / "artifacts"
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, len(FEATURE_KEYS)))
    y = (X[:, 0] > 0).astype(int)
    model = LogisticRegression(max_iter=200).fit(X, y)
    meta = ModelMetadata(
        model_version="card-lr-v1",
        feature_version=FEATURE_VERSION,
        dataset_version="test-012",
        code_commit="test",
        training_config={},
        metrics={"validation": {"selected": "logistic_regression"}, "test": {"log_loss": 0.5}},
        selection={"rule": "validation_log_loss", "used_test_for_selection": False},
        model_family="logistic_regression",
    )
    publish_artifacts(artifacts_dir=artifacts, model=model, metadata=meta)
    state = AppState(
        artifacts_dir=artifacts,
        games=InMemoryGameRepo(games={1: {"home_team_id": 1, "away_team_id": 2}}),
        features=InMemoryFeatureRepo(
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
        ),
        db_ping=lambda: True,
    )
    state.load_pin()
    return TestClient(create_app(state))


def test_model_card_documents_methodology_and_limitations() -> None:
    assert MODEL_CARD.is_file()
    text = MODEL_CARD.read_text(encoding="utf-8").lower()
    assert "baselines" in text and "never served" in text
    assert "temporal" in text and "70" in text
    assert "log loss" in text or "log_loss" in text
    assert "validation" in text
    assert "limitation" in text
    assert "accurately predict" in text
    assert "never served" in text


def test_v1_model_aligns_with_fr010_and_card(tmp_path: Path) -> None:
    client = _client(tmp_path)
    res = client.get("/v1/model")
    assert res.status_code == 200
    body = res.json()
    assert body["model_card_ref"] == MODEL_CARD_REF
    assert body["baselines_served"] is False
    assert METHODOLOGY["baselines"]["served"] is False
    assert body["methodology"]["primary_metric"] == "log_loss"
    assert body["methodology"]["split"]["shuffle"] is False
    assert body["methodology"]["selection"]["partition"] == "validation"
    assert body["methodology"]["selection"]["test_used_for_selection"] is False
    lim = body["limitations"].lower()
    assert "baselines are never served" in lim
    assert "log loss" in lim or "log_loss" in lim
    assert "does not claim" in lim or "accurately predict" in lim

    pred = client.get("/v1/predict", params={"game_id": "1"})
    assert pred.status_code == 200
    assert pred.json()["limitations_ref"] == "/v1/model"
