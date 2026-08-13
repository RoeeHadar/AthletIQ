# Permanent project gates

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 0.2.0

These gates govern **ongoing** AthletIQ work. They are distinct from one-time setup checkpoints.

Enforced by always-on rule: `.cursor/rules/engineering-lifecycle.mdc`.

## Gate list

A gate is satisfied when its required documents are **`Approved`**, not merely `Draft`.

| Gate | Phase | Required artifacts |
|---|---|---|
| 0 | Project initiation | Project Charter |
| 1 | Product definition | PRD |
| 2 | Requirements | SRS, traceability |
| 3 | Architecture | Architecture docs, ADRs (as needed) |
| 4 | Detailed design | Relevant database / API / ML / error-handling design |
| 5 | Implementation planning | Implementation Plan |
| 6 | Implementation | Code (with `# Implements: FR-XXX` on modules listed in the plan) |
| 7 | Verification | Tests, CI, quality checks; **test strategy / test plan** live here as living docs |
| 8 | Release | Deployment notes, release notes as applicable |
| 9 | Operations | Monitoring / incidents / change process as applicable |

```text
Gate 9 … Change Request → re-enters at Gate 2 (Requirements)
```

## Feature-slice applicability (§22) — reconciled with gate numbers

**Completeness before coding (Gate 6):** Before implementing a non-trivial feature slice, the minimum **Approved** set is:

- PRD, SRS, relevant Architecture, relevant ADRs, relevant Design  
- **Implementation Plan** (Gate 5)  
- **Test Strategy** (and preferably Test Plan) — authored under Gate 7 docs, but **must be Approved before Gate 6 code starts**

Gate **numbers** order Verification after Implementation because *running* verification and closing CI/quality checks complete after code exists. That does **not** mean Test Strategy may remain Draft while coding starts.

```text
Approve: … → Design → Impl Plan → Test Strategy  →  write code (Gate 6)  →  execute/close verification (Gate 7)
```

Not every document must exist if genuinely irrelevant — the agent must state explicitly what applies and what is deliberately skipped.

## Gates vs Definition of Done

| Mechanism | Answers |
|---|---|
| Gate | When may this **phase** / feature slice start? |
| IMP task Definition of Done | When is this **single task** finished? |

## Architecture review gate (§21)

Before major implementation, run **engineering-review** covering: requirements coverage, component boundaries, data flow, failure modes, scalability, security, maintainability, observability, testing implications, operational implications, technology decisions. Record the result under `docs/00-meta/reviews/` (or as agreed with the owner).

## Trivial exemptions

Typos, formatting, and obvious bugs with no behavior/design change may proceed without re-opening gates.
