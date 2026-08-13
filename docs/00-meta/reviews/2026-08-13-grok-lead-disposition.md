# Grok disposition of lead docs review

Status: Complete  
Date: 2026-08-13  
Reviewer role: Engineering reviewer (read-only `engineering-review`) — disposition of lead rejection, not a full re-score  
Baseline: `docs/00-meta/reviews/2026-08-13-lead-sol-docs-review.md` (8 / 10; ≥9/10 rejected)  
Prior Grok pass: `docs/00-meta/reviews/2026-08-13-grok-docs-rereview.md` (9 / 10)  
Scope: Re-check LEAD-001…003 against the **current** repo. Write this file only.

Must not: Grill-Me; primary Charter/PRD/SRS/architecture/ADR/design/impl/test edits.

---

## Ruling (this pass)

The lead’s rejection of **≥9/10 is upheld**. **LEAD-001 is a valid 9/10 blocker** on the current tree. Grok’s prior 9/10 under-weighted NFR-001 / FR-012 evidence grain: TEST-013 and TEST-010 are honestly labeled at the test-plan grain, but Approved traceability still reports those requirements as **Implemented / Passing (local)** against an SRS that requires a **documented clean-machine demo**, while the copy-paste Compose command still omits `--store postgres`.

This file does **not** re-score the whole docs set. It is a ruling on the lead rejection.

| Finding | Disposition | Blocks 9/10? |
|---|---|---|
| **LEAD-001** | **Confirm as blocker** | **Yes** |
| **LEAD-002** | **Confirm as nit (fix anyway)** | No |
| **LEAD-003** | **Confirm as nit (fix anyway)** | No |

**Bar to close LEAD-001 (and thus expect both reviewers ≥9/10):** honest evidence labels **and** one unambiguous Compose/Postgres workflow in the places people copy from. **Do not** add a new Compose bring-up → pipeline → API pytest to close this. SRS NFR-001 AC already allows **owner attestation or scripted smoke**; documented steps plus honest labels (and optional owner attestation) suffice.

---

## LEAD-001 — NFR-001 / FR-012 overstated; ambiguous demo command

**Disposition: Confirm as blocker.**

### What the lead got right (current repo)

| Claim | Current evidence | Verdict |
|---|---|---|
| NFR-001 SRS is clean-machine, not “run train twice” | `docs/03-requirements/SRS.md`: clone, configure documented env, reproduce pipeline/eval without editing source. AC: “Documented steps succeed on a **clean machine** (owner attestation or scripted smoke).” | **Held** |
| FR-012 AC2 ties e2e demo to NFR-001 | FR-012 AC: documented compose brings up db/etl/api **and** “End-to-end local demo path works per NFR-001.” | **Held** |
| Traceability overstates | `docs/03-requirements/traceability.md` v1.5.0: NFR-001 and FR-012 = **Implemented** / **Passing (local)**. Mapped tests: TEST-001+TEST-013 and TEST-010. | **Held** |
| TEST-013 ≠ clean-clone | `tests/unit/test_reproducibility.py`: in-process synthetic feature/train repeat. Test-plan Status already says “controlled synthetic fixture.” | **Held** (overclaim is **traceability aggregation**, not the test module lying about itself) |
| TEST-010 ≠ Compose bring-up | `tests/integration/test_compose.py`: file text + optional `docker compose config`. Never `up`, never pipeline, never `/v1/health`. Test-plan Status already says “static topology.” Plan **step 3** still mentions bring-up that the code does not run. | **Held** |
| Root README has no setup/run | `README.md`: docs index + gate status only. No clone → `.env` → compose → pipeline → curl. | **Held** |
| Copy-paste ETL command defaults memory | CLI `--store` **default memory** (`src/athletiq/pipeline/__main__.py`). `docker-compose.yml` comment: `docker compose run --rm etl python -m athletiq.pipeline --provider fixture ...` — **no** `--store postgres`. `docs/09-devops/infrastructure.md` etl row: same `python -m athletiq.pipeline …` ellipsis. Compose **api** sets `ATHLETIQ_STORE: postgres`; **etl does not**. Pipeline CLI does not read `ATHLETIQ_STORE`. | **Held** |

Partial mitigation that does **not** close the finding: `infrastructure.md` already has a **Store selection** paragraph (`python -m athletiq.pipeline` defaults memory; `./scripts/run_pipeline.sh` passes `--store postgres`). Reviewers who copy the **etl table command** or the **Compose comment** still get an in-memory run that does not populate PostgreSQL or the API’s store. `.env.example` exists; nothing in README tells a new clone to use it.

Host wrapper `scripts/run_pipeline.sh` **does** `exec python -m athletiq.pipeline --store postgres "$@"`. That is the right demo store. It is **not** the documented Compose copy-paste. The etl image is `python:3.11-slim` (no `bash` install); the script shebang is `#!/usr/bin/env bash`, so `./scripts/run_pipeline.sh` inside Compose is not a safe canonical command. The unambiguous Compose command is:

```text
docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture
```

PRD MVP acceptance remaining unchecked is **correct** and does not excuse Approved SRS/traceability saying Passing (local) for the clean-machine AC.

### What the lead overreached (remedy, not the defect)

- **Do not require a new Compose e2e pytest** (bring-up → pipeline → healthy API/predict) to restore ≥9/10. That is one valid *scripted smoke*, not the only AC. NFR-001 explicitly allows **owner attestation**.
- Do not treat TEST-013 / TEST-010 **Status lines** as dishonest. They already qualify synthetic vs static. The 9/10 defect is **Approved traceability** (and FR-012 AC2) claiming those tests close the clean-machine / e2e demo bar, plus an **ambiguous demo command**.
- CON-003 AC is only “Compose file **defines** database, ETL, API.” TEST-010 covers that. CON-003 **Passing (local)** may stay. Do not drag CON-003 into the same Partial bucket as FR-012’s e2e AC.

### Required close (docs-only)

See implementer list below. Relabeling Passing **without** replacing the copy-paste command is **not** a close (agree with lead). Adding a Compose e2e test **without** honest labels and a canonical command is also not the required path.

---

## LEAD-002 — ADR-005 resume/checkpoint exceeds code

**Disposition: Confirm as nit (fix anyway).** Not a 9/10 blocker.

### Evidence (current repo)

- ADR-005 Decision: “Stages are checkpointed so partial failures can resume (e.g. retrain without full re-ingest when safe).” Consequences do **not** enumerate which restart points work.
- `PipelineContext.save_state()` writes `artifacts/pipeline_state.json`. **No** `load_state` / read of that file exists under `src/`.
- `--from-stage` only **selects a stage window** (`resolve_stages`). A new process builds a fresh `PipelineContext`.
- **Supported after restart:** `--from-stage train` if `feature_matrix.npz` exists (`stage_train` rediscovers it). `--from-stage load` can rediscover latest raw batch.
- **Not supported after restart:** `--from-stage features` raises `no curated store; run load first` because `stage_features` requires in-process `ctx.store` and does **not** reopen Postgres/memory from checkpoint. Same-process `--from-stage features` after load in that process works; TEST-009 never tests process restart.
- Echoed overclaim: `system-architecture.md` §8 “rerun from checkpointed stage when safe”; `error-handling.md` “rerun from checkpoint when safe”; IMP-009 “stage selection / resume where safe” (acceptable only if “safe” is defined).

Lead’s code reading is accurate. Fix by **narrowing docs** (architecture-decisions + architecture + error-handling). **Do not** implement checkpoint restore just to close a documentation nit.

---

## LEAD-003 — matchup home/away/date vs OpenAPI/code

**Disposition: Confirm as nit (fix anyway).** Not a 9/10 blocker. Same leftover Grok already logged as a non-table nit in the 9/10 pass.

### Evidence (current repo)

| Layer | What it says |
|---|---|
| Architecture | `system-architecture.md`: matchup (home + away [+ date]) may resolve to `game_id`. `api-architecture.md`: “Optional resolver to unique `game_id`.” |
| ADR-008 | Optional home/away/date matchup may only resolve to `game_id`; “OpenAPI will center on `game_id` (+ optional resolver fields).” |
| Glossary | “Matchup \| Home/away pairing (**optional predict input**) used only to resolve a unique `game_id`.” |
| Design / contract / code | `api-design.md` + `api/openapi.yaml` + `api/app/routes.py`: **`game_id` or `provider_game_id` only**. No home/away/date parameters. |

Design vs contract vs code for the **shipped** resolver (`provider_game_id`) is aligned. Architecture/ADR/glossary still promise a **second** resolver that does not exist.

**Do not** implement home/away/date to close this. Label it **Future / not in MVP OpenAPI**, and state that the only optional resolver in MVP is `provider_game_id`.

---

## Required implementer actions

Docs-only unless noted. Owning skills in parentheses. **No** new Compose e2e test. **No** checkpoint-restore feature. **No** matchup resolver feature. **Do not** change CLI `--store` default to postgres (memory default is intentional for unit/offline).

### Must (closes LEAD-001; required for ≥9/10)

1. **Canonical Compose/Postgres command** (`devops-operations`; tiny comment in `docker-compose.yml`): Replace every copy-paste ETL invocation that is `python -m athletiq.pipeline` **without** `--store postgres` in `docs/09-devops/infrastructure.md` (etl row) and the `docker-compose.yml` etl comment. Canonical:

   `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture`

   Keep the store-selection paragraph. State explicitly: host `python -m athletiq.pipeline` defaults **memory**; `scripts/run_pipeline.sh` is the **host** postgres wrapper (bash); Compose demo **must** pass `--store postgres`; API uses `ATHLETIQ_STORE=postgres` and shared `artifacts` / `raw_data` volumes.

2. **Clean-clone workflow** (`devops-operations` + root `README.md`): Document prerequisites (Docker Compose), copy `.env.example` → `.env`, `docker compose up -d --build`, the canonical pipeline command above, then `GET http://127.0.0.1:8000/v1/health` and `/v1/model`. One page a new clone can follow without hunting reviews.

3. **Honest labels** (`requirements` + `testing`):
   - NFR-001 Verification: **do not** keep unqualified **Passing (local)**. Split: TEST-013 = training-repeatability (keep its existing synthetic/controlled-fixture Status); clean-machine AC = **Partial** / **Planned** until the workflow in (2) exists **and** an owner attestation (or a later optional smoke) is recorded in traceability notes / test-plan.
   - FR-012: Implementation may stay **Implemented** (topology exists). Verification must match TEST-010: **Passing (static topology)** — not e2e demo. The NFR-001 e2e AC is not closed by TEST-010.
   - CON-003 **Passing (local)** may stay (file defines services).
   - TEST-010: drop or mark plan **step 3** (bring-up / health) as not executed; do not implement it to satisfy this review.
   - TEST-013: do **not** retitle as clean-clone.

4. After (1)–(2) are in the repo: either record a one-line **owner attestation** that the documented steps were run on a clean machine, **or** leave the clean-machine slice Partial. Either satisfies NFR-001 AC. **Do not** mint a Compose e2e TEST solely to close LEAD-001.

### Should (same pass; nits; not 9/10 blockers)

5. **LEAD-002** (`architecture-decisions`, then `architecture` / error-handling): Narrow ADR-005 (and the architecture/error-handling echoes) to: state file is written but **not** restored; `--from-stage train` resumes from `feature_matrix.npz`; `--from-stage features` is same-process only (needs `ctx.store`). Optional: IMP-009 “resume where safe” → point at that sentence.

6. **LEAD-003** (`architecture`, `architecture-decisions`, glossary): Home/away/date matchup = **Future / not MVP**. MVP optional resolver = `provider_game_id` only. Do not add API fields.

### Must not

- Do not close LEAD-001 by only changing “Passing” prose.
- Do not add player ingest, GCP, auth, or ML-005 real-holdout claims.
- Do not claim remote CI green.
- Do not implement `save_state` load or home/away/date predict to “match the docs.”

---

## After those fixes: ≥9/10 from both reviewers?

**Yes — expected**, if Must items 1–4 are done (unambiguous command **and** honest labels; attestation or Partial for the clean-machine slice). Items 5–6 should ride along; leaving them open would still be nits, which the lead already treated as non-blocking.

Until Must 1–4 land, **do not** treat Grok’s prior 9/10 as current. The lead was right to reject ≥9/10 on LEAD-001.

---

## Lead overreach

| Item | Overreach? |
|---|---|
| LEAD-001 as a 9/10 blocker | **No** — valid on current repo |
| Ambiguous `python -m athletiq.pipeline` demo command | **No** — still in infrastructure.md + Compose comment |
| “Do not only relabel Passing” | **No** — agree |
| Mandating automated Compose bring-up → pipeline → API as the close | **Yes (remedy only)** — exceeds NFR-001 AC; honest docs + canonical command (+ owner attestation or Partial) suffice |
| Treating TEST-013/TEST-010 Status text as the lie | **Mild** — those Status lines are already qualified; the lie is traceability / FR-012 AC2 / missing README |
| LEAD-002, LEAD-003 as minors | **No** |

---

## Gate snapshot (unchanged by this ruling)

Gates 0–5 and Gate 7 **docs** remain Approved. LEAD-001 is **content/evidence drift** inside Approved SRS/traceability/devops, not a missing gate artifact. Gates 8–9 remain Draft. PRD acceptance remains unchecked (correct).

ADR-005 / ADR-008 consequences: **partially held** (resume claim; optional matchup prose). Other Accepted ADRs were not re-litigated; the lead’s ADR table is accepted except those two nits.

---

## Validation

- [x] No Grill-Me
- [x] No primary doc authorship (this file only)
- [x] LEAD-001…003 re-checked against current docs, contracts, Compose, CLI, and tests
- [x] Findings actionable and mapped to owning skills
- [x] Close bar stated: honest labels + canonical command; Compose e2e test **not** required
