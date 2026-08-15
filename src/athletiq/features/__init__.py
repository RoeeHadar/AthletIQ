# Implements: FR-004, ML-001, ML-002, ML-008, ML-011, ADR-008, CR-004
"""Shared train/serve feature contract (team L5/L10 + player aggregates)."""

from __future__ import annotations

from athletiq.features.builder import (
    FEATURE_KEYS,
    FEATURE_VERSION,
    MIN_PRIOR_GAMES,
    FeatureRow,
    PlayerGameHistory,
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
    "PlayerGameHistory",
    "TeamGameHistory",
    "build_feature_row",
    "feature_vector",
    "preprocess_for_model",
    "FeatureStore",
    "InMemoryFeatureStore",
    "PostgresFeatureStore",
]
