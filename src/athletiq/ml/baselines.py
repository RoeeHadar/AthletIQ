# Implements: FR-005, FR-006, ML-006
"""Deterministic baselines — never served by the API."""

from __future__ import annotations

import numpy as np


def naive_home_predict(n: int) -> np.ndarray:
    """Always predict home win with probability 1.0 (binary pred = home)."""
    return np.ones(n, dtype=float)


def domain_informed_predict(
    home_season_wr: np.ndarray,
    away_season_wr: np.ndarray,
) -> np.ndarray:
    """P(home) = 1 if home season WR >= away season WR else 0 (tie → home)."""
    home_better_or_tie = home_season_wr >= away_season_wr
    return home_better_or_tie.astype(float)
