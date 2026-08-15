# Implements: FR-010
"""FR-010 methodology / limitations summary for GET /v1/model (aligned with model card)."""

from __future__ import annotations

from typing import Any

# Canonical long-form disclosure (repo-relative).
MODEL_CARD_REF = "docs/06-design/model-card.md"

METHODOLOGY: dict[str, Any] = {
    "task": "pre-game home-win binary classification + P(home_win)",
    "temporal_boundary": (
        "Features and evaluation use only information available before tip; no post-tip leakage"
    ),
    "split": {
        "scheme": "temporal",
        "fractions": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "order": "oldest_to_newest_by_game_start_time",
        "shuffle": False,
    },
    "selection": {
        "metric": "log_loss",
        "partition": "validation",
        "tie_break": "logistic_regression",
        "test_used_for_selection": False,
    },
    "primary_metric": "log_loss",
    "secondary_metric": "accuracy",
    "baselines": {
        "naive": "always_home",
        "domain_informed": "better_pregame_season_wr_tie_home",
        "served": False,
    },
    "candidates": ["logistic_regression", "xgboost"],
    "feature_version_default": "team_l5_l10_v1",
    "min_prior_games": 5,
}

LIMITATIONS_TEXT = (
    "Demo-grade local API (NFR-002). No hard latency/availability SLO (NFR-004). "
    "No application auth (ADR-009). Baselines are never served. "
    "Temporal ~70/15/15 split; selection on validation log loss only (tie → LR); "
    "test set used once for ML-005. Team-level L5/L10 + season WR features only; "
    "cold start uses season-to-date when prior games < 5. "
    "Live NBA pin logistic_regression-v1: sklearn lbfgs max_iter=500 emitted "
    "ConvergenceWarning; reported test log loss is that fit, not full optimizer "
    "convergence (config not changed after inspecting test metrics). "
    "Does not claim to accurately predict NBA games — see model card."
)


def model_disclosure(
    *,
    model_version: str,
    feature_version: str,
    dataset_version: str | None,
    metrics: dict[str, Any] | None,
) -> dict[str, Any]:
    """Payload for GET /v1/model."""
    return {
        "model_version": model_version,
        "feature_version": feature_version,
        "dataset_version": dataset_version,
        "metrics": metrics,
        "methodology": METHODOLOGY,
        "limitations": LIMITATIONS_TEXT,
        "model_card_ref": MODEL_CARD_REF,
        "baselines_served": False,
    }
