# Documentation guide

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 0.3.0

## Purpose

Rules for authoring and maintaining AthletIQ docs so agents and humans share one lifecycle.

## Metadata (every doc under `docs/`)

```text
Status: Draft | In Review | Approved | Superseded | Deprecated
Owner: [role or TBD]
Last Updated: [YYYY-MM-DD]
Version: [semantic or incrementing integer]
```

Decision status (ADRs and Change Requests only — not document status):

```text
Proposed | Accepted | Rejected | Superseded | Deprecated
```

## Content classification

Distinguish explicitly:

- **Known** — confirmed (e.g. via Grill-Me)
- **Assumption** — `[ASSUMPTION — needs confirmation]`
- **Decision** — recorded in an ADR when material
- **Open Question** — `[OPEN QUESTION: ...]` only after Grill-Me could not resolve
- **Future Consideration** — out of current phase; still documented when relevant

## Charter vs PRD

- **Charter** — why the effort exists, who is accountable, organizational boundaries. No user/feature sentences.
- **PRD** — what gets built and for whom. Reference the Charter; do not restate it.

## Design vs contract vs implementation

| Layer | Database | API | ML |
|---|---|---|---|
| Design | `06-design/database-design.md` | `06-design/api-design.md` | `06-design/ml-design.md` |
| Contract | `database/schema.sql` | `api/openapi.yaml` | selection pin + joblib + lineage JSON (ADR-003/004; not a TBD MLflow registry) |
| Implementation | migrations / source | source | training code + pin JSON + joblib artifact |

Disagreement across layers is a defect (`engineering-review`), not three valid truths.

## IDs

Mint IDs only via `00-meta/id-registry.md` (append-only). Prefixes: FR-, NFR-, DR-, SEC-, ML-, OPS-, CON-, ARCH-, ADR-, DESIGN-, TEST-, IMP-, CR-.

## Traceability

- Forward/reverse matrix: `03-requirements/traceability.md`
- Code annotations (`# Implements: FR-XXX`) only on files/modules listed under Implementation Plan task “Files/modules affected”. **Not** on test files (TEST ids live in the test plan).

## Change propagation

Requirement change → impact analysis → update architecture / ADRs / design / implementation / tests → bump versions → update traceability. Post-live changes use Change Requests (`11-change-management/`).

## Gates and quality

- Permanent gates: `gates.md`
- Quality checklist: `quality-checks.md`
- Always-on enforcement: `.cursor/rules/engineering-lifecycle.mdc`

## Do not

Invent product facts, fake metrics, fictional users, or present assumptions as Known. Invoke Grill-Me before placeholders for user-only decisions. See also anti-over-engineering in `quality-checks.md`.
