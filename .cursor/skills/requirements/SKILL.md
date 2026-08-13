---
name: requirements
description: >-
  Draft or update the SRS and requirements traceability matrix from Charter and PRD.
  Use when writing functional or non-functional requirements, FR-/NFR-/DR-/SEC-/ML-/OPS-/CON-
  IDs, acceptance criteria, traceability.md, or turning product scope into measurable
  software requirements.
---

# Requirements

## Purpose

Produce a measurable SRS and bidirectional traceability skeleton from Approved (or current) Charter/PRD. Never invent metrics or users.

## Grill-Me

Invoke **Grill-Me** when a target is not in Charter/PRD and only the user can set it (e.g. latency budget, ML threshold). Do not invent numbers; after Grill-Me fails/deferred, use `[OPEN QUESTION: …]`.

## Inputs (may read)

- `docs/01-project/project-charter.md`
- `docs/02-product/PRD.md`
- `docs/00-meta/glossary.md`
- `docs/00-meta/id-registry.md`
- Existing `docs/03-requirements/*`

## Outputs (may modify)

- `docs/03-requirements/SRS.md`
- `docs/03-requirements/traceability.md`
- `docs/00-meta/id-registry.md` (register new IDs first)
- `docs/00-meta/glossary.md` (new terms)

## Must not touch

Architecture docs, ADRs, design docs, implementation plan, tests, devops/ops, source code, contracts.

## IDs to register

Before use: `FR-`, `NFR-`, `DR-`, `SEC-`, `ML-`, `OPS-`, `CON-`.

## Requirement shape

Each requirement must include: ID, Description, Rationale, Priority, Source, Acceptance Criteria, Dependencies, Architecture refs, Design refs, Tests.

No vague requirements (“be fast”) — only measurable expectations, or Open Question if unknown.

## Categories

| Prefix | Meaning |
|---|---|
| FR- | Functional |
| NFR- | Non-functional (performance, reliability, scalability, security, maintainability, observability, availability) |
| DR- | Data |
| SEC- | Security |
| ML- | Machine learning |
| OPS- | Operational |
| CON- | Constraint (must use/obey) |

## Procedure

1. Read Charter + PRD; refuse to invent scope not present there.
2. Register IDs in `id-registry.md`, then write SRS entries.
3. Seed `traceability.md` rows (architecture/design/impl/test columns may be empty until downstream).
4. Grill-Me any missing measurable targets.
5. Update metadata; keep Draft unless user Approves.

## Validation

- [ ] Every ID is in `id-registry.md`
- [ ] Every requirement has acceptance criteria or an explicit Open Question
- [ ] No architecture/design decisions smuggled into SRS as fake requirements
- [ ] Traceability matrix has a row per minted requirement
- [ ] Grill-Me used before any new numeric target not in PRD

## Downstream

Hand off to **architecture** (and later **testing**). Do not write ADRs.
