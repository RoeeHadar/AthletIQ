---
name: implementation-planning
description: >-
  Draft or update the implementation plan with IMP tasks, requirement mapping,
  files/modules affected, and Definition of Done. Use when sequencing build work,
  creating IMP-XXX tasks, defining annotation targets for Implements comments,
  or planning implementation after design is ready.
---

# Implementation planning

## Purpose

Bridge Approved (or current) design to code via `docs/07-implementation/implementation-plan.md`. The **Files/modules affected** lists are the sole source of truth for where `# Implements: FR-XXX` annotations belong.

## Grill-Me

Invoke **Grill-Me** only for sequencing/scope choices not derivable from upstream docs (e.g. which post-MVP slice to schedule). Prefer upstream docs otherwise.

## Inputs (may read)

- Charter → PRD → SRS → architecture → ADRs → design → test strategy
- glossary, id-registry
- Existing implementation plan

## Outputs (may modify)

- `docs/07-implementation/implementation-plan.md`
- `docs/00-meta/id-registry.md` (`IMP-` ids)
- Optionally refresh empty Implementation column hints in `traceability.md` (task ids only — not fake completion)

## Must not touch

- Source code (this skill plans; it does not implement)
- ADR authorship
- Inventing new product requirements (send gaps to **requirements**)

## Task fields (required)

```text
Task ID (IMP-XXX)
Title
Requirement IDs
Architecture references
Design references
Dependencies (other IMP-XXX)
Files/modules affected
Implementation sequence notes
Testing requirements (TEST-XXX)
Definition of Done (checklist below)
Status
```

### Definition of Done (every task)

```text
[ ] Requirements satisfied
[ ] Design satisfied
[ ] Tests implemented and passing
[ ] Logging/observability addressed
[ ] Error handling addressed
[ ] Documentation updated
[ ] Traceability matrix + code annotations updated
[ ] Code review passed
[ ] CI passed
```

## Procedure

1. Confirm upstream docs exist for the slice being planned; list deliberate skips.
2. Register IMP- ids; write tasks with real file/module paths when known, or path patterns with Open Question.
3. Ensure every Must requirement in scope maps to ≥1 IMP task.
4. Do not start coding in this skill.

## Validation

- [ ] Every IMP id registered
- [ ] DoD checklist present on each task
- [ ] Files/modules affected present (annotation key)
- [ ] Requirement IDs reference minted SRS ids
- [ ] No application source edited

## Note on gates vs DoD

Gates (§22a / engineering-lifecycle rule) decide when a **phase** may start. DoD decides when a **task** is finished.
