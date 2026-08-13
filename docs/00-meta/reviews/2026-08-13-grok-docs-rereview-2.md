# Grok re-review 2 — AthletIQ living docs after LEAD Must closes

Status: Complete  
Date: 2026-08-13  
Reviewer role: Engineering reviewer (read-only `engineering-review`)  
Baselines:
- Managing architect: `docs/00-meta/reviews/2026-08-13-managing-architect-docs.md` (7 / 10)
- Grok first pass: `docs/00-meta/reviews/2026-08-13-grok-docs-rereview.md` (9 / 10)
- Lead Sol: `docs/00-meta/reviews/2026-08-13-lead-sol-docs-review.md` (8 / 10; LEAD-001 blocker)
- Grok disposition: `docs/00-meta/reviews/2026-08-13-grok-lead-disposition.md` (LEAD-001 confirmed; Must 1–4 = ≥9/10 bar)

Scope: Verify claimed Must closes in the current tree; re-check LEAD-001…003, prior F-001…F-009, design/contract/implementation drift, Accepted ADR consequences.  
Must not: Grill-Me; primary Charter/PRD/SRS/architecture/ADR/design/impl/test edits.

---

## Executive verdict

The LEAD Must list landed. The copy-paste Compose command now includes `--store postgres` in the three places reviewers copy from (root `README.md`, `docs/09-devops/infrastructure.md` etl row, `docker-compose.yml` etl comment). Root README has a clean-clone path (`.env.example` → `.env`, `docker compose up -d --build`, canonical pipeline, `/v1/health` and `/v1/model`). NFR-001 is no longer unqualified **Passing (local)**; FR-012 Verification is **Passing (static topology)** and the SRS no longer pretends TEST-010 closes e2e. TEST-010 dropped bring-up; TEST-013 is still training-repeat. CON-003 stays Passing. LEAD-002 and LEAD-003 were narrowed in ADR-005 / architecture / error-handling and ADR-008 / API architecture / glossary. No new Compose e2e pytest was added — correct per the disposition.

**LEAD-001 is Closed.** Remaining disagreements are leftover titles and legend lag (TEST-010 still “smoke / health/startup” in the ID registry and test-strategy; strategy principle 4 still collapses NFR-001 onto TEST-013). They do not overclaim the Approved SRS/traceability/test-plan grain.

This is **not** MVP-complete: PRD acceptance remains unchecked; DR-001 and ML-005 are Partial / synthetic; remote CI is Deferred; Gates 8–9 are Draft; no owner attestation of the clean-machine path is recorded (allowed — that slice stays Partial).

**Score: 9 / 10** — Must closes verified; leftover items are unimportant. Not 10 / 10 because TEST-010/NFR-001 wording in strategy + ID registry still lags the honesty pass.

**≥9 / 10: yes.** OPEN blockers: **none**.

---

## Gate snapshot

A gate is satisfied only when required artifacts are **Approved**. “Done code” ≠ Gate 8/9.

| Gate | Phase | Artifacts | Status |
|---|---|---|---|
| 0 | Project initiation | `docs/01-project/project-charter.md` | **Approved** 1.0.1 |
| 1 | Product definition | `docs/02-product/PRD.md` | **Approved** 1.0.4 (CR-001); MVP acceptance **unchecked** (correct) |
| 2 | Requirements | `docs/03-requirements/SRS.md`, `traceability.md` | **Approved** (SRS **1.4.1**; traceability **1.5.1**) |
| 3 | Architecture | `docs/04-architecture/*`, binding ADRs | **Approved**; ADR-001–006, 008, 009, 010 **Accepted**; ADR-007 **Proposed / non-binding** |
| 4 | Detailed design | DB / API / ML / errors + model card | **Approved** (DB 1.0.2; ML 1.0.1; API 1.0.0; errors **1.0.1**; model card 1.0.0) |
| 5 | Implementation planning | `docs/07-implementation/implementation-plan.md` | **Approved** 1.0.2; IMP-001…012 **Done** (code-review + remote-CI DoD boxes still open — honest) |
| 6 | Implementation | Code + `# Implements` on listed modules | **Code exists**; CLI `--store` still defaults **memory** (intentional) |
| 7 | Verification | Test strategy/plan + execution | **Docs Approved** (strategy 1.0.0; plan **1.0.2**); TEST-001…014 local; **remote GHA green deferred** |
| 8 | Release | `docs/12-releases/*` | **Draft** — expected |
| 9 | Operations | `docs/10-operations/*`, change process | **Draft**; leftover OQs are Gate 8/9 |

**CR-001:** still Accepted / registered. Do **not** treat IMP-001…012 Done as MVP-complete.

---

## Claimed Must closes (this pass)

Canonical command checked everywhere it is offered as copy-paste:

`docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture`

| Claim | Evidence | Verdict |
|---|---|---|
| Canonical command in README, infrastructure etl row, Compose comment | `README.md` Local demo block; `docs/09-devops/infrastructure.md` etl row; `docker-compose.yml` line 41 | **Held** |
| Store-selection paragraph kept | README + infrastructure: host CLI defaults memory; Compose **must** pass `--store postgres`; `scripts/run_pipeline.sh` is host bash; API `ATHLETIQ_STORE=postgres`; CLI does not read `ATHLETIQ_STORE` | **Held** |
| Clean-clone: `.env.example` → `.env`, `up -d --build`, canonical command, `/v1/health` + `/v1/model` | `README.md` Local demo; `.env.example` present | **Held** |
| NFR-001 Implementation Partial; Verification split; no owner attestation | Traceability v1.5.1: Implementation **Partial**; Verification **Passing (local) / Partial (clean-machine)**. Notes: workflow in README; attestation **not recorded**; TEST-001/013 do not close clean-machine. SRS NFR-001 AC matches. | **Held** |
| FR-012 Verification = Passing (static topology); AC no longer claims TEST-010 closes e2e | Traceability FR-012 Verification **Passing (static topology)**; Implementation **Implemented**. SRS FR-012: TEST-010 = static topology; e2e is NFR-001, **not** closed by TEST-010. | **Held** |
| TEST-010 plan dropped bring-up step 3 | Test plan v1.0.2: two steps (`compose config` + declared services/volumes). Expected result: bring-up / pipeline / `/v1/health` **not** this suite. `tests/integration/test_compose.py` still file text + optional `docker compose config` only. | **Held** |
| TEST-013 still training-repeat, not retitled clean-clone | Title remains **Training reproducibility**. Description: “**training-repeatability**, not a clean-clone Compose demo.” Module `tests/unit/test_reproducibility.py` still synthetic feature/train repeat. | **Held** |
| CON-003 may stay Passing | Traceability CON-003 **Implemented** / **Passing (local)**. AC is still “Compose file **defines** database, ETL, API.” | **Held** |
| LEAD-002 narrowed | ADR-005 v1.2.0 Decision: `save_state` **not** restored; `--from-stage train` from `feature_matrix.npz`; `--from-stage features` same-process (`ctx.store`). Echoed in `system-architecture.md` §8 and `error-handling.md`. IMP-009 points at ADR-005 restart limits. No `load_state` under `src/`. | **Held** |
| LEAD-003 Future matchup; MVP resolver = `provider_game_id` | ADR-008, `system-architecture.md`, `api-architecture.md`, glossary. OpenAPI query params remain `game_id` / `provider_game_id` only. | **Held** |
| No new Compose e2e test | No bring-up / pipeline / predict pytest. Correct. | **Held** |
| CLI `--store` default still memory | `src/athletiq/pipeline/__main__.py` `default="memory"` | **Held** |

Disposition Must 4: workflow exists **and** clean-machine slice left **Partial** (no owner attestation). That is an allowed close. Relabel-only without the canonical command did **not** happen.

---

## LEAD findings

| ID | Prior | This pass | Blocks 9/10? |
|---|---|---|---|
| **LEAD-001** | OPEN (lead); confirmed blocker (disposition) | **Closed** | **No** |
| **LEAD-002** | OPEN nit | **Closed** (docs narrowed; no restore implemented — correct) | No |
| **LEAD-003** | OPEN nit | **Closed** (Future / `provider_game_id` only) | No |

### OPEN findings blocking 9/10

None.

---

## Prior findings F-001…F-009

Independent spot-check; not re-litigated unless the Must pass broke them.

| ID | Disposition |
|---|---|
| F-001 player path | **Still Closed** (CR-001). No `fetch_player` / `upsert_player` / `INSERT INTO players` under `src/`. Do not demand player ingest. |
| F-002 independent columns | **Still Closed**. v1.5.1 still splits Requirement / Implementation / Verification. NFR-001 Implementation Partial is conservative (attestation is verification evidence); not an overclaim. |
| F-003 stub language | **Still Closed**. `docs/README.md` MVP topology/workflow. |
| F-004 Gate-4 OQs | **Still Closed** (not reopened by NFR-001/FR-012 AC edits). |
| F-005 schema snapshot / payload | **Still Closed**. `schema_migrations` in `schema.sql`; envelope in database-design. |
| F-006 `# Implements` | **Still Closed** (not re-sprayed by this pass). |
| F-007 ops/packaging/registry | **Still Closed**. |
| F-008 OpenAPI `security: []` | **Still Closed**. |
| F-009 TEST-005 in-memory | **Still Closed**. Plan: Level unit; Status Passing (in-memory). |

---

## Remaining findings

| ID | Severity | Area | Evidence | Owning skill | Recommended action |
|---|---|---|---|---|---|
| F-010 | **nit** | TEST-010 / NFR-001 leftover titles | `docs/00-meta/id-registry.md` TEST-010 = “Compose **smoke** suite.” `docs/08-testing/test-strategy.md` TEST-010 vs TEST-011 table still says “health/startup”; principle 4 still says NFR-001 is verified by TEST-013 twice-run. Approved test-plan, SRS, and traceability already split training-repeat vs static topology vs clean-machine Partial. | `testing` (strategy + registry titles) | Optionally retitle TEST-010 in the registry and drop “health/startup” / NFR-001=TEST-013 collapse from strategy on the next test-doc touch. **Not** required to keep 9 / 10. |

Nits not table-worthy: traceability “Allowed values” legend omits `Passing (static topology)` and `Partial (clean-machine)` (matrix uses both; Notes explain them); implementation-plan Upstream still cites SRS 1.4.0 / traceability 1.5.0 / test plan 1.0.1 after 1.4.1 / 1.5.1 / 1.0.2; ADR-005 **Consequences** stay generic while the **Decision** now enumerates restart limits (architecture/error-handling carry the detail); README uses Unix `cp` for `.env.example` (works in Git Bash; PowerShell equivalent is obvious). None reopen LEAD-001.

---

## Drift defects (design vs contract vs code)

### Database

| Claim | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Engine / ids | PostgreSQL; BIGINT/BIGSERIAL (ADR-010) | `schema.sql` BIGSERIAL PKs | Migrations + TEST-002 | **Aligned** |
| Entity themes | MVP load: teams, games, `team_game_stats`; players reserved (CR-001) | Tables present; reserved comments | Load never writes player tables | **Aligned** |
| Snapshot / payload | `schema_migrations` + JSONB envelope | Table + comment | Migrate INSERT + `features/postgres.py` envelope | **Aligned** |
| Local persistence path | Curated PostgreSQL for demo | Compose Postgres + volumes | Canonical Compose command now passes `--store postgres`; host CLI still defaults memory | **Aligned** (LEAD-001 copy-paste drift **closed**) |

### API

| Claim | Design | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Routes / errors / auth | health/predict/model; distinct 404/503; no auth | Same; `security: []` | Routes/state; no middleware; Compose `127.0.0.1:8000` | **Aligned** |
| Prediction key | `game_id`; optional `provider_game_id`; home/away/date **Future** | Query params `game_id` / `provider_game_id` only | Same | **Aligned** (LEAD-003 **closed**) |

### ML

| Claim | Design + model card | Contract | Implementation | Verdict |
|---|---|---|---|---|
| Features / splits / selection / pin | Team L5/L10; ~70/15/15; val log loss; pin-only serve | Pin JSON + `FEATURE_VERSION` | builder / splits / select / publish | **Aligned** |
| ML-005 | Test log loss &lt; domain-informed on frozen holdout | Eval metadata path | TEST-007 Passing (synthetic); Implementation Partial | **Honest** — do not claim NBA holdout |
| Reproducibility | NFR-001 clean-machine **or** owner attestation; TEST-013 = train-repeat | README workflow; no attestation recorded | TEST-013 synthetic repeat; TEST-010 static Compose | **Honest** — LEAD-001 evidence drift **closed** |

---

## ADR consequences check (Accepted only)

| ADR | Consequences present? | Observed follow-through | Verdict |
|---|---|---|---|
| **001** PostgreSQL 16 | Yes | Compose `postgres:16`; dialect in schema/migrations | **Held** |
| **002** API-Sports + adapter | Yes | `ApiSportsProvider` + `FixtureProvider`; teams+games (CR-001) | **Held** |
| **003** Val select / test once / pin | Yes | `select.py`, train pipeline, API pin load; baselines not served | **Held**; ML-005 still honestly Partial |
| **004** Local artifacts volume | Yes | Compose `artifacts` on etl+api; README demo uses shared volumes | **Held** |
| **005** Thin bash → Python orchestrator | Yes (generic); Decision now lists restart limits | Thin bash; Python stages; `save_state` write-only; `--from-stage` as documented | **Held** (LEAD-002 closed). Consequence paragraph could restate restart limits — nit. |
| **006** Immutable raw JSON FS | Yes | Ingest refuses overwrite; skip out-of-window seasons | **Mostly held**; curated prune helper unused (nit, previously documented) |
| **007** GCP | Proposed only | Omitted from binding index | **Non-binding — ignore for MVP** |
| **008** `game_id` + precomputed features | Yes | `(game_id, feature_version)`; shared preprocess; MVP resolver `provider_game_id`; matchup Future | **Held** (LEAD-003 closed) |
| **009** No auth; local bind | Yes | Compose `127.0.0.1:8000`; no auth; OpenAPI `security: []` | **Held** |
| **010** BIGINT not UUID | Yes | schema, migrations, OpenAPI decimal string, TEST-002 | **Held** |

---

## Architecture review gate (§21)

| Lens | Judgment |
|---|---|
| Requirements coverage | Must set architected and CR-001-amended. NFR-001 clean-machine AC is documented and honestly Partial. |
| Component boundaries | Adapter / raw FS / curated PG / shared features / batch ML / sync API. `--store` / `ATHLETIQ_STORE` remains the right seam. |
| Data flow | Team-level ingest→features→train→pin→predict. Empty player tables specified. Demo path now unambiguous for Postgres. |
| Failure modes | Missing pin → 503, not baseline. Restart/resume claims now match code. |
| Scalability | Single-node. Correct for MVP. |
| Security | ADR-009 exposure decision. Secrets via env. No public bind in Compose. |
| Maintainability | Independent traceability columns; Partial/synthetic/deferred where the product bar is not attested. |
| Observability | `/v1/health` + structured logs. Gate 9 Draft; NFR-004 respected. |
| Testing implications | TEST-010 static; TEST-013 synthetic train-repeat; no Compose e2e pytest (correct). ML-005 synthetic. |
| Operational implications | Manual retrain via documented Compose command. Remote CI green not claimed. Clean-machine unattested (Partial). |
| Technology decisions | Binding set complete. ADR-007 stays non-binding. |

---

## What is architecturally sound (keep)

- Canonical Compose/Postgres command in the three copy-paste surfaces.
- README clean-clone path without hunting reviews.
- Honest NFR-001 / FR-012 / CON-003 grain split.
- CR-001 team-level MVP; reserved player tables.
- Independent traceability columns; Partial/synthetic/deferred used where true.
- ADR-005 restart limits match code (`save_state` not restored).
- ADR-008 MVP resolver = `provider_game_id`; matchup Future.
- Pin-only serving; no silent baseline; BIGINT on the wire as decimal string.
- CLI `--store` default memory; Compose demo must pass postgres.
- IMP DoD leaving code review and remote CI unchecked; PRD acceptance unchecked.

---

## What not to do next (scope creep)

- Do **not** add a Compose bring-up → pipeline → API pytest solely to close this review (already closed without it).
- Do **not** implement `save_state` restore or home/away/date predict to “match old prose.”
- Do **not** change CLI `--store` default to postgres.
- Do **not** Accept ADR-007 or design GCP/CD.
- Do **not** add API keys/auth, player ingest, player-level ML, NumPy NN, SLOs, or automated retrain.
- Do **not** claim remote CI green, 2–3 live NBA seasons, or NBA ML-005 attestation.
- Do **not** tick PRD MVP acceptance items that are not true.
- Do **not** treat IMP-001…012 Done as Gate 8/9 or publish-bar complete.
- Do **not** record a fake owner attestation; leave NFR-001 clean-machine Partial until a real run is recorded.

---

## Recommended next actions (optional; not 9/10 blockers)

1. **Nit pass** — `testing`: F-010 (TEST-010 registry/strategy titles; strategy principle 4). Optionally extend the traceability allowed-values legend; bump impl-plan Upstream version cites.
2. **Owner attestation (optional)** — run the README path on a clean machine and record one line in traceability notes. Until then Partial is correct.
3. **Publish-bar remainder (still later)** — freeze dataset/`feature_version` and attest ML-005 on a real holdout; ingest 2 completed seasons under DR-001; record remote GHA green; then tick only PRD items that are actually true.

---

## Validation (this review)

- [x] No Grill-Me
- [x] No primary doc authorship (this file only)
- [x] Every Accepted ADR checked for consequences
- [x] Findings actionable and mapped to owning skills
- [x] LEAD-001…003 and claimed Must closes re-checked against current docs, Compose, CLI, OpenAPI, and tests
- [x] Prior F-001…F-009 spot-checked
- [x] Did not demand player ingest, GCP, auth, remote CI green, NBA ML-005, or ticking PRD acceptance
