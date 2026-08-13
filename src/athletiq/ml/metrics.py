# Implements: ML-004
"""Primary log loss + secondary accuracy."""

from __future__ import annotations

import numpy as np


def log_loss_binary(y_true: np.ndarray, y_prob: np.ndarray, *, eps: float = 1e-15) -> float:
    y = np.asarray(y_true, dtype=float)
    p = np.clip(np.asarray(y_prob, dtype=float), eps, 1.0 - eps)
    return float(-np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))


def accuracy(y_true: np.ndarray, y_prob: np.ndarray, *, threshold: float = 0.5) -> float:
    y = np.asarray(y_true, dtype=float)
    pred = (np.asarray(y_prob, dtype=float) >= threshold).astype(float)
    return float(np.mean(pred == y))


def beats_baseline(candidate_log_loss: float, baseline_log_loss: float) -> bool:
    """ML-005 comparison machinery (strictly better = lower log loss)."""
    return candidate_log_loss < baseline_log_loss
