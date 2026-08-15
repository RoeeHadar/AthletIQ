# Change management

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 0.3.0

Living process for scope and requirement changes. Change Requests **re-enter at Gate 2 (Requirements)** — they are not the end of the chain.

**Accepted CRs:** [CR-001](CR-001-mvp-team-stats-not-players.md) — MVP persist/ingest is team-level; player tables reserved. [CR-002](CR-002-nba-stats-api-provider.md) — live provider is no-key NBA Stats API (ADR-011). [CR-003](CR-003-minimal-prediction-ui.md) — local prediction UI at `GET /`.

## Propagation flow

```text
Requirement changed (or CR Accepted)
        ↓
Identify impacted requirements → architecture → ADRs → designs → implementation → tests
        ↓
Update traceability matrix + bump doc versions (metadata §2a)
        ↓
Re-Approve affected docs before non-trivial implementation continues
```

## When to use a Change Request

Use a CR (`change-request-template.md`) when, after Charter/PRD/SRS exist:

- Scope, goals, non-goals, or success criteria change
- A material requirement is added, removed, or redefined
- An Accepted ADR must be superseded because reality changed
- Post-MVP items are pulled into MVP (or vice versa) in a way that affects gates

Skip a formal CR for typo-only doc edits that do not change meaning.

## CR procedure

1. Register `CR-XXX` in `docs/00-meta/id-registry.md`.
2. Fill `change-request-template.md` → save as `CR-XXX-<slug>.md` in this folder.
3. Decision status starts `Proposed`.
4. Owner sets `Accepted` | `Rejected` | later `Superseded`.
5. If Accepted: run impact updates via owning skills (`requirements`, `architecture`, `architecture-decisions`, etc.); bump versions; refresh `traceability.md`; update Implementation Plan tasks.
6. Do not implement code for an Accepted CR until affected gate docs are **Approved** again.

## Decision status (CR only)

`Proposed | Accepted | Rejected | Superseded` — distinct from document Status (`Draft | In Review | Approved | …`).

## Related

- Gates: `docs/00-meta/gates.md`
- Quality checks: `docs/00-meta/quality-checks.md`
- Always-on enforcement: `.cursor/rules/engineering-lifecycle.mdc`
