# Implementation plan

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.2

> Bridge from Approved design (Gate 4) to code. Annotation scope for `# Implements: FR-XXX` is exactly the **Files/modules affected** lists below.  
> **Gate 5 Approved.** **Gate 7 test strategy v1.0.0 + test plan v1.0.1 Approved** — Gate 6 coding may proceed (`gates.md` §22).

## Upstream

| Artifact | Status |
|---|---|
| Charter 1.0.1, PRD 1.0.4, SRS v1.4.0, traceability 1.5.0 | Approved (CR-001) |
| Architecture + ADRs 001–006, 008, 009, **010** | Approved / Accepted |
| Design: ML / DB / API / errors + contracts | Approved (DB design **v1.0.2** cites ADR-010 + CR-001) |
| Test strategy / test plan | **Approved** (strategy v1.0.0; plan **v1.0.1**) — Gate 6 coding allowed (§22) |
| ADR-007 GCP | Proposed / non-binding — **out of MVP scope** |

## Deliberate skips (not IMP-scoped)

### Out of scope for MVP

- Post-MVP product: NumPy NN, score/spread, second league, UI, player-level features, automated retrain, drift dashboards  
- Public auth / internet-safe bind (MVP keeps ADR-009 no-auth demo)  
- Cloud deploy / GCP (ADR-007 Proposed only)

### Explicitly prohibited or not required by design

These are **not** “cut requirements.” IMP tasks **satisfy** the NFR by obeying it; the forbidden/non-required *pattern* is what we never build.

| Rule | Meaning | Satisfied by |
|---|---|---|
| **NFR-003** | CI must **not** call live API-Sports | IMP-011 + fixtures (TEST-003/011) |
| **NFR-004** | No hard latency/availability SLOs in MVP; **no** SLO-enforcing load/perf suite | IMP-008 docs “no hard SLO”; **verified** by TEST-008 (OpenAPI/design cite check) — see `docs/08-testing/test-strategy.md` (falsifiable “no SLO promised”); load tests stay out |

## Proposed repo layout (annotation roots)

```text
src/athletiq/           # shared + batch pipeline package
  config/
  logging/
  db/
  provider/             # API-Sports adapter
  ingest/
  validate/
  load/
  analytics/
  features/             # single train/serve feature builder (ML-008)
  ml/                   # baselines, train, select, eval, publish
  pipeline/             # CLI stage runner
api/                    # FastAPI app (alongside openapi.yaml)
  app/
database/
  schema.sql
  migrations/
scripts/run_pipeline.sh
tests/
  unit/
  integration/
  fixtures/             # recorded provider payloads (no live API in CI)
.github/workflows/
docker-compose.yml
```

Packaging: **hatchling + pip / `pyproject.toml`** (IMP-001 Done). `uv` is optional, not required.

## Sequence overview

```text
IMP-001 bootstrap
  → IMP-002 DB  ∥  IMP-003 ingest   (parallel: curated schema vs raw filesystem)
        ↘___________↙
              → IMP-004 validate/load → IMP-005 analytics
                                      → IMP-006 features
  → IMP-007 ML train/select/publish (depends IMP-006)
  → IMP-008 API (feature path IMP-006; stub artifacts until IMP-007)
  → IMP-009 orchestration (can stub stages early)
  → IMP-010 Compose
  → IMP-011 CI
  → IMP-012 methodology (after IMP-007 + IMP-008)
```

**Parallelism:** After IMP-001, **IMP-002 ∥ IMP-003** (raw ingest is filesystem-only per ADR-006 / database-design — no Postgres dependency). After IMP-004: **IMP-005 ∥ IMP-006**. API (IMP-008) may stub artifact load until IMP-007 lands.

## Requirement coverage (Must)

> **Canonical mapping:** `docs/03-requirements/traceability.md`. This table is a reading aid only — if they disagree, **traceability wins**.

| Requirement | Primary IMP | Notes |
|---|---|---|
| FR-001, CON-007, DR-001 (ingest window) | IMP-003 | |
| FR-002, DR-002, DR-003 | IMP-004 | Schema contract also IMP-002; **CR-001** team-level MVP load |
| FR-013 | IMP-004 | |
| FR-003 | IMP-005 | |
| FR-004, ML-001, ML-002, ML-008 | IMP-006 | |
| FR-005…008, ML-003…007, ML-009, CON-008, ADR-003/005 | IMP-007 | |
| FR-009, FR-014, CON-004, ADR-008/009, NFR-002 | IMP-008 | |
| NFR-004 | IMP-008 | Target documented (no invented SLOs); **not** load-tested — see Deliberate Skips |
| FR-010 | IMP-012 (+ `/v1/model` in IMP-008) | |
| FR-011, CON-001, CON-006, OPS-002 | IMP-009 | |
| FR-012, CON-003, ADR-001/004/006 | IMP-010 | |
| OPS-001, CON-005, NFR-003 | IMP-011 | NFR-003 satisfied by **excluding** live provider from CI |
| SEC-001, SEC-002, NFR-001 | IMP-001 (+ secrets checks IMP-011) | |
| NFR-005 | IMP-002 | |
| CON-002 | IMP-002 | |

---

## Tasks

### IMP-001 — Project bootstrap, config, logging, secrets

- **Requirement IDs:** SEC-001, SEC-002, NFR-001, OPS-002, CON-001  
- **Architecture references:** system-architecture.md §7 trust; §2 deployment  
- **Design references:** error-handling.md (never log secrets)  
- **Dependencies:** none  
- **Files/modules affected:**
  - `pyproject.toml`
  - `src/athletiq/__init__.py`
  - `src/athletiq/config/`
  - `src/athletiq/logging/`
  - `.env.example`
  - `.gitignore` (secrets, `data/raw/`, `artifacts/`, `.venv/`)
- **Implementation sequence notes:** Env-only secrets (API key, DB URL); structured logging helper used by all stages; seed/config for reproducibility (NFR-001). No application business logic.  
- **Testing requirements:** TEST-001, TEST-013  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (full workflow = IMP-011; local TEST-001 green)  
- **Status:** Done

### IMP-002 — Database schema and migrations

- **Requirement IDs:** FR-002 (persistence contract), DR-002, DR-003, NFR-005, CON-002, ADR-001, ADR-010  
- **Architecture references:** data-architecture.md; system-architecture.md  
- **Design references:** database-design.md; `database/schema.sql`  
- **Dependencies:** IMP-001  
- **Files/modules affected:**
  - `database/schema.sql`
  - `database/migrations/`
  - `src/athletiq/db/`
- **Implementation sequence notes:** Forward-only migrations; **BIGINT** ids (**ADR-010**); indexes per NFR-005; curated-only (no `raw_*` tables). Apply path used by pipeline and local Compose. **May run in parallel with IMP-003** after IMP-001.  
- **Testing requirements:** TEST-002  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (full workflow = IMP-011; contract tests green; live migrate skips without Postgres)  
- **Status:** Done

### IMP-003 — Provider adapter and raw ingest

- **Requirement IDs:** FR-001, CON-007, DR-001, SEC-001, ADR-002, ADR-006  
- **Architecture references:** data-architecture.md (raw zone); system-architecture.md §2–3  
- **Design references:** ml-design.md (active history / prune too-old); error-handling.md (retries)  
- **Dependencies:** IMP-001  
- **Files/modules affected:**
  - `src/athletiq/provider/`
  - `src/athletiq/ingest/`
  - `tests/fixtures/provider/`
- **Implementation sequence notes:** API-Sports adapter behind interface; immutable raw JSON to volume (`teams.json`, `games_{season}.json`, `manifest.json`); exponential backoff + jitter, max 5, honor `Retry-After`; season window 2 Must / ≤3 Should; record fixtures for CI (no live calls in tests). **CR-001:** adapter fetches teams + games (team stats derived at load); no `players.json`. **Independent of IMP-002** (raw is filesystem, not Postgres) — may run in parallel after IMP-001.  
- **Testing requirements:** TEST-003  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (full workflow = IMP-011; unit TEST-003 green)  
- **Status:** Done

### IMP-004 — Validate, transform/load, validation report

- **Requirement IDs:** FR-002, FR-013, DR-002, DR-003, OPS-002  
- **Architecture references:** data-architecture.md (validation boundary); system-architecture.md §8  
- **Design references:** database-design.md; error-handling.md (skip vs fail); ml-design.md (prune)  
- **Dependencies:** IMP-002, IMP-003  
- **Files/modules affected:**
  - `src/athletiq/validate/`
  - `src/athletiq/load/`
  - `src/athletiq/prune/` (or under `load/`)
- **Implementation sequence notes:** Skip noisy + report; dedupe by provider natural key; fail if zero teams or zero games for a required season; idempotent upserts for **teams / games / team_game_stats** (**CR-001** — no player upserts); prune too-old outside active window (`seasons_to_prune` is a helper; ingest already skips out-of-window seasons).  
- **Testing requirements:** TEST-004  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (full workflow = IMP-011; TEST-004 green on in-memory store)  
- **Status:** Done

### IMP-005 — SQL analytics

- **Requirement IDs:** FR-003, NFR-005  
- **Architecture references:** data-architecture.md  
- **Design references:** database-design.md (analytics examples)  
- **Dependencies:** IMP-004  
- **Files/modules affected:**
  - `src/athletiq/analytics/`
- **Implementation sequence notes:** Aggregations + window functions over curated **team** tables (rolling windows ordered by `game_start_time`). Top-scorer helpers are **not** a pipeline load outcome (**CR-001**). Read-only analytics helpers/scripts; not a separate service.  
- **Testing requirements:** TEST-005  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-005 green)  
- **Status:** Done

### IMP-006 — Feature engineering

- **Requirement IDs:** FR-004, ML-001, ML-002, ML-008, ADR-008  
- **Architecture references:** system-architecture.md §4 inference feature contract  
- **Design references:** ml-design.md (L5/L10, season WR, `min_prior_games = 5`)  
- **Dependencies:** IMP-004  
- **Files/modules affected:**
  - `src/athletiq/features/`
- **Implementation sequence notes:** Single module for training and API preprocessing; persist `(game_id, feature_version)`; cold start → season-to-date; no post-tip leakage; team-level only.  
- **Testing requirements:** TEST-006  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-006 green)  
- **Status:** Done

### IMP-007 — ML train / select / publish

- **Requirement IDs:** FR-005, FR-006, FR-007, FR-008, ML-003, ML-004, ML-005, ML-006, ML-007, ML-009, CON-008, NFR-001, ADR-003, ADR-004, ADR-005  
- **Architecture references:** system-architecture.md §3, §5; ADR-003/004/005  
- **Design references:** ml-design.md; error-handling.md (quality gate vs execution failure)  
- **Dependencies:** IMP-006  
- **Files/modules affected:**
  - `src/athletiq/ml/`
  - artifact writers under configured artifacts path (runtime; not committed binaries)
- **Implementation sequence notes:** Temporal ~70/15/15; baselines never served; select on validation log loss (tie → LR); test set once for ML-005; joblib + JSON lineage; pin at batch time; XGBoost defaults recorded in `training_config`. Quality-gate miss may exit 0 with failed report (design).  
- **Testing requirements:** TEST-007, TEST-013, TEST-014  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-007 green; TEST-013/014 with later IMPs)  
- **Status:** Done

### IMP-008 — FastAPI prediction service

- **Requirement IDs:** FR-009, FR-014, CON-004, NFR-002, NFR-004, ADR-008, ADR-009  
- **Architecture references:** api-architecture.md; system-architecture.md §4  
- **Design references:** api-design.md; error-handling.md; `api/openapi.yaml`  
- **Dependencies:** IMP-006 (feature read path); IMP-007 (published pin) for full DoD — can develop against fixtures first  
- **Files/modules affected:**
  - `api/app/`
  - `api/openapi.yaml` (keep contract aligned)
- **Implementation sequence notes:** `/v1/health`, `/v1/predict`, `/v1/model`; no auth; sync only; distinct error codes; no silent baseline fallback; load pin + features by `game_id` + pinned `feature_version`; reuse `src/athletiq/features` preprocessing. **NFR-004:** implement as demo-grade sync API with **no** hard latency/availability SLO and **no** requirement for load tests (see Deliberate Skips).  
- **Testing requirements:** TEST-008, TEST-014  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-008 green; TEST-014 with later IMPs)  
- **Status:** Done

### IMP-009 — Pipeline orchestration

- **Requirement IDs:** FR-011, CON-006, CON-001, OPS-002, ADR-005  
- **Architecture references:** system-architecture.md §2 (script → CLI → etl stages)  
- **Design references:** error-handling.md; ml-design.md (manual retrain)  
- **Dependencies:** IMP-003…IMP-007 (stages exist); can stub early  
- **Files/modules affected:**
  - `scripts/run_pipeline.sh`
  - `src/athletiq/pipeline/`
- **Implementation sequence notes:** Thin bash → Python CLI; `--from-stage` selection per ADR-005 (restart limits documented there); structured logs; non-zero on execution failure; operator-invoked only.  
- **Testing requirements:** TEST-009  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-009 green)  
- **Status:** Done

### IMP-010 — Docker Compose local deployment

- **Requirement IDs:** FR-012, CON-003, ADR-001, ADR-004, ADR-006  
- **Architecture references:** system-architecture.md §2  
- **Design references:** database-design.md; infrastructure intent docs  
- **Dependencies:** IMP-002, IMP-008, IMP-009 (images for etl + api)  
- **Files/modules affected:**
  - `docker-compose.yml`
  - `api/Dockerfile` (or repo-root Dockerfiles as chosen)
  - `Dockerfile.etl` (or equivalent)
- **Implementation sequence notes:** Services `database`, `etl`, `api`; volumes for raw JSON + artifacts; env-based credentials; runnable MVP topology (not a stub).  
- **Testing requirements:** TEST-010  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-010 green)  
- **Status:** Done

### IMP-011 — GitHub Actions CI

- **Requirement IDs:** OPS-001, CON-005, NFR-003, SEC-002  
- **Architecture references:** system-architecture.md §6  
- **Design references:** error-handling.md (CI ≠ live pipeline)  
- **Dependencies:** IMP-001; tests from prior IMPs; image defs from IMP-010  
- **Files/modules affected:**
  - `.github/workflows/ci.yml`
  - `tests/fixtures/` (used by workflow; no live provider)
- **Implementation sequence notes:** lint → unit → integration (ephemeral DB) → image build; **no** live API-Sports (**NFR-003** satisfied by prohibition + fixtures); secrets only via GHA secrets if needed (none required for fixture path).  
- **Testing requirements:** TEST-011  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (workflow defined; green on remote when pushed)  
- **Status:** Done

### IMP-012 — Methodology and limitations disclosure

- **Requirement IDs:** FR-010  
- **Architecture references:** system-architecture.md §5 lineage  
- **Design references:** ml-design.md; api-design.md (`/v1/model`)  
- **Dependencies:** IMP-007, IMP-008  
- **Files/modules affected:**
  - `docs/12-releases/` or `docs/06-design/` model card / methodology note (path chosen at impl; prefer `docs/06-design/model-card.md` or `docs/12-releases/methodology.md`)
  - `api/app/` model metadata payload (keep aligned with FR-010 text)
- **Implementation sequence notes:** Document features, splits, baselines, selection rule, limitations, and that baselines are never served; expose summary via `/v1/model`. Starts only after **both** IMP-007 (lineage/metrics) and IMP-008 (`/v1/model` surface).  
- **Testing requirements:** TEST-012  
- **Definition of Done:**
  - [x] Requirements satisfied  
  - [x] Design satisfied  
  - [x] Tests implemented and passing  
  - [x] Logging/observability addressed  
  - [x] Error handling addressed  
  - [x] Documentation updated  
  - [x] Traceability matrix + code annotations updated  
  - [ ] Code review passed  
  - [ ] CI passed (IMP-011; TEST-012 green)  
- **Status:** Done

---

## Open (non-blocking)

- Exact XGBoost hyperparameters → defaults at IMP-007; record in lineage  
- Exact season date-cut row counts → after first real ingest; store in `dataset_version`  

## Post-MVP backlog (not minted)

NumPy NN; score/spread; second league; UI; GCP when Gate 8 designed.
