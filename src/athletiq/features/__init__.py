# Implements: FR-004, ML-001, ML-002, ML-008, ADR-008
"""Shared train/serve feature contract (team L5/L10 + season WR)."""

from __future__ import annotations

from athletiq.features.builder import (
    FEATURE_KEYS,
    FEATURE_VERSION,
    MIN_PRIOR_GAMES,
    FeatureRow,
    TeamGameHistory,
    build_feature_row,
    feature_vector,
    preprocess_for_model,
)
from athletiq.features.postgres import PostgresFeatureStore
from athletiq.features.store import FeatureStore, InMemoryFeatureStore

__all__ = [
    "FEATURE_KEYS",
    "FEATURE_VERSION",
    "MIN_PRIOR_GAMES",
    "FeatureRow",
    "TeamGameHistory",
    "build_feature_row",
    "feature_vector",
    "preprocess_for_model",
    "FeatureStore",
    "InMemoryFeatureStore",
    "PostgresFeatureStore",
]
