# Implements: FR-005…008, ML-003…007, ML-009, ML-010, ADR-003, ADR-005, ADR-013
"""Train → validation select → test-once → publish."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from athletiq.features.builder import FEATURE_VERSION
from athletiq.ml.baselines import domain_informed_predict, naive_home_predict
from athletiq.ml.metrics import accuracy, beats_baseline, log_loss_binary
from athletiq.ml.publish import ModelMetadata, publish_artifacts
from athletiq.ml.select import select_model
from athletiq.ml.splits import temporal_split
from athletiq.ml.train import (
    predict_proba_positive,
    score_candidate,
    train_logistic_regression,
    train_xgboost,
)

logger = logging.getLogger("athletiq.ml")


@dataclass
class TrainResult:
    model_version: str
    feature_version: str
    selected_family: str
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any] | None
    baseline_test: dict[str, float]
    ml005_pass: bool | None
    pin_path: Path
    selection_used_test: bool  # must remain False


def run_train_select_publish(
    *,
    X: np.ndarray,
    y: np.ndarray,
    home_season_wr: np.ndarray,
    away_season_wr: np.ndarray,
    artifacts_dir: Path,
    dataset_version: str,
    code_commit: str | None = None,
    seed: int = 42,
    feature_version: str = FEATURE_VERSION,
    model_version: str | None = None,
    evaluate_test: bool = True,
    pin_name: str = "selected_pin.json",
    model_version_prefix: str = "",
) -> TrainResult:
    """Full MVP ML batch. Selection never sees the test set."""
    n = len(y)
    split = temporal_split(n)
    X_a = np.asarray(X, dtype=float)
    y_a = np.asarray(y, dtype=float)
    home_a = np.asarray(home_season_wr, dtype=float)
    away_a = np.asarray(away_season_wr, dtype=float)

    X_train_a, y_train_a = X_a[split.train], y_a[split.train]
    X_val_a, y_val_a = X_a[split.validation], y_a[split.validation]
    X_test_a, y_test_a = X_a[split.test], y_a[split.test]

    lr = train_logistic_regression(X_train_a, y_train_a, seed=seed)
    xgb = train_xgboost(X_train_a, y_train_a, seed=seed)
    candidates = [lr, xgb]

    val_scores = {c.name: score_candidate(c, X_val_a, y_val_a) for c in candidates}
    selection = select_model(candidates, val_scores)
    selection_used_test = False

    # Baselines on same partitions (never served)
    naive_val = naive_home_predict(len(y_val_a))
    # domain-informed needs season WR aligned to rows
    home_wr_val = home_a[split.validation]
    away_wr_val = away_a[split.validation]
    domain_val = domain_informed_predict(home_wr_val, away_wr_val)

    validation_metrics = {
        "candidates": val_scores,
        "selected": selection.selected.name,
        "baselines": {
            "naive": {
                "log_loss": log_loss_binary(y_val_a, naive_val),
                "accuracy": accuracy(y_val_a, naive_val),
            },
            "domain_informed": {
                "log_loss": log_loss_binary(y_val_a, domain_val),
                "accuracy": accuracy(y_val_a, domain_val),
            },
        },
        "selection_rule": selection.rule,
    }

    test_metrics: dict[str, Any] | None = None
    baseline_test: dict[str, float] = {}
    ml005_pass: bool | None = None

    if evaluate_test:
        p_test = predict_proba_positive(selection.selected.model, X_test_a)
        cand_ll = log_loss_binary(y_test_a, p_test)
        home_wr_test = home_a[split.test]
        away_wr_test = away_a[split.test]
        domain_test = domain_informed_predict(home_wr_test, away_wr_test)
        domain_ll = log_loss_binary(y_test_a, domain_test)
        naive_test = naive_home_predict(len(y_test_a))
        baseline_test = {
            "naive_log_loss": log_loss_binary(y_test_a, naive_test),
            "domain_informed_log_loss": domain_ll,
            "domain_informed_accuracy": accuracy(y_test_a, domain_test),
        }
        test_metrics = {
            "selected": selection.selected.name,
            "log_loss": cand_ll,
            "accuracy": accuracy(y_test_a, p_test),
            "baselines": baseline_test,
        }
        ml005_pass = beats_baseline(cand_ll, domain_ll)
        logger.info(
            "stage=eval partition=test selected=%s log_loss=%s ml005=%s",
            selection.selected.name,
            cand_ll,
            ml005_pass,
        )

    version = model_version or f"{model_version_prefix}{selection.selected.name}-v1"
    meta = ModelMetadata(
        model_version=version,
        feature_version=feature_version,
        dataset_version=dataset_version,
        code_commit=code_commit,
        training_config=selection.selected.training_config,
        metrics={
            "validation": validation_metrics,
            "test": test_metrics,
        },
        selection={
            "rule": selection.rule,
            "validation_scores": val_scores,
            "used_test_for_selection": selection_used_test,
        },
        model_family=selection.selected.name,
    )
    pin_path = publish_artifacts(
        artifacts_dir=artifacts_dir,
        model=selection.selected.model,
        metadata=meta,
        pin_name=pin_name,
    )
    return TrainResult(
        model_version=version,
        feature_version=feature_version,
        selected_family=selection.selected.name,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        baseline_test=baseline_test,
        ml005_pass=ml005_pass,
        pin_path=pin_path,
        selection_used_test=selection_used_test,
    )
