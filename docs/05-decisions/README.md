# Architecture Decision Records

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-14  
Version: 1.1.1

## Binding index (MVP)

| ADR | Title | Decision status |
|---|---|---|
| [ADR-001](ADR-001-postgresql.md) | PostgreSQL | Accepted |
| [ADR-002](ADR-002-api-sports-provider.md) | API-Sports NBA | **Superseded** by ADR-011 |
| [ADR-011](ADR-011-nba-stats-api-provider.md) | NBA Stats API (no-key live) | Accepted |
| [ADR-003](ADR-003-served-model-selection.md) | Validation select / test once | Accepted |
| [ADR-004](ADR-004-artifact-storage.md) | Local artifacts | Accepted |
| [ADR-005](ADR-005-training-as-batch.md) | Batch + Python orchestrator | Accepted |
| [ADR-006](ADR-006-raw-landing.md) | Immutable raw JSON FS | Accepted |
| [ADR-008](ADR-008-inference-feature-contract.md) | game_id + precomputed features | Accepted |
| [ADR-009](ADR-009-no-auth-mvp-api.md) | No auth on MVP demo API | Accepted |
| [ADR-010](ADR-010-bigint-surrogate-keys.md) | BIGINT / BIGSERIAL surrogate keys | Accepted |

## Deferred / non-binding

| ADR | Note |
|---|---|
| [ADR-007](ADR-007-post-mvp-gcp.md) | GCP candidate only — revisit at Gate 8 |

Template: `ADR-template.md`.
