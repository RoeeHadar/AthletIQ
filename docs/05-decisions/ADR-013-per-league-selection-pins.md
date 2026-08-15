# ADR-013: Separate served pins per league

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-15  
Version: 1.0.0

Decision status: Accepted

## Context

CR-004 adds WNBA on the same basketball grain. Pooling NBA and WNBA into one classifier would mix calendars, talent pools, and base rates. ADR-003 already requires validation-only selection and a batch pin the API loads — it assumed a single NBA pin.

## Decision

1. **Shared** curated schema, raw landing, and feature-builder implementation (`feature_version` contract).  
2. **Separate** train / validation / test partitions and **separate served pins** per `league` (`nba`, `wnba`).  
3. Inside each league, ADR-003 still binds: fit LR + XGBoost on that league’s train; select on that league’s validation log loss (tie → logistic regression); test once for ML-005 **within that league**.  
4. Do **not** pool leagues into one classifier.  
5. Predict resolves `game.league` and loads that league’s pin. Unknown/missing league → `nba` only if the game row is NBA; otherwise `model_unavailable` for that league.  
6. Pin file may list multiple leagues; a legacy single-object `selected_pin.json` is treated as the `nba` pin.

## Alternatives considered

- One pooled model with a league dummy — rejected (owner: no pooled classifier)  
- Separate feature builders per league — unnecessary duplication (ML-008)  
- Per-request model pick among leagues — rejected (ADR-003)

## Consequences

- Artifact names include league (e.g. `nba-xgboost-v1`, `wnba-logistic_regression-v1`).  
- `/v1/model` reports the pin for a requested league (query) or default `nba`.  
- Fixture CI trains both pins from recorded payloads (NFR-003).  
- Live `--provider nba-stats` still NBA-only; WNBA live HTTP is out of this ADR.

## References

- Related requirements: ML-007, ML-010, FR-019, CR-004  
- Related architecture: `system-architecture.md`, `api-architecture.md`  
- Amends application of ADR-003 (does not supersede it)
