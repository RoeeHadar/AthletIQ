# ADR-008: Inference feature contract — game_id + precomputed features

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

Decision status: Accepted

## Context

Precomputed features (Option B) require a precise lookup key. Ambiguity between “pass two teams and compute live” vs “lookup existing game features” would break training–serving consistency.

## Decision

- MVP predictions are for an existing **`game_id`**.  
- Features are materialized by the **same feature-builder implementation** used in training.  
- Feature rows are uniquely identified by **`(game_id, feature_version)`**.  
- Optional `provider_game_id` may **resolve** to a unique `game_id`. Home/away/date matchup input is **Future / not MVP** — it must not appear in OpenAPI and must not compute a divergent feature path.  
- Inference is **synchronous**.

## Alternatives considered

- Live feature computation in API from team IDs — higher leakage/drift risk  
- Precompute all possible future matchups — combinatorial explosion  
- Async prediction jobs — unnecessary for MVP

## Consequences

- Feature builder is a shared library/module, not duplicated in API.  
- Predict fails clearly if feature row missing for pinned `feature_version`.  
- OpenAPI centers on `game_id` plus optional **`provider_game_id`** resolver. Home/away/date is out of MVP.  
- Internal SQL type of `game_id` is **BIGINT** (**ADR-010**); wire format remains decimal string.

## References

- Related requirements: FR-004, FR-009, FR-014, ML-008  
- Related architecture: `api-architecture.md`, `data-architecture.md`, `system-architecture.md`  
- Owner architecture review 2026-08-12
