# Implements: FR-007, FR-008, CON-008
"""Train logistic regression and XGBoost candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from athletiq.ml.metrics import accuracy, log_loss_binary

DEFAULT_XGB_CONFIG: dict[str, Any] = {
    "n_estimators": 50,
    "max_depth": 3,
    "learning_rate": 0.1,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "eval_metric": "logloss",
    "verbosity": 0,
}


@dataclass
class FittedCandidate:
    name: str
    model: Any
    training_config: dict[str, Any]


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    *,
    seed: int = 42,
) -> FittedCandidate:
    cfg = {"C": 1.0, "max_iter": 500, "random_state": seed, "solver": "lbfgs"}
    model = LogisticRegression(**cfg)
    model.fit(X_train, y_train)
    return FittedCandidate(name="logistic_regression", model=model, training_config=cfg)


def train_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    *,
    seed: int = 42,
    config: dict[str, Any] | None = None,
) -> FittedCandidate:
    cfg = {**DEFAULT_XGB_CONFIG, **(config or {}), "random_state": seed}
    model = XGBClassifier(**cfg)
    model.fit(X_train, y_train)
    return FittedCandidate(name="xgboost", model=model, training_config=dict(cfg))


def predict_proba_positive(model: Any, X: np.ndarray) -> np.ndarray:
    proba = model.predict_proba(X)
    # positive class column
    classes = list(getattr(model, "classes_", [0, 1]))
    if 1 in classes:
        idx = classes.index(1)
    else:
        idx = -1
    return np.asarray(proba[:, idx], dtype=float)


def score_candidate(
    candidate: FittedCandidate,
    X: np.ndarray,
    y: np.ndarray,
) -> dict[str, float]:
    p = predict_proba_positive(candidate.model, X)
    return {
        "log_loss": log_loss_binary(y, p),
        "accuracy": accuracy(y, p),
    }
