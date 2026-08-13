# Managing-architect review — AthletIQ living docs & drift

Status: Complete  
Date: 2026-08-13  
Reviewer role: Managing architect (read-only `engineering-review`)  
Scope: `docs/` + design/contract/implementation triple + `# Implements` vs Implementation Plan  
Must not: Grill-Me; primary Charter/PRD/SRS/architecture/ADR/design/impl/test edits

---

## Executive verdict

AthletIQ’s **architecture is coherent and shippable as a demo spine**: temporal no-leakage invariants, batch training + pin, `game_id` + `(game_id, feature_version)`, BIGINT ids, explicit no-auth, fixture CI, and error codes that match OpenAPI. What is **not** good enough to hand a reviewer as “MVP complete” is the **honesty layer**. Gate 0–5 and Gate 7 test *docs* are Approved; IMP-001…012 are marked Done; local tests are Passing — but the **Approved traceability matrix still says Planned for most Musts**, the **docs index still calls Compose/CI stubs**, the **SRS still has TBD pointers and Gate-4 questions as if design never landed**, and **two of five DR-002 entity themes (`players`, `player_game_stats`) exist only as empty tables**. Predictions can work on team-level fixtures. A reviewer who traces FR-002 / FR-003 / FR-001 from SRS → schema → load → fixtures will correctly call the player/analytics path **schema theater**. Do not publish as complete; do not start GCP/auth/NN. Close honesty + the player data path (implement or CR) before claiming the PRD bar.

**Score: 7 / 10** — architecture and binding ADRs are good enough to keep; documentation currency and DR-002 completeness are what would bite.

No **blocker** for *continuing local work*. Two items **block publish-bar / MVP-complete honesty** (F-001, F-002) until resolved.

---

## Gate snapshot

A gate is satisfied only when required artifacts are **Approved**. “Done code” ≠ Gate 8/9. Traceability **Status** is not treated as implementation evidence (see F-002).

| Gate | Phase | Artifacts | Status |
|---|---|---|---|
| 0 | Project initiation | `docs/01-project/project-charter.md` | **Approved** 1.0.0 |
| 1 | Product definition | `docs/02-product/PRD.md` | **Approved** 1.0.3 |
| 2 | Requirements | `docs/03-requirements/SRS.md`, `traceability.md` | **Approved** (SRS 1.3.0; traceability 1.4.0 — **content stale**, F-002) |
| 3 | Architecture | `docs/04-architecture/*`, binding ADRs | **Approved**; ADR-001–006, 008, 009, 010 **Accepted**; ADR-007 **Proposed / non-binding** |
| 4 | Detailed design | DB / API / ML / errors + model card | **Approved** (DB 1.0.1; others 1.0.0) |
| 5 | Implementation planning | `docs/07-implementation/implementation-plan.md` | **Approved** 1.0.1; IMP-001…012 **Done** (code-review + remote CI DoD boxes still open — honest) |
| 6 | Implementation | Code + `# Implements` on listed modules | **Code exists**; annotation hygiene imperfect (F-006); player load missing (F-001) |
| 7 | Verification | Test strategy/plan + execution | **Docs Approved** 1.0.0; TEST-001…014 **Passing locally**; **remote GHA green deferred** (test-plan Open) |
| 8 | Release | `docs/12-releases/*` | **Draft** / missing real release notes — expected |
| 9 | Operations | `docs/10-operations/*`, change process | **Draft**; several Open Questions leftover or contradictory (F-007) |

PRD MVP acceptance checklist (`PRD.md` §MVP acceptance) is **entirely unchecked**. That is the correct product-level signal: **do not treat IMP Done as MVP complete**.

---

## Findings

| ID | Severity | Area | Evidence | Owning skill | Recommended action |
|---|---|---|---|---|---|
| F-001 | **major** (blocks **publish-bar / MVP-complete**) | DR-002 / FR-001 / FR-002 / FR-003 data path | SRS FR-002, DR-002, FR-001 AC (fetch **players**); PRD “persist players … player/team statistics”; `database/schema.sql` tables `players`, `player_game_stats`; **no** `fetch_players` / `players.json` / `upsert_player*` anywhere under `src/`; `ProviderClient` is teams+games only (`src/athletiq/provider/base.py`); load writes teams/games/`team_game_stats` only (`src/athletiq/load/__init__.py`); fixtures: `tests/fixtures/provider/{teams,games_*.json}` only; TEST-005 executes **in-memory Python clones**, never SQL against loaded rows (`tests/unit/test_analytics.py`); TEST-004 plan lists `player_game_stats` grain — test does not (`docs/08-testing/test-plan.md` vs `tests/unit/test_load_validate.py`) | `requirements` (if demoting) **or** implementation (if keeping Must) + `testing` | Either **implement** provider→raw→curated player stats (and tests that load then query), **or** mint a **CR** that demotes player persistence from MVP Must and amends PRD/SRS/schema/analytics. Do not leave tables as decoration. |
| F-002 | **major** (honesty / traceability invariant) | Traceability columns | `docs/03-requirements/traceability.md` v1.4.0: single **Status** column; most Musts still **Planned** while IMP-001…012 are **Done**; several rows set Implemented **because a test is Passing** (e.g. FR-009 “Implemented (TEST-008)”, SEC-001 “Implemented (TEST-001)”) — violates independent requirement / implementation / verification columns. Notes still say “Planned = mapped, not implemented.” SRS body still has **Architecture refs / Design refs / Tests: TBD** on nearly every requirement (`docs/03-requirements/SRS.md`). ID registry ML-003 title still “Shared temporal holdout (~20%)” (`docs/00-meta/id-registry.md`) vs ML-003 three-way split. | `requirements` | Split Status into **requirement / implementation / verification**. Update implementation **only** from IMP/code evidence; verification **only** from TEST evidence. Fill or delete SRS TBD pointers. Fix ML-003 registry title. |
| F-003 | **major** (stale stub / reviewer trap) | Docs index vs shipped topology | `docs/README.md` (Last Updated 2026-08-12): `docker-compose.yml` = “Local multi-container topology **stub**”; `.github/workflows/` = “CI/CD workflow **stubs**”. Reality: runnable Compose (`docker-compose.yml`: `database` / `etl` / `api`, volumes, localhost bind) and `.github/workflows/ci.yml` (lint ∥ unit → integration → image). Root `README.md` already describes real contracts. `docs/09-devops/ci-cd.md` still narrates “replaces `ci-stub.yml`”. | `devops-operations` (index + devops prose); meta index | Strike “stub”. Call compose/CI **MVP topology / workflow**. Bump `docs/README.md` Last Updated. |
| F-004 | **major** | SRS Open Questions that Gate 4 already closed | `docs/03-requirements/SRS.md` §Open questions remaining still lists “Feature formulas / season cut points”, “Validation invalid-record policy”, “Raw directory layout / retention” as Gate 4 work. Those are **decided** in `docs/06-design/ml-design.md` (L5/L10, `min_prior_games=5`, ~70/15/15), `error-handling.md` (skip+count; fail on zero teams/games), `ADR-006` + ingest layout (`teams.json`, `games_{season}.json`, `manifest.json`). PRD still has `[OPEN QUESTION: numeric ML success thresholds not set]` while **ML-005** is the relative bar (test log loss &lt; domain-informed). | `requirements` + `project-discovery` (PRD OQ only) | Close or retarget those OQs as **resolved (see design/ML-005)**. Leave only true leftovers (free-tier vs DR-001 assumption; Gate 8 deploy). |
| F-005 | **minor** | DB contract vs migrations | Design: `schema.sql` is the **consolidated snapshot** (`docs/06-design/database-design.md`). `database/migrations/001_initial.sql` adds `schema_migrations` + insert; `database/schema.sql` has **neither**. Apply path is migrations (`src/athletiq/db/migrate.py`, Compose initdb). A reviewer diffing contract vs migrate will see a missing table. Feature **payload** JSONB envelope (`values`, `label_home_win`, cold-start flags in `src/athletiq/features/postgres.py`) is **not** specified in database-design — only “payload JSONB”. | `architecture` / design owner (`database-design`) + keep contract in sync | Add `schema_migrations` to `schema.sql` **or** document it as migrate-only bookkeeping. Document payload envelope in database-design (one paragraph). |
| F-006 | **minor** | `# Implements` vs plan | Rule: annotations **only** on Implementation Plan **Files/modules affected** (`docs/00-meta/documentation-guide.md`, `implementation-plan.md`). **Extra:** almost every file under `tests/unit/` and `tests/integration/` has `# Implements`. **Missing** on listed artifacts: `pyproject.toml`, `database/schema.sql`, `database/migrations/001_initial.sql`, `api/openapi.yaml`, `docs/06-design/model-card.md`, `tests/fixtures/provider/`. Listed Dockerfiles **do** have annotations. | `implementation-planning` (rule reminder) — do not spray IDs onto tests | Remove Implements from tests (TEST ids belong in test-plan). Add annotations only on the listed missing files if you still want the reverse index complete. |
| F-007 | **minor** | Stale / contradictory Open Questions | `docs/10-operations/observability.md`: `[OPEN QUESTION: metrics backend and SLOs]` — **contradicts Approved NFR-004** (no hard SLOs). `docs/10-operations/logging.md` still open on format while IMP-001 logging exists (`src/athletiq/logging/__init__.py`). Implementation plan still “Open: uv vs Poetry — decide at IMP-001 start” after IMP-001 **Done** (`pyproject.toml` is hatchling/pip). `docs/00-meta/documentation-guide.md` ML contract still “model registry entry **(TBD)**” — pin + joblib + JSON is the contract (ADR-003/004). | `devops-operations`; `implementation-planning`; meta guide | Close SLO OQ citing NFR-004. Mark logging/format as leftover Gate 9 or document current formatter. Delete packaging OQ. Replace “TBD registry” with pin/metadata path. |
| F-008 | **nit** | ADR-009 OpenAPI wording | ADR-009 consequence: “OpenAPI documents security as empty / none.” `api/openapi.yaml` has **no** `security` / `securitySchemes` (implicit none). FastAPI app also has no auth middleware (`api/app/main.py`). Functionally aligned; a pedantic reviewer will want `security: []`. | `architecture-decisions` flag only; API design/contract if you tighten | Add explicit empty security to OpenAPI when next touching the contract. Not a behavior bug. |

Nits not table-worthy: Charter example `./run_pipeline.sh` vs actual `scripts/run_pipeline.sh` (SRS allows equivalent); architecture `Last Updated` 2026-08-12 while ADR-010 is cited in the ADR index; glossary missing “selection pin” / “cold start”; `seasons_to_prune` never called from pipeline (ingest already skips out-of-window seasons — curated prune is a helper only).

---

## Drift defects (design vs contract vs code)

### Database

| Claim | Design | Contract | Implementation |
|---|---|---|---|
| Engine / ids | PostgreSQL; BIGINT/BIGSERIAL (ADR-010); `docs/06-design/database-design.md` | `database/schema.sql` BIGSERIAL PKs; no UUID | Migrations + TEST-002 agree. **Aligned.** |
| Entity themes | teams, players, games, player/team stats, features, optional `model_registry` | All tables present | **Load/API path never writes `players` / `player_game_stats`.** Analytics SQL would return empty after a real pipeline run. **Defect (F-001).** |
| Indexes (NFR-005) | Listed six indexes | Same names in `schema.sql` | Migrations match. **Aligned.** |
| Idempotent grain | DR-003; natural `provider_*` | UNIQUE on provider ids; PKs on stats/features | Postgres upserts on those keys (`src/athletiq/load/postgres.py`). **Team path aligned; player grain untested because unloaded.** |
| Snapshot completeness | `schema.sql` = consolidated snapshot | Missing `schema_migrations` | Present only in `001_initial.sql`. **Defect (F-005).** |
| Feature payload | Unspecified JSONB | `payload JSONB` | Envelope `{values, label_home_win, used_cold_start_*}` in `features/postgres.py`. Compatible with thin design; **underspecified** for a future implementer. |
| `model_registry` | Optional mirror; files canonical | Table exists | Publish writes **files only** (`src/athletiq/ml/publish.py`). Allowed. Do not treat the table as live lineage. |

### API

| Claim | Design | Contract | Implementation |
|---|---|---|---|
| Routes | `/v1/health`, `/v1/predict`, `/v1/model` | Same in `api/openapi.yaml` | `api/app/routes.py`. **Aligned.** |
| Auth | None (ADR-009); localhost/Compose | No security schemes | No middleware. **Aligned** (explicit `security: []` missing — F-008). |
| Predict key | `game_id` string of BIGINT; optional `provider_game_id` | Both query params optional | 400 if both missing; int parse; resolver. **Aligned.** Matchup home/away/date resolver mentioned in architecture is **not** in api-design/OpenAPI — design refined to provider id; architecture prose is slightly ahead. Not a code bug. |
| Errors | Distinct `game_not_found` vs `features_not_found`; 503 `model_unavailable` / `db_unavailable`; no silent baseline | Enum matches | `api/app/errors.py` + `state.py`. **Aligned.** |
| Lineage | `model_version`, `feature_version`; card via `/v1/model` | Required fields on PredictionResponse / ModelInfo | Pin-loaded; `methodology.py` matches model card. **Aligned.** |
| Threshold | `home_win_pred` = `p >= 0.5` | boolean | Same. **Aligned.** |

### ML

| Claim | Design + model card | Contract | Implementation |
|---|---|---|---|
| Feature version | `team_l5_l10_v1`; L5/L10 + season WR; `min_prior_games=5` | Pin JSON + `FEATURE_VERSION` | `src/athletiq/features/builder.py`. **Aligned.** |
| Splits | Temporal ~70/15/15; no shuffle | Lineage `dataset_version` | `src/athletiq/ml/splits.py`. **Aligned.** |
| Selection | Val log loss; tie → LR; baselines never served | Pin at batch time | `select.py` + `publish.py`; API loads pin only. **Aligned.** |
| Artifacts | joblib + JSON; ML-009 fields | Files under artifacts volume (ADR-004); **not** a TBD MLflow registry | `ModelMetadata` includes required fields; pin has `artifact` path. **Aligned.** Guide still says registry TBD (F-007). |
| ML-005 | Test log loss &lt; domain-informed | Eval report / attestation | TEST-007 **Passing (synthetic)**. Not an attested NBA holdout. **Do not claim MVP-complete ML quality.** |

---

## ADR consequences check (Accepted only)

| ADR | Consequences present? | Observed follow-through | Verdict |
|---|---|---|---|
| **001** PostgreSQL 16 | Yes | Compose `postgres:16`; dialect in schema/migrations | **Held** |
| **002** API-Sports + adapter | Yes | `ApiSportsProvider` + `FixtureProvider`; key via env | **Held**; adapter surface omits players (F-001) |
| **003** Val select / test once / pin | Yes | `select.py`, train pipeline, API pin load; baselines not served | **Held** |
| **004** Local artifacts volume | Yes | Compose `artifacts` on etl+api; gitignore intent in IMP-001 | **Held** |
| **005** Thin bash → Python orchestrator | Yes | `scripts/run_pipeline.sh` execs `python -m athletiq.pipeline` | **Held** |
| **006** Immutable raw JSON FS; prune too-old | Yes | Ingest refuses overwrite; new batch id; skip out-of-window seasons | **Mostly held**; curated prune helper unused (nit) |
| **007** GCP | Proposed only | Correctly omitted from binding index | **Non-binding — ignore for MVP** |
| **008** `game_id` + precomputed features | Yes | Predict lookup `(game_id, feature_version)`; shared `preprocess_for_model` | **Held** |
| **009** No auth; local bind | Yes | Compose `127.0.0.1:8000`; no auth middleware; docs warn public bind | **Held** (OpenAPI implicit — F-008) |
| **010** BIGINT not UUID | Yes | schema, migrations, OpenAPI decimal string, TEST-002 | **Held** |

---

## Architecture review gate (§21)

| Lens | Judgment |
|---|---|
| Requirements coverage | Must set is **architected**. Player **persistence** is specified and schematized, not implemented (F-001). |
| Component boundaries | Clear: adapter / raw FS / curated PG / shared features / batch ML / sync API. Protocols for store/repos are the right seam (`ATHLETIQ_STORE` / `--store`). |
| Data flow | Documented and implemented for **team-level** ingest→features→train→pin→predict. Player stats are a dead-end table. |
| Failure modes | Execution vs quality-gate vs validation skip is real in design and mostly in code. Missing pin → 503, not baseline. Good. |
| Scalability | Explicitly single-node; no Kafka/MLflow/K8s. Correct for MVP. |
| Security | ADR-009 is an **exposure decision**, not an omission. Secrets via env; CI has no live key. Public bind without a CR would be a defect — none found in Compose. |
| Maintainability | Binding ADRs + contracts are the maintainable core. SRS TBD + stale traceability will **rot the map**. |
| Observability | `/v1/health` + structured logs with redaction. Gate 9 docs are Draft and should not invent SLOs (F-007). |
| Testing implications | NFR-003 fixtures are real. TEST-013/014 exist. FR-003/DR-002 are **under-verified** (F-001). ML-005 is synthetic attestation. |
| Operational implications | Manual retrain via pipeline; etl image `sleep infinity` + `compose run` is documented. Remote CI green not claimed — keep it that way until it is true. |
| Technology decisions | Binding set is complete for MVP. ADR-007 must stay non-binding. |

---

## What is architecturally sound (keep)

- No-leakage / test-isolation / pin-only serving invariants (`docs/04-architecture/system-architecture.md`).
- Logical stages in **one etl image**, not fake microservices.
- ADR-008/010: BIGINT internally, decimal string on the wire.
- ADR-009 written down; Compose bound to localhost.
- Error taxonomy: `game_not_found` ≠ `features_not_found`; 503 for model/DB; no silent baseline.
- Train/serve shared `feature_version` + `preprocess_for_model`.
- Explicit `--store` / `ATHLETIQ_STORE`; `DATABASE_URL` is connection-only.
- CI DAG: lint ∥ unit → integration (ephemeral Postgres) → image; no live API-Sports.
- Charter vs PRD split is **mostly** respected (portfolio constraints in Charter; product in PRD). Do not re-merge them.
- IMP DoD leaving **code review** and **remote CI** unchecked is honest; copy that honesty into traceability.

---

## What not to do next (scope creep)

- Do **not** Accept ADR-007 or design GCP/CD.
- Do **not** add API keys/auth “because ADR-009 looks incomplete.”
- Do **not** add player-**level ML features**, NumPy NN, score/spread, UI, MLflow, drift dashboards, or automated retrain.
- Do **not** invent latency/availability SLOs (NFR-004).
- Do **not** silently rewrite Approved SRS/architecture to hide F-001 — either implement the Must or a **CR**.
- Do **not** mark traceability Implemented because pytest is green.
- Do **not** claim remote CI green or 2–3 live NBA seasons ingested.

---

## Recommended next 3 actions (priority)

1. **Honesty pass (cheap, unblocks reviewers)** — `requirements` + `devops-operations`: fix `docs/README.md` stub language; split/update `traceability.md` columns from IMP/code vs TEST evidence; close Gate-4-resolved SRS/PRD Open Questions; fix ML-003 registry title. No new product scope.
2. **Resolve F-001 before any publish-bar claim** — keep FR-002/DR-002 Must and implement player ingest/load/tests **or** CR to demote player stats and stop advertising top-scorer SQL as a pipeline outcome. Until then, IMP-004 “Requirements satisfied” is overstated.
3. **Publish-bar remainder (after 1–2)** — freeze a dataset/`feature_version` and run **ML-005 attestation** on it (not only synthetic TEST-007); ingest **2 completed seasons** under DR-001 (live or recorded); push and record **remote** GHA green; then tick PRD acceptance items that are actually true.

---

## Validation (this review)

- [x] No Grill-Me
- [x] No primary doc authorship (this file only)
- [x] Every Accepted ADR checked for consequences
- [x] Findings actionable and mapped to owning skills
