---
name: architecture
description: >-
  Draft or update system, data, API, ML, and infrastructure architecture documents.
  Use when designing component boundaries, data lifecycle, API service shape, ML
  system placement, infra topology, architecture diagrams, or when the user asks for
  system architecture before implementation.
---

# Architecture

## Purpose

Own architecture docs for system + data + API + ML + infra. Flag decisions; never author ADRs.

## Progressive disclosure

Read only the reference file(s) needed for this pass:

- `references/system.md` — component flow (`system-architecture.md`)
- `references/data.md` — data lifecycle (`data-architecture.md`)
- `references/api.md` — API architecture (`api-architecture.md`)
- `references/ml.md` — ML in the system (create/update only if ML is confirmed in PRD/SRS)
- `references/infra.md` — high-level infra (detail may live in devops docs; keep boundaries clean)

## Grill-Me

Invoke **Grill-Me** for trade-offs the SRS does not resolve (build-vs-buy, scalability targets, hosting). **After** elicitation, if still undecided or the choice is material, flag `[DECISION PENDING: see ADR-XXX]` (register ADR id via architecture-decisions / id-registry coordination — this skill does **not** write the ADR file).

## Inputs (may read)

- Charter, PRD, SRS, glossary, id-registry
- Existing `docs/04-architecture/**`
- Related design docs (read-only) to avoid contradiction

## Outputs (may modify)

- `docs/04-architecture/system-architecture.md`
- `docs/04-architecture/data-architecture.md`
- `docs/04-architecture/api-architecture.md`
- `docs/04-architecture/diagrams/**`
- ML architecture sections only if ML confirmed (prefer pointing at `docs/06-design/ml-design.md` for methodology; keep system placement here)
- `docs/00-meta/id-registry.md` if minting `ARCH-` cross-refs (optional)
- `docs/00-meta/glossary.md`

Infra deep-dives (CI jobs, Compose service env): prefer **devops-operations**; this skill states topology and trust boundaries only.

## Must not touch

- `docs/05-decisions/ADR-*.md` (owned by **architecture-decisions**)
- Implementation plan, source code, `database/schema.sql`, `api/openapi.yaml` (contracts updated in design/devops passes)
- SRS primary authorship

## Boundaries

- **system** = who talks to whom
- **data** = ingest → transform → store → retain (link system diagram; do not duplicate)
- Material decisions → ADR flag only

## Procedure

1. Read SRS/PRD; load relevant `references/*.md`.
2. Grill-Me unresolved trade-offs.
3. Update architecture docs + diagrams.
4. For each material pending decision: ensure ADR-XXX id will be drafted by **architecture-decisions**; leave `[DECISION PENDING: see ADR-XXX]`.
5. After an ADR is Accepted, replace pending flags with citations.

## Validation

- [ ] Components have responsibilities
- [ ] No ADR files authored by this skill
- [ ] System vs data boundary respected
- [ ] ML architecture present only if ML is in scope
- [ ] Open Questions / pending ADRs explicitly marked
- [ ] Grill-Me used for non-derivable trade-offs

## Downstream

Trigger **architecture-decisions** for each pending ADR. Detailed design follows in design docs (often same session, still not ADR authorship).
