---
name: architecture-decisions
description: >-
  Create or update Architecture Decision Records (ADRs) only. Use when a material
  architecture, cost, reliability, security, or scalability decision needs an ADR,
  when resolving DECISION PENDING flags, or when accepting, rejecting, or superseding
  an ADR.
---

# Architecture decisions (ADRs)

## Purpose

**Single owner** of all ADR files. Keep this skill small and format-strict.

## Grill-Me

If the proposing skill already ran Grill-Me, use that outcome as Context. If the user must still choose among alternatives, invoke **Grill-Me** before setting Decision status to Accepted.

## Inputs (may read)

- PRD, SRS, architecture docs, design docs, whatever flagged `[DECISION PENDING: see ADR-XXX]`
- Existing `docs/05-decisions/**`
- `docs/00-meta/id-registry.md`

## Outputs (may modify)

- `docs/05-decisions/ADR-XXX-*.md` (create/update)
- `docs/05-decisions/README.md` (index)
- `docs/00-meta/id-registry.md` (register `ADR-XXX` before use)

## Must not touch

Primary content of Charter/PRD/SRS/architecture/design beyond replacing pending flags **after** Accepted (architecture skill usually updates citations; this skill may patch the pending marker to a citation if explicitly completing the loop). Prefer asking **architecture** to refresh docs when large.

Never write implementation code.

## Decision status enum

`Proposed | Accepted | Rejected | Superseded | Deprecated`

(Document Status remains Draft/In Review/Approved/… separately in the metadata header.)

## Procedure

1. Register `ADR-XXX` in id-registry.
2. Create from `ADR-template.md`: Context, Decision, Alternatives, Consequences, References.
3. Status starts `Proposed` unless user accepts in-session.
4. On Accept: set Decision status Accepted; ensure Consequences are non-empty; notify architecture docs to cite it.
5. On supersede: set old ADR Superseded; link bidirectional.

## Validation

- [ ] ID registered
- [ ] Consequences documented before Accepted
- [ ] Alternatives listed
- [ ] No trivial implementation detail ADRs (lint rules, rename-only, etc.)
- [ ] README index updated

## Only ADR files

Do not absorb system-architecture authorship into this skill.
