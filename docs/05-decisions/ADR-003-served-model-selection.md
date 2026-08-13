# ADR-003: Model selection on validation; final report on test

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 1.1.0

Decision status: Accepted

## Context

Selecting the served model using the same set used for final reported metrics contaminates the test estimate (owner architecture review). SRS originally used a single holdout for both.

## Decision

1. Use a **temporal train / validation / test** partition (exact cut points in ML design).  
2. Fit LR and XGBoost on **train**; compute validation metrics; **select** the served model as the candidate with best (lowest) **validation log loss** (tie → logistic regression).  
3. Evaluate baselines + selected comparison on **test once** for final reporting and ML-005 (at least one of LR/XGB beats domain-informed baseline on **test** log loss).  
4. Persist a **selection pin** in artifact metadata at batch time. The API **loads the pin only** — no per-request model selection.  
5. Baselines are never served.

## Alternatives considered

- Single holdout for selection + reporting — rejected (leakage into “final” metrics)
- Always serve XGBoost — may not win on validation
- API picks model at request time — rejected (runtime complexity)

## Consequences

- SRS ML-003/ML-005 amended to three-way split.  
- Registry renamed conceptually to **model metadata / selection pin** (not a full MLflow registry).  
- Stronger honesty in model card: selection set vs test set clearly labeled.

## References

- Related requirements: FR-005–FR-009, ML-003, ML-004, ML-005, ML-007  
- Related architecture docs: `system-architecture.md`, `api-architecture.md`  
- Owner architecture review 2026-08-12; prior Grill-Me Q3 amended
