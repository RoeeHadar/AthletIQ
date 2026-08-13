# Grok re-review — AthletIQ living docs & drift (post CR-001 honesty pass)

Status: Complete  
Date: 2026-08-13  
Reviewer role: Engineering reviewer (read-only `engineering-review`)  
Baseline: `docs/00-meta/reviews/2026-08-13-managing-architect-docs.md` (7 / 10)  
Scope: `docs/` + design/contract/implementation triple + claimed F-001…F-008 closures  
Must not: Grill-Me; primary Charter/PRD/SRS/architecture/ADR/design/impl/test edits

---

## Executive verdict

The honesty pass landed. **CR-001 is Accepted, registered, and propagated**: MVP persist/ingest is teams / games / `team_game_stats`; `players` / `player_game_stats` are reserved schema, not a pipeline outcome. Traceability v1.5.0 now has independent Requirement / Implementation / Verification columns and does **not** set Implemented solely because a test passed. Gate-4 Open Questions in the SRS are closed to design / ML-005 / CR-001. Compose/CI are no longer called stubs. `schema_migrations` and the feature JSONB envelope are in the DB contract. `# Implements` is off tests and on the previously missing listed artifacts. OpenAPI has `security: []`. Load still does not write players — **intentionally**.

This is **not** MVP-complete and **must not** be published as such: PRD acceptance remains unchecked; DR-001 and ML-005 are **Partial** / synthetic; remote CI is **Deferred**; Gates 8–9 are Draft; IMP-001…012 Done is Gate 6 code, not Gate 8/9. Remaining disagreements are nits (TEST-005 grain vs FR-003 “persisted data” wording; architecture matchup prose ahead of OpenAPI). They do **not** reopen CR-001 completeness or the prior honesty blockers.

**Score: 9 / 10** — prior majors Closed; leftover items are unimportant. Not 10 / 10 because verification labeling on FR-003/TEST-005 is still a shade generous.

**≥9 / 10: yes.** No OPEN finding that would block 9 / 10.

---

## Gate snapshot

A gate is satisfied only when required artifacts are **Approved**. “Done code” ≠ Gate 8/9. Traceability Implementation is not treated as product-complete.

| Gate | Phase | Artifacts | Status |
|---|---|---|---|
| 0 | Project initiation | `docs/01-project/project-charter.md` | **Approved** 1.0.1 |
| 1 | Product definition | `docs/02-product/PRD.md` | **Approved** 1.0.4 (CR-001); MVP acceptance **unchecked** (correct) |
| 2 | Requirements | `docs/03-requirements/SRS.md`, `traceability.md` | **Approved** (SRS 1.4.0 + CR-001; traceability **1.5.0**) |
| 3 | Architecture | `docs/04-architecture/*`, binding ADRs | **Approved**; ADR-001–006, 008, 009, 010 **Accepted**; ADR-007 **Proposed / non-binding** |
| 4 | Detailed design | DB / API / ML / errors + model card | **Approved** (DB **1.0.2**; ML 1.0.1; API/errors 1.0.0; model card 1.0.0) |
| 5 | Implementation planning | `docs/07-implementation/implementation-plan.md` | **Approved** 1.0.2; IMP-001…012 **Done** (code-review + remote-CI DoD boxes still open — honest) |
| 6 | Implementation | Code + `# Implements` on listed modules | **Code exists**; annotation hygiene matches the plan (see F-006 Closed) |
| 7 | Verification | Test strategy/plan + execution | **Docs Approved** (strategy 1.0.0; plan **1.0.1**); TEST-001…014 **Passing locally**; **remote GHA green deferred** |
| 8 | Release | `docs/12-releases/*` | **Draft** — expected |
| 9 | Operations | `docs/10-operations/*`, change process | **Draft**; leftover OQs are Gate 8/9 (deploy host, correlation IDs), not contradictory SLOs |

**CR-001:** `docs/11-change-management/CR-001-mvp-team-stats-not-players.md` — document Status **Approved**, decision **Accepted**; registered in `docs/00-meta/id-registry.md`.

Do **not** treat IMP-001…012 Done as MVP-complete.

---

## Prior findings F-001…F-008

| ID | Claimed close | Disposition | Evidence (this pass) |
|---|---|---|---|
| **F-001** | CR-001 Accepted; MVP load = teams/games/`team_game_stats`; player tables reserved; no player ingest code | **Closed** | CR-001 registered. SRS FR-001 AC has **no** “fetch players” Must (player fetch/persist **out of MVP**). FR-002/DR-002 MVP themes = teams, games, team statistics; player themes Future/reserved. PRD persist row and analytics row match. `database/schema.sql` comments reserved tables. `ProviderClient` is `fetch_teams` / `fetch_games` only. Load upserts teams/games/`team_game_stats` only (`src/athletiq/load/__init__.py`, `postgres.py`). No `fetch_player` / `upsert_player` / `INSERT INTO players` under `src/`. Fixtures README: no `players.json`. TEST-004 grain excludes `player_game_stats` load. **Do not demand player ingest.** |
| **F-002** | Traceability v1.5.0 independent columns; SRS TBD filled; ML-003 title; IMP Done ≠ Gate 8/9; ML-005 synthetic; DR-001 Partial; remote CI Deferred | **Closed** | `traceability.md` v1.5.0: Requirement / Implementation / Verification with separate evidence rules. No “Implemented (TEST-00X)” coupling. DR-001 **Partial**; ML-005 **Partial** + Verification **Passing (synthetic)**; OPS-001/CON-005 **Deferred (remote CI)**. SRS Architecture/Design/Tests pointers filled (no TBD on Musts). ID registry ML-003 = “Temporal train / validation / test (~70/15/15)”. Notes state IMP Done is not Gate 8/9 / not PRD MVP-complete. |
| **F-003** | `docs/README.md` no longer calls Compose/CI stubs | **Closed** | Index v0.3.0 (2026-08-13): Compose = “Local multi-container **MVP topology**”; CI = “CI **MVP workflow**”. `docs/09-devops/ci-cd.md` v0.3.0: “MVP workflow; not a stub.” Impl plan IMP-010: “runnable MVP topology (not a stub).” |
| **F-004** | SRS Open Questions closed to design/ML-005/CR-001; PRD numeric OQ → ML-005 | **Closed** | SRS §Open questions remaining: feature formulas, validation policy, raw layout, numeric ML threshold, player persist — all **Resolved**. Leftovers = free-tier vs DR-001 assumption; cloud deploy Future. PRD success metrics point at **ML-005**; no numeric-threshold Open Question. |
| **F-005** | `schema_migrations` in `schema.sql`; feature JSONB envelope documented | **Closed** | `database/schema.sql` creates `schema_migrations`. `database-design.md` v1.0.2 documents the table **and** `features.payload` envelope `{values, label_home_win, used_cold_start_*}` matching `src/athletiq/features/postgres.py`. |
| **F-006** | `# Implements` removed from tests; added on listed missing files | **Closed** | No `# Implements` under `tests/unit/` or `tests/integration/`. Present on `pyproject.toml`, `database/schema.sql`, `database/migrations/001_initial.sql`, `api/openapi.yaml`, `docs/06-design/model-card.md`, `tests/fixtures/provider/README.md`. |
| **F-007** | Observability SLO OQ closed (NFR-004); logging documents IMP-001 formatter; packaging OQ removed; ML contract = pin+joblib+JSON | **Closed** | `observability.md`: SLO OQ **Closed** citing NFR-004; no invented backend. `logging.md`: IMP-001 formatter documented; correlation/retention = Gate 9 leftover. Impl plan: “Packaging: hatchling + pip / `pyproject.toml`” — no uv-vs-Poetry Open. Documentation guide ML contract = “selection pin + joblib + lineage JSON (ADR-003/004; not a TBD MLflow registry).” |
| **F-008** | OpenAPI `security: []` | **Closed** | `api/openapi.yaml`: `security: []` and `securitySchemes: {}`. FastAPI still has no auth middleware. ADR-009 consequence held. |

---

## Remaining findings

| ID | Severity | Area | Evidence | Owning skill | Recommended action |
|---|---|---|---|---|---|
| F-009 | **nit** | FR-003 verification grain | SRS FR-003 AC still says example queries “execute successfully **against persisted data**.” TEST-005 is `tests/unit/test_analytics.py` (in-memory clones + SQL **string** asserts); test-plan **Level: integration**, Status **Passing** (unqualified). Traceability FR-003 Verification = **Passing (local)**. Contrast TEST-004, which honestly says Passing (in-memory). `ROLLING_TEAM_POINTS_SQL` is never executed against Postgres in tests. Does **not** reopen CR-001 (team Must vs reserved player helper is documented). | `testing` (label) / `requirements` (AC wording if you tighten) | Optionally align TEST-005 Status to Passing (in-memory) and/or Level to unit, or add a Postgres execution of the team-window SQL. Not required to keep 9 / 10. |

Nits not table-worthy (unchanged or leftover): architecture/API still mention a home/away/date **matchup** resolver (`system-architecture.md`, `api-architecture.md`, ADR-008) while contract/code resolve `game_id` or `provider_game_id` only; impl-plan upstream still cites DB design v1.0.1 / test plan v1.0.0 after 1.0.2 / 1.0.1 bumps; `schema.sql` snapshot has the `schema_migrations` **table** but not the `001_initial` INSERT row (apply path does); `seasons_to_prune` remains a helper not called from the pipeline (ingest already skips out-of-window seasons — documented on IMP-004); SRS Sources still say Charter 1.0.0 vs file 1.0.1; `.env.example` uses `# Implements intent:` rather than `# Implements:`; Charter/deploy Gate-8 Open Questions remain (expected).

---

## Drift defects (design vs contract vs code)

### Database

| Claim | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Engine / ids | PostgreSQL; BIGINT/BIGSERIAL (ADR-010) | `schema.sql` BIGSERIAL PKs; no UUID | Migrations + TEST-002 | **Aligned** |
| Entity themes | MVP load: teams, games, `team_game_stats`; players reserved (**CR-001**) | Tables present; reserved comments on player tables | Load/API **never writes** `players` / `player_game_stats` (spot-checked `src/athletiq/load/*`, `tests/integration/test_postgres_stores.py`) | **Aligned** (empty player tables expected) |
| Indexes (NFR-005) | Six indexes incl. reserved player | Same names | Migrations match | **Aligned** |
| Idempotent grain | DR-003; MVP grains only | UNIQUE `provider_*`; PKs on stats/features | Postgres upserts on those keys | **Aligned** |
| Snapshot completeness | `schema.sql` = consolidated snapshot incl. `schema_migrations` | Table present | `001_initial.sql` also INSERTs version row | **Aligned** on table (INSERT-row nit only) |
| Feature payload | Envelope documented | Comment + `payload JSONB` | `{values, label_home_win, used_cold_start_*}` + legacy bare map | **Aligned** |
| `model_registry` | Optional mirror; files canonical | Table exists | Publish writes **files only** | **Aligned** — do not treat table as live lineage |

### API

| Claim | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Routes | `/v1/health`, `/v1/predict`, `/v1/model` | Same in `openapi.yaml` | `api/app/routes.py` | **Aligned** |
| Auth | None (ADR-009); localhost/Compose | `security: []` | No middleware; Compose `127.0.0.1:8000` | **Aligned** |
| Predict key | `game_id` string of BIGINT; optional `provider_game_id` | Both query params optional | 400 if both missing; int parse; provider resolver | **Aligned**. Matchup home/away/date in architecture is still ahead of contract — nit, not a code bug. |
| Errors | Distinct `game_not_found` vs `features_not_found`; 503 model/DB; no silent baseline | Enum matches | `errors.py` + `state.py` | **Aligned** |
| Lineage | `model_version`, `feature_version`; card via `/v1/model` | Required fields | Pin-loaded; methodology matches model card | **Aligned** |
| Threshold | `home_win_pred` = `p >= 0.5` | boolean | Same | **Aligned** |

### ML

| Claim | Design + model card | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Feature version | `team_l5_l10_v1`; L5/L10 + season WR; `min_prior_games=5`; no player-level features | Pin JSON + `FEATURE_VERSION` | `src/athletiq/features/builder.py` | **Aligned** |
| Splits | Temporal ~70/15/15; no shuffle | Lineage `dataset_version` | `src/athletiq/ml/splits.py` | **Aligned** |
| Selection | Val log loss; tie → LR; baselines never served | Pin at batch time | `select.py` + `publish.py`; API loads pin only | **Aligned** |
| Artifacts | joblib + JSON; ML-009 fields | Files under artifacts volume (ADR-004) | Pin has `artifact` path | **Aligned** |
| ML-005 | Test log loss &lt; domain-informed | Eval report / attestation | TEST-007 **Passing (synthetic)**; Implementation **Partial** | **Honest** — do not claim NBA holdout attestation |

---

## ADR consequences check (Accepted only)

| ADR | Consequences present? | Observed follow-through | Verdict |
|---|---|---|---|
| **001** PostgreSQL 16 | Yes | Compose `postgres:16`; dialect in schema/migrations | **Held** |
| **002** API-Sports + adapter | Yes | `ApiSportsProvider` + `FixtureProvider`; key via env; teams+games surface (CR-001) | **Held** |
| **003** Val select / test once / pin | Yes | `select.py`, train pipeline, API pin load; baselines not served | **Held** |
| **004** Local artifacts volume | Yes | Compose `artifacts` on etl+api | **Held** |
| **005** Thin bash → Python orchestrator | Yes | `scripts/run_pipeline.sh` execs `python -m athletiq.pipeline` | **Held** |
| **006** Immutable raw JSON FS; prune too-old | Yes | Ingest refuses overwrite; new batch id; skip out-of-window seasons | **Mostly held**; curated prune helper unused (nit, documented) |
| **007** GCP | Proposed only | Correctly omitted from binding index | **Non-binding — ignore for MVP** |
| **008** `game_id` + precomputed features | Yes | Predict lookup `(game_id, feature_version)`; shared preprocess | **Held** |
| **009** No auth; local bind | Yes | Compose `127.0.0.1:8000`; no auth; OpenAPI `security: []` | **Held** |
| **010** BIGINT not UUID | Yes | schema, migrations, OpenAPI decimal string, TEST-002 | **Held** |

---

## Architecture review gate (§21)

| Lens | Judgment |
|---|---|
| Requirements coverage | Must set is architected **and** CR-001-amended. Player persistence is reserved schema, not a silent Must. |
| Component boundaries | Clear: adapter / raw FS / curated PG / shared features / batch ML / sync API. `--store` / `ATHLETIQ_STORE` remains the right seam. |
| Data flow | Documented and implemented for **team-level** ingest→features→train→pin→predict. Empty player tables are **specified**, not theater. |
| Failure modes | Execution vs quality-gate vs validation skip is real. Missing pin → 503, not baseline. Good. |
| Scalability | Explicitly single-node. Correct for MVP. |
| Security | ADR-009 is an exposure decision. Secrets via env; CI has no live key. Public bind without a CR would be a defect — none in Compose. |
| Maintainability | Binding ADRs + contracts + independent traceability columns are a maintainable map. |
| Observability | `/v1/health` + structured logs with redaction. Gate 9 Draft; NFR-004 respected. |
| Testing implications | NFR-003 fixtures are real. TEST-013/014 exist. ML-005 is synthetic. FR-003 team SQL is specified more strongly than the unit clone tests (F-009 nit). |
| Operational implications | Manual retrain via pipeline. Remote CI green not claimed. |
| Technology decisions | Binding set complete for MVP. ADR-007 stays non-binding. |

---

## What is architecturally sound (keep)

- No-leakage / test-isolation / pin-only serving invariants.
- Logical stages in **one etl image**, not fake microservices.
- CR-001: team-level MVP load; reserved player tables called out in SRS/PRD/design/schema/tests.
- Independent traceability columns; Partial/synthetic/deferred used where the product bar is not attested.
- ADR-008/010: BIGINT internally, decimal string on the wire.
- ADR-009 written down; Compose bound to localhost; OpenAPI `security: []`.
- Error taxonomy: `game_not_found` ≠ `features_not_found`; 503 for model/DB; no silent baseline.
- Train/serve shared `feature_version` + `preprocess_for_model`.
- Explicit `--store` / `ATHLETIQ_STORE`.
- CI DAG: lint ∥ unit → integration (ephemeral Postgres) → image; no live API-Sports.
- Charter vs PRD split still respected.
- IMP DoD leaving **code review** and **remote CI** unchecked is honest; PRD acceptance unchecked is honest.

---

## What not to do next (scope creep)

- Do **not** Accept ADR-007 or design GCP/CD.
- Do **not** add API keys/auth “because ADR-009 looks incomplete.”
- Do **not** add player ingest, player-level ML features, NumPy NN, score/spread, UI, MLflow, drift dashboards, or automated retrain (CR-001 demoted player persist; do not reverse without a new CR).
- Do **not** invent latency/availability SLOs (NFR-004).
- Do **not** mark traceability Implemented because pytest is green.
- Do **not** claim remote CI green, 2–3 live NBA seasons ingested, or NBA ML-005 attestation.
- Do **not** tick PRD MVP acceptance items that are not true.
- Do **not** treat IMP-001…012 Done as Gate 8/9 or as publish-bar complete.

---

## Recommended next actions (optional; not 9/10 blockers)

1. **Nit pass** — `testing`: TEST-005 Status/Level vs FR-003 AC (F-009). Optionally bump impl-plan upstream version cites.
2. **Publish-bar remainder (still later)** — freeze a dataset/`feature_version` and run ML-005 on a real holdout; ingest 2 completed seasons under DR-001; record remote GHA green; then tick only PRD items that are actually true.

---

## Validation (this review)

- [x] No Grill-Me
- [x] No primary doc authorship (this file only)
- [x] Every Accepted ADR checked for consequences
- [x] Findings actionable and mapped to owning skills
- [x] Prior F-001…F-008 re-checked against repo (docs + code)
