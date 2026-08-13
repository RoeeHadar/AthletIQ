# ADR-004: Model artifact storage (MVP local; post-MVP GCP)

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 1.0.0

Decision status: Accepted

## Context

Trained models, evaluation reports, and model cards must be durable across pipeline and API containers without introducing production ML platform scope.

## Decision

**MVP:** store artifacts on a **local filesystem volume** (bind mount or Compose named volume) shared by train batch and API.

**Future:** if/when cloud CD is designed, artifact location may move (e.g. object storage). GCP is only a **candidate** platform (ADR-007 Proposed) — not a commitment in this ADR.

## Alternatives considered

- MLflow / cloud model registry in MVP — conflicts with PRD non-goal (no production ML ops)
- DB BYTEA for models — awkward for XGBoost artifacts and tooling
- Cloud object store from day one — premature before local demo works

## Consequences

- Compose must mount the same artifacts path into train and API.
- `.gitignore` artifacts binaries; keep schema/examples of metadata JSON in repo if useful.
- “Model registry” in prose means **metadata + selection pin**, not MLflow.

## References

- Related requirements: FR-009, FR-010, FR-014, NFR-001, NFR-002  
- Related architecture docs: `system-architecture.md`, `data-architecture.md`  
- Grill-Me architecture Q4; owner review 2026-08-12
