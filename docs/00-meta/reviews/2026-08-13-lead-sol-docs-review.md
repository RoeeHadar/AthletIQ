# Lead engineering review — AthletIQ documentation, contracts, and drift

Status: Complete  
Date: 2026-08-13  
Reviewer role: Lead engineering reviewer (independent read-only pass)  
Scope: `docs/`, Accepted ADR consequences, DB/API/ML design-contract-code triples, tests, Compose, and CI workflow

## Executive verdict

The CR-001 honesty pass is materially sound. MVP ingestion and persistence consistently mean teams, games, and `team_game_stats`; player tables are explicitly reserved. The SRS no longer requires player fetch, the provider/load code does not write player data, traceability separates Requirement / Implementation / Verification, `schema_migrations` is in the schema contract, OpenAPI says `security: []`, and TEST-005 is now honestly labeled unit/in-memory.

This is nevertheless **below 9/10**. The remaining disagreement is not minimal: NFR-001 and FR-012 are reported as Implemented / Passing (local), while the repository has no complete documented clean-clone setup and no test that brings up Compose, runs the Postgres pipeline into the shared volumes, then proves the API serves that pin and those feature rows. TEST-013 proves deterministic synthetic training, not clean-environment reproducibility. TEST-010 proves topology/config only. The documented ETL command also omits `--store postgres`, so it defaults to memory. That would mislead a reviewer about the local-demo path even though the PRD checklist correctly remains unchecked.

**Score: 8 / 10**  
**≥9 / 10: no**

## Findings

| ID | Severity | Status | Area | Evidence | Owning skill | Required disposition |
|---|---|---|---|---|---|---|
| LEAD-001 | **Major — blocks 9/10** | **OPEN** | Reproducibility / local-demo honesty | NFR-001 requires documented clean-machine execution (`docs/03-requirements/SRS.md`); traceability marks NFR-001 **Implemented / Passing (local)** (`docs/03-requirements/traceability.md`). TEST-013 is only controlled synthetic feature/train repetition (`tests/unit/test_reproducibility.py`), not clone/setup/Compose/pipeline/API. TEST-010 only statically checks services/volumes and optionally `docker compose config` (`tests/integration/test_compose.py`); it never brings up the stack. Root `README.md` has no setup/run procedure. `docs/09-devops/infrastructure.md` and the Compose comment show `docker compose run --rm etl python -m athletiq.pipeline …`, but CLI defaults `--store memory` (`src/athletiq/pipeline/__main__.py`), so that documented command does not populate PostgreSQL unless the omitted argument is supplied. | `testing` + `devops-operations`; implementation only if an executable demo path is added | Until an actual clean-path attestation exists, mark NFR-001 and the end-to-end portion of FR-012 Partial/Planned rather than Passing. Document one unambiguous Compose workflow that selects Postgres and shares artifacts with the API, then test bring-up → pipeline → healthy API/predict. |
| LEAD-002 | Minor | **OPEN** | ADR-005 resume consequence | ADR-005 says stages are checkpointed so partial failures can resume. `PipelineContext.save_state()` writes state, but no code loads it. `--from-stage train` can rediscover `feature_matrix.npz`; `--from-stage features` still requires `ctx.store` from the same process and fails after restart (`src/athletiq/pipeline/orchestrator.py`, `stages.py`). TEST-009 checks stage selection and a same-process happy path, not restart/resume (`tests/unit/test_pipeline.py`). | implementation-planning / implementation / testing | Narrow the claim to the resume cases actually supported, or implement and verify state restoration for advertised restart points. |
| LEAD-003 | Minor | **OPEN** | API architecture drift | System/API architecture and ADR-008 allow an optional home/away/date matchup resolver. OpenAPI and code expose only `game_id` and `provider_game_id` (`api/openapi.yaml`, `api/app/routes.py`). | `architecture` / `architecture-decisions` | Remove the unimplemented resolver promise or explicitly label it future/optional; do not add it merely to close a documentation nit. |

### OPEN findings blocking 9/10

- **LEAD-001** — clean-environment / Compose end-to-end verification is overstated in Approved traceability.

## Gate snapshot

Gate status is based on artifact approval, not code existence or an IMP checkbox.

| Gate | Phase | Snapshot |
|---|---|---|
| 0 | Project initiation | **Approved** — Project Charter 1.0.1 |
| 1 | Product definition | **Approved** — PRD 1.0.4; MVP acceptance remains unchecked |
| 2 | Requirements | **Approved** — SRS 1.4.0 and traceability 1.5.0; LEAD-001 is content/evidence drift |
| 3 | Architecture | **Approved** — architecture docs; ADR-001–006 and 008–010 Accepted; ADR-007 Draft/Proposed and non-binding |
| 4 | Detailed design | **Approved** — DB/API/ML/error design and model card |
| 5 | Implementation planning | **Approved** — implementation plan 1.0.2 |
| 6 | Implementation | Code present; IMP-001…012 marked Done, but code-review and remote-CI DoD boxes remain open. This is not an “Approved” release gate. |
| 7 | Verification | Test strategy and plan **Approved**; local run: **63 passed, 5 skipped**. Live Postgres cases were skipped locally; remote CI is not claimed. LEAD-001 prevents treating local-demo verification as complete. |
| 8 | Release | **Draft** — release process and notes template Draft; no release attestation |
| 9 | Operations | **Draft** — observability, logging, and incident response Draft |

## Required independent checks

| Check | Result | Evidence |
|---|---|---|
| CR-001 registered and Accepted | **Pass** | `docs/00-meta/id-registry.md`; `docs/11-change-management/CR-001-mvp-team-stats-not-players.md` |
| SRS FR-001 has no fetch-players Must | **Pass** | FR-001 explicitly makes player fetch/persist out of MVP |
| Load path does not write players | **Pass** | `src/athletiq/provider/base.py`, `src/athletiq/load/__init__.py`, `src/athletiq/load/postgres.py` |
| Independent traceability columns | **Pass** | Requirement / Implementation / Verification are distinct with separate evidence rules |
| `schema.sql` has `schema_migrations` | **Pass** | `database/schema.sql` |
| OpenAPI has `security: []` | **Pass** | `api/openapi.yaml` |
| Docs index avoids Compose/CI “stub” wording | **Pass** | `docs/README.md` calls them MVP topology/workflow |
| SRS Gate-4 questions closed | **Pass** | formulas, validation, raw layout, ML threshold, and CR-001 are Resolved |
| TEST-005 labeled in-memory/unit | **Pass** | `docs/08-testing/test-plan.md`; traceability says Passing (in-memory) |

## Design / contract / implementation drift

### Database

| Concern | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| MVP entity load | teams, games, `team_game_stats`; player tables reserved | Reserved comments and all tables present | Provider/load writes only MVP themes | **Aligned — CR-001 held** |
| Identity | BIGINT/BIGSERIAL | BIGSERIAL PKs and BIGINT FKs | Postgres stores and API decimal strings agree | **Aligned** |
| Migration bookkeeping | `schema_migrations` in consolidated snapshot | Table present | Migration creates table and records `001_initial` | **Aligned**; snapshot need not contain runtime row |
| Feature payload | Envelope `{values, label_home_win, used_cold_start_*}` with legacy read | JSONB contract/comment | Postgres feature store writes/reads envelope | **Aligned** |
| Local persistence path | Curated PostgreSQL for demo | Compose has PostgreSQL and volumes | Pipeline supports Postgres only when `--store postgres`; documented direct ETL command defaults memory | **Drift — LEAD-001** |

### API

| Concern | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Routes and errors | health/predict/model; distinct 404/503 codes | Same endpoints and error enum | Routes/state match | **Aligned** |
| Authentication | No auth; localhost only | `security: []`, empty schemes | No auth middleware; Compose binds `127.0.0.1` | **Aligned; ADR-009 held** |
| Prediction key | `game_id`; optional resolver language includes matchup | `game_id` or `provider_game_id` | Same as contract | **Minor architecture drift — LEAD-003** |
| Artifact/feature compatibility | Pinned model + `(game_id, feature_version)` | Lineage fields required | Shared preprocessing and composite lookup | **Aligned** |

### ML

| Concern | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Features | Team L5/L10 + season WR; no player features | Feature version/pin metadata | Shared feature builder/preprocessor | **Aligned** |
| Split/selection | Temporal ~70/15/15; select on validation; tie to LR | Pin + lineage JSON | `temporal_split`, `select_model`, publish pin | **Aligned** |
| Test/quality claim | ML-005 requires real frozen holdout attestation | Eval metadata path | Synthetic TEST-007 only; traceability says Partial / Passing (synthetic) | **Honest, not MVP-complete** |
| Reproducibility | Same raw+code+config+seed within tolerance | NFR-001 clean-environment bar | TEST-013 repeats synthetic feature/train functions only | **Evidence drift — LEAD-001** |

## Accepted ADR consequences

| ADR | Consequences present? | Follow-through | Verdict |
|---|---|---|---|
| ADR-001 PostgreSQL 16 | Yes | Postgres 16 in Compose; PostgreSQL schema/migrations | **Held** |
| ADR-002 API-Sports adapter | Yes | Env key, adapter boundary, fixture provider; team/game surface matches CR-001 | **Held** |
| ADR-003 validation select / test report / pin | Yes | Validation-only selection, tie to LR, test metrics after selection, pin-only API | **Held**; real ML-005 attestation remains honestly Partial |
| ADR-004 shared local artifacts | Yes | ETL/API mount same Compose volume; pin/joblib/JSON implementation | **Held in topology**; end-to-end use unverified (LEAD-001) |
| ADR-005 batch + Python orchestrator | Yes | Thin bash and Python stages | **Partially held**; restart/resume claim exceeds implementation (LEAD-002) |
| ADR-006 immutable raw filesystem | Yes | Batch paths, no raw DB tables, raw Compose volume | **Held** |
| ADR-008 game/feature contract | Yes | Composite feature lookup and shared preprocessing | **Held**; optional matchup prose is stale |
| ADR-009 no-auth local API | Yes | No middleware, localhost Compose bind, OpenAPI empty security | **Held** |
| ADR-010 BIGINT keys | Yes | Design, schema, migration, API string handling | **Held** |

ADR-007 is Draft/Proposed, not Accepted; it was checked only to confirm that GCP remains non-binding.

## Prior-finding disposition

| Prior finding | Independent disposition |
|---|---|
| Managing F-001 player pipeline mismatch | **Closed by Accepted CR-001**; no player ingest should be demanded |
| Managing F-002 traceability coupling/staleness | **Closed**; columns and evidence rules are independent |
| Managing F-003 stub language | **Closed** |
| Managing F-004 stale Gate-4 SRS questions | **Closed** |
| Managing F-005 schema snapshot/payload | **Closed** |
| Managing F-006 annotation hygiene | **Closed** for checked plan-listed artifacts/tests |
| Managing F-007 stale operations/packaging/registry prose | **Closed** for the cited contradictions |
| Managing F-008 OpenAPI security | **Closed** |
| Grok F-009 TEST-005 labeling | **Closed after Grok review**; SRS, test plan, and traceability now explicitly say in-memory/unit |
| Grok “no 9/10 blocker” conclusion | **Reopened as LEAD-001** on different evidence: clean-environment and Compose end-to-end claims remain overstated |

## What is sound

- CR-001 propagation across PRD, SRS, architecture, database design/schema, implementation plan, tests, provider, and load code.
- Temporal leakage boundary, validation-only model selection, pin-only serving, and no silent baseline fallback.
- DB/API contracts: BIGINT identity, `schema_migrations`, feature envelope, explicit no-auth OpenAPI.
- Honest product-level incompleteness: PRD acceptance unchecked, DR-001 and ML-005 Partial, remote CI Deferred, Gates 8–9 Draft.
- CI workflow structure: lint and unit gate Postgres integration, then image builds; no live provider dependency.

## What not to do

- Do not add player ingest or player-level ML; CR-001 explicitly moved it out of MVP.
- Do not add GCP, public auth, MLOps, hard SLOs, or automated retraining to close this review.
- Do not relabel synthetic ML-005 as real NBA holdout evidence.
- Do not claim remote CI green, two live completed NBA seasons, Gate 8/9 completion, or MVP completion.
- Do not solve LEAD-001 by merely changing “Passing” prose while leaving an ambiguous demo command; either narrow the evidence claim honestly or add a real end-to-end attestation.

## Validation

- [x] Only this review artifact was authored
- [x] No Grill-Me
- [x] Every Accepted ADR checked for consequences
- [x] DB/API/ML design-contract-implementation triples checked
- [x] Prior findings independently re-verified
- [x] Local test run observed: 63 passed, 5 skipped; no remote-CI claim

**Final score: 8 / 10**
