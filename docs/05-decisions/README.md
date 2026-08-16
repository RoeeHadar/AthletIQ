# Architecture Decision Records

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.3.0

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
| [ADR-012](ADR-012-synthetic-odds-snapshots.md) | Fixture/synthetic odds snapshots | Accepted |
| [ADR-013](ADR-013-per-league-selection-pins.md) | Per-league selection pins | Accepted |
| [ADR-014](ADR-014-demo-identity-ecoin-ledger.md) | Demo identity + e-coin ledger | Accepted |
| [ADR-015](ADR-015-game-lifecycle-board-poll-settle.md) | Scheduled persist, board poll, pipeline settle | Accepted |
| [ADR-016](ADR-016-three-ui-surfaces.md) | Three FastAPI surfaces `GET /`, `/slate`, `/board` | Accepted |
| [ADR-017](ADR-017-uncapped-nba-live-player-boxes.md) | Uncapped live NBA + live player boxes (extends ADR-011) | Accepted |

## Deferred / non-binding

| ADR | Note |
|---|---|
| [ADR-007](ADR-007-post-mvp-gcp.md) | GCP candidate only — revisit at Gate 8 |

Template: `ADR-template.md`.
