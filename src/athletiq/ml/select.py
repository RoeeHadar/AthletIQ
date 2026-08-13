# Implements: ML-007, ADR-003
"""Model selection on validation log loss only (tie → logistic regression)."""

from __future__ import annotations

from dataclasses import dataclass

from athletiq.ml.train import FittedCandidate


@dataclass(frozen=True)
class SelectionResult:
    selected: FittedCandidate
    validation_scores: dict[str, dict[str, float]]
    rule: str


def select_model(
    candidates: list[FittedCandidate],
    val_scores: dict[str, dict[str, float]],
) -> SelectionResult:
    """Pick lowest validation log loss; ties prefer logistic_regression."""
    if not candidates:
        raise ValueError("no candidates")
    best = candidates[0]
    best_ll = val_scores[best.name]["log_loss"]
    for c in candidates[1:]:
        ll = val_scores[c.name]["log_loss"]
        if ll < best_ll - 1e-15:
            best, best_ll = c, ll
        elif abs(ll - best_ll) <= 1e-15:
            # tie → LR
            if c.name == "logistic_regression":
                best, best_ll = c, ll
            elif best.name != "logistic_regression" and c.name == "logistic_regression":
                best, best_ll = c, ll
    # Explicit tie preference: if equal, ensure LR wins
    tied = [
        c
        for c in candidates
        if abs(val_scores[c.name]["log_loss"] - best_ll) <= 1e-15
    ]
    if len(tied) > 1:
        for c in tied:
            if c.name == "logistic_regression":
                best = c
                break
    return SelectionResult(
        selected=best,
        validation_scores=val_scores,
        rule="min_val_log_loss_tie_logistic_regression",
    )
