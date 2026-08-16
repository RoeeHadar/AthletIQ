# AthletIQ documentation

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 0.3.3

Living documentation for AthletIQ. Read this index first; do not duplicate content across docs — follow the source-of-truth rules in `00-meta/documentation-guide.md`.

Root overview + local Compose demo: [`../README.md`](../README.md).

## Hierarchy

| Folder | Purpose |
|---|---|
| `00-meta/` | ID registry, glossary, documentation guide, [gates](00-meta/gates.md), [quality checks](00-meta/quality-checks.md), [agent memory spec](00-meta/agent-memory-system.md) (portable skill anchor, Approved; installer: `.cursor/skills/memory-creator/`) |
| `01-project/` | Project Charter (sponsorship / boundaries) |
| `02-product/` | PRD (product / user intent) |
| `03-requirements/` | SRS + bidirectional traceability |
| `04-architecture/` | System, data, API architecture (+ diagrams) |
| `05-decisions/` | Architecture Decision Records (ADRs) |
| `06-design/` | Detailed design (DB, API, ML, errors) + [model card](06-design/model-card.md) |
| `07-implementation/` | Implementation plan (task → requirement mapping) |
| `08-testing/` | Test strategy and requirement-driven test plan |
| `09-devops/` | CI/CD, infrastructure, deployment |
| `10-operations/` | Observability, logging, incident response |
| `11-change-management/` | Change requests (re-enter at requirements); **CR-001**–**CR-005** Accepted |
| `12-releases/` | Release process and notes template |

## Machine-consumable contracts (alongside prose)

| Path | Role |
|---|---|
| `api/openapi.yaml` | API contract |
| `database/schema.sql` | Database contract |
| `docker-compose.yml` | Local multi-container **MVP topology** (`database` / `etl` / `api`) |
| `.github/workflows/ci.yml` | CI **MVP workflow** (lint ∥ unit → integration → image build) |

## Gates (summary)

Implementation of non-trivial features requires upstream documents **Approved** (not merely Draft). See root `README.md` and `00-meta/documentation-guide.md` for the permanent gate list. Change Requests re-enter at requirements.
