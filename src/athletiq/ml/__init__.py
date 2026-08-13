# Implements: FR-005, FR-006, FR-007, FR-008, ML-003, ML-004, ML-005, ML-006, ML-007, ML-009, CON-008, ADR-003, ADR-004, ADR-005
"""ML training, baselines, selection, and artifact publish."""

from __future__ import annotations

from athletiq.ml.baselines import domain_informed_predict, naive_home_predict
from athletiq.ml.metrics import accuracy, log_loss_binary
from athletiq.ml.pipeline import TrainResult, run_train_select_publish
from athletiq.ml.publish import load_pin, publish_artifacts
from athletiq.ml.select import select_model
from athletiq.ml.splits import temporal_split

__all__ = [
    "naive_home_predict",
    "domain_informed_predict",
    "log_loss_binary",
    "accuracy",
    "temporal_split",
    "select_model",
    "publish_artifacts",
    "load_pin",
    "run_train_select_publish",
    "TrainResult",
]
