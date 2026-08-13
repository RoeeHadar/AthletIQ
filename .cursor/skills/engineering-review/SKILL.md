---
name: engineering-review
description: >-
  Review architecture coverage, documentation consistency, requirements traceability,
  and design/contract/implementation drift. Use when auditing docs before implementation,
  checking Accepted ADR consequences, finding contradictions, stale docs, missing
  Implements annotations, or producing an architecture review / drift report.
---

# Engineering review

## Purpose

Read-only reviewer. Produce findings; **never** author primary Charter/PRD/SRS/architecture/ADR/design/impl/test content; **never** call Grill-Me. Flag gaps for a human (or the owning skill) to resolve.

## Inputs (may read)

Everything under `docs/`, plus contracts and implementation when present:

- `api/openapi.yaml`, `database/schema.sql`, migrations/source, CI workflows, Compose

## Outputs

Write a review artifact only, e.g.:

- `docs/00-meta/reviews/YYYY-MM-DD-<topic>.md` (create `reviews/` if needed), **or**
- A clearly labeled report in the chat if the user prefers no file

Do not “fix” primary docs silently — list required edits per owning skill.

## Must not touch

Primary content ownership of other skills (except creating review report files under `docs/00-meta/reviews/`).

## Checklist

### Architecture review gate

- Requirements coverage; component boundaries; data flow; failure modes; scalability; security; maintainability; observability; testing implications; operational implications; technology decisions

### Documentation quality

- Broken references; missing requirement IDs; requirements without acceptance criteria; components without responsibilities; requirements not covered by architecture; decisions without rationale; **Accepted ADRs without consequences**; design without upstream justification; tests without requirements (and vice versa where applicable); contradictions; stale `Last Updated`; duplicate definitions; undefined terms vs glossary; Charter/PRD overlap; missing `# Implements` annotations where Implementation Plan lists modules

### Drift (§13a)

| Layer | DB | API | ML |
|---|---|---|---|
| Design | database-design.md | api-design.md | ml-design.md |
| Contract | schema.sql | openapi.yaml | model registry |
| Implementation | migrations/source | source | training code |

Report “design says X, contract says Y, code does Z” as defects.

### Gates

For a proposed implementation slice, state which Gate 0–9 docs are Approved vs missing/Draft.

## Validation

- [ ] No Grill-Me invocation
- [ ] No primary doc authorship disguised as review
- [ ] Every Accepted ADR checked for consequences
- [ ] Findings actionable and mapped to owning skill when possible
