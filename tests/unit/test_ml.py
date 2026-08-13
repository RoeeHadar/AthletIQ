# TEST-007
"""TEST-007 — ML lifecycle automated correctness (+ ML-005 smoke on synthetic)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from athletiq.ml.baselines import domain_informed_predict, naive_home_predict
from athletiq.ml.metrics import beats_baseline
from athletiq.ml.pipeline import run_train_select_publish
from athletiq.ml.publish import load_pin
from athletiq.ml.select import select_model
from athletiq.ml.splits import temporal_split
from athletiq.ml.train import FittedCandidate


def test_temporal_split_fractions_and_order() -> None:
    split = temporal_split(100)
    assert split.train[0] == 0
    assert split.train[-1] < split.validation[0]
    assert split.validation[-1] < split.test[0]
    assert split.test[-1] == 99
    assert abs(len(split.train) / 100 - 0.70) <= 0.02
    assert abs(len(split.validation) / 100 - 0.15) <= 0.02
    assert abs(len(split.test) / 100 - 0.15) <= 0.02


def test_baselines_naive_and_domain_informed() -> None:
    assert list(naive_home_predict(3)) == [1.0, 1.0, 1.0]
    home = np.array([0.6, 0.4, 0.5])
    away = np.array([0.5, 0.5, 0.5])
    # tie on last → home
    assert list(domain_informed_predict(home, away)) == [1.0, 0.0, 1.0]


def test_selection_tie_prefers_logistic_regression() -> None:
    lr = FittedCandidate("logistic_regression", model=object(), training_config={})
    xgb = FittedCandidate("xgboost", model=object(), training_config={})
    scores = {
        "logistic_regression": {"log_loss": 0.5, "accuracy": 0.5},
        "xgboost": {"log_loss": 0.5, "accuracy": 0.6},
    }
    result = select_model([xgb, lr], scores)
    assert result.selected.name == "logistic_regression"


def test_ml005_comparison_machinery() -> None:
    assert beats_baseline(0.4, 0.5) is True
    assert beats_baseline(0.5, 0.4) is False


def _synthetic_dataset(n: int = 120, seed: int = 0):
    """Linearly separable-ish home-win signal in feature 0."""
    rng = np.random.default_rng(seed)
    home_wr = rng.uniform(0.2, 0.8, size=n)
    away_wr = rng.uniform(0.2, 0.8, size=n)
    # Label mostly follows home_wr - away_wr
    logits = 3.0 * (home_wr - away_wr)
    probs = 1 / (1 + np.exp(-logits))
    y = (rng.random(n) < probs).astype(float)
    X = np.column_stack(
        [
            home_wr - away_wr,
            home_wr,
            away_wr,
            rng.normal(size=n),
        ]
    )
    return X, y, home_wr, away_wr


def test_train_select_publish_and_test_isolation(tmp_path: Path) -> None:
    X, y, home_wr, away_wr = _synthetic_dataset()
    result = run_train_select_publish(
        X=X,
        y=y,
        home_season_wr=home_wr,
        away_season_wr=away_wr,
        artifacts_dir=tmp_path / "artifacts",
        dataset_version="synthetic-v1",
        code_commit="test",
        seed=42,
        model_version="lr-or-xgb-test",
        evaluate_test=True,
    )
    assert result.selection_used_test is False
    assert "validation" in result.validation_metrics or "candidates" in result.validation_metrics
    assert result.test_metrics is not None
    assert "log_loss" in result.test_metrics
    assert "baselines" in result.test_metrics

    pin = load_pin(tmp_path / "artifacts")
    assert pin["model_version"] == result.model_version
    assert pin["feature_version"] == result.feature_version
    meta = json.loads(
        (tmp_path / "artifacts" / f"{result.model_version}.json").read_text(encoding="utf-8")
    )
    assert meta["selection"]["used_test_for_selection"] is False
    assert meta["metrics"]["validation"] is not None
    assert meta["metrics"]["test"] is not None
    assert (tmp_path / "artifacts" / f"{result.model_version}.joblib").is_file()


def test_select_without_test_when_evaluate_false(tmp_path: Path) -> None:
    X, y, home_wr, away_wr = _synthetic_dataset(n=60)
    result = run_train_select_publish(
        X=X,
        y=y,
        home_season_wr=home_wr,
        away_season_wr=away_wr,
        artifacts_dir=tmp_path / "art2",
        dataset_version="synthetic-v2",
        evaluate_test=False,
    )
    assert result.test_metrics is None
    assert result.ml005_pass is None


@pytest.mark.ml005
def test_ml005_quality_gate_on_synthetic(tmp_path: Path) -> None:
    """Attestation-style: on this frozen synthetic set, selected model should beat domain baseline."""
    X, y, home_wr, away_wr = _synthetic_dataset(n=200, seed=7)
    result = run_train_select_publish(
        X=X,
        y=y,
        home_season_wr=home_wr,
        away_season_wr=away_wr,
        artifacts_dir=tmp_path / "art3",
        dataset_version="synthetic-ml005-freeze",
        seed=7,
        evaluate_test=True,
    )
    assert result.ml005_pass is True
