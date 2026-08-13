---
name: project-discovery
description: >-
  Draft or update the Project Charter and PRD from real user elicitation.
  Use when starting a project, defining product purpose/scope, writing or revising
  project-charter.md or PRD.md, clarifying stakeholders, goals, non-goals, personas,
  MVP scope, or success criteria — before requirements or architecture work.
---

# Project discovery

## Purpose

Elicit and record **organizational** (Charter) and **product** (PRD) truth. This skill never invents product facts.

## Elicitation (required)

Invoke the **Grill-Me** skill (`.cursor/skills/grill-me/` → `/grilling`) before writing Known content. Cover Charter + PRD themes: purpose, stakeholders, scope, constraints, users/personas, goals, non-goals, success criteria, MVP vs future.

Placeholders (`[OPEN QUESTION]`, `[ASSUMPTION — needs confirmation]`, `[FUTURE CONSIDERATION]`) are allowed **only** after Grill-Me leaves something unresolved or the user defers.

## Inputs

- User answers via Grill-Me (primary)
- Existing `docs/01-project/project-charter.md` / `docs/02-product/PRD.md` if updating
- `docs/00-meta/glossary.md` for shared terms

## Outputs (may modify)

- `docs/01-project/project-charter.md`
- `docs/02-product/PRD.md`
- `docs/00-meta/glossary.md` (new terms only)
- `docs/README.md` index pointers if paths change (rare)

## Must not touch

- SRS, traceability, architecture, ADRs, design, implementation plan, tests, devops, operations, source code, contracts (`api/`, `database/`), CI workflows
- Do not mint FR-/NFR-/ADR-/IMP-/TEST-/CR- IDs (no requirements yet)

## IDs

None required. If glossary introduces ambiguous domain terms, define them in `glossary.md` without ID registry entries.

## Charter vs PRD (enforce)

| Document | Owns |
|---|---|
| Charter | Why the effort exists, sponsorship, accountability, organizational boundaries |
| PRD | What gets built, for whom, goals/non-goals, journeys, features, MVP/future, success metrics |

If a sentence could live in either: Charter only if it says nothing about users or features; otherwise PRD only. PRD references Charter — does not restate it.

## Procedure

1. Read current Charter/PRD if present; note Status/Version.
2. Run Grill-Me rounds until the frontier for Charter/PRD is empty or user confirms shared understanding.
3. Write **Known** sections from Grill-Me output (not a transcript dump).
4. Mark deferred items with the correct placeholder type.
5. Update metadata: `Last Updated`, bump `Version`, keep `Status: Draft` unless the user explicitly Approves.
6. Run validation below.

## Validation (before completing)

- [ ] Grill-Me was run (or explicitly N/A for a tiny metadata-only edit)
- [ ] No invented users, metrics, or constraints presented as Known
- [ ] Charter/PRD boundary respected (no feature lists in Charter; no sponsorship essay in PRD)
- [ ] Every Open Question / Assumption is labeled
- [ ] Glossary updated for any new shared term
- [ ] Metadata header present on both docs

## Downstream

When Charter + PRD are ready for requirements, hand off to the **requirements** skill. Do not draft SRS here.
