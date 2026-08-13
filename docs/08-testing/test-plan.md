# Test plan

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.2

> Requirement-driven cases. **Canonical** req↔test map: `../03-requirements/traceability.md`.  
> **Approved** with Gate 7 strategy v1.0.0. Levels: one **primary** `Level` per suite; optional **Also** for nested cases (see `test-strategy.md`).

## Case template

```text
TEST-XXX
Requirement IDs:
IMP refs:
Dependencies:
Description:
Preconditions:
Steps:
Expected result:
Level: unit | integration | pipeline | ci
Also: (optional nested level)
Status: Planned | Implemented | Passing
```

---

### TEST-001 — Bootstrap, config, logging, secrets

- **Requirement IDs:** SEC-001, SEC-002, OPS-002, CON-001 (config knobs support NFR-001; **behavior** = TEST-013)  
- **IMP refs:** IMP-001  
- **Dependencies:** none  
- **Description:** Env config; falsifiable secret non-leakage; `.env.example` placeholders; seed/path knobs present.  
- **Preconditions:** Package installable.  
- **Steps:**
  1. Load config from env; assert values without committing real `.env`.  
  2. Inject sentinel `SUPER_SECRET_TEST_VALUE` into logging / error paths (including a forced exception and a retry-error path if available); assert **final log/HTTP error text does not contain the sentinel**.  
  3. Assert `.env.example` has placeholder keys only.  
  4. Assert config exposes seed, artifact path, raw path (mechanism for NFR-001 — not reproducibility itself).  
- **Expected result:** Sentinel never appears in outputs; placeholders only in examples.  
- **Level:** unit  
- **Status:** Passing

### TEST-002 — Schema and migrations

- **Requirement IDs:** FR-002 (contract), DR-002, CON-002, NFR-005, ADR-001, ADR-010  
- **IMP refs:** IMP-002  
- **Dependencies:** none  
- **Description:** Migrations/schema apply; DR-002 **MVP** themes plus reserved player tables; indexes; BIGINT (**ADR-010**); `schema_migrations`; second apply is idempotent.  
- **Preconditions:** Ephemeral Postgres.  
- **Steps:**
  1. Apply migration set to empty DB — succeeds.  
  2. Assert required tables exist (teams, games, team_game_stats, features; reserved players / player_game_stats; optional model_registry; schema_migrations).  
  3. Assert database-design indexes present.  
  4. Assert `game_id` / `team_id` / `player_id` are BIGINT-compatible.  
  5. Apply the **same** migration set again — succeeds; schema unchanged; no duplicate objects / corrupted state.  
- **Expected result:** Idempotent migrate; contract + ADR-010 hold. Empty reserved player tables after migrate-only is expected (CR-001).  
- **Level:** integration  
- **Status:** Passing (contract/static always; live migrate when `TEST_DATABASE_URL` set)

### TEST-003 — Provider adapter and raw ingest (fixtures)

- **Requirement IDs:** FR-001, CON-007, DR-001, SEC-001, ADR-011, ADR-006, CR-002  
- **IMP refs:** IMP-003  
- **Dependencies:** TEST-001  
- **Description:** Fixture-backed ingest to immutable raw FS; season window; retries without live network; mocked NBA Stats API pagination.  
- **Preconditions:** `tests/fixtures/provider/`; no API key required.  
- **Steps:**
  1. Ingest via fixture backend → raw files under configured path.  
  2. Re-run; assert immutability / batch layout per design.  
  3. Seasons outside active 2–3 window not ingested (or pruned).  
  4. API key only from env (unused API-Sports fallback).  
  5. **Also (unit):** retry helper — max 5, backoff+jitter, honor `Retry-After` (mocked HTTP/clock).  
  6. **Also (unit):** `NbaStatsApiProvider` with injected GET — multi-page newest-first, season filter, alias map, skip missing scores / non-NBA teams; no live HTTP.  
- **Expected result:** No live HTTP; raw landing correct.  
- **Level:** integration  
- **Also:** unit (retry helper; mocked nba-stats pages)  
- **Status:** Passing

### TEST-004 — Validate, load, report, idempotency

- **Requirement IDs:** FR-002, FR-013, DR-002, DR-003, OPS-002  
- **IMP refs:** IMP-004  
- **Dependencies:** TEST-002, TEST-003  
- **Description:** Valid load; skip+count noisy; grain-level idempotency; critical emptiness fails.  
- **Preconditions:** Schema + fixture raw.  
- **Steps:**
  1. Load valid batch → teams and games &gt; 0 for required seasons.  
  2. Inject invalid row → skip + report count; continue.  
  3. Re-run same raw batch → **no duplicate rows at natural grain:**  
     - `team_game_stats`: `(game_id, team_id)`  
     - `features`: `(game_id, feature_version)`  
     - games/teams: `provider_*` unique  
     - `player_game_stats` is **reserved** (CR-001) — not an MVP load grain; do not require player upserts.  
  4. Zero games for a required season → non-zero exit + inspectable log.  
- **Expected result:** DR-003 + FR-013 satisfied.  
- **Level:** integration  
- **Status:** Passing (in-memory curated store; Postgres adapter + TEST_DATABASE_URL integration when available)

### TEST-005 — SQL analytics

- **Requirement IDs:** FR-003, NFR-005  
- **IMP refs:** IMP-005  
- **Dependencies:** TEST-004  
- **Description:** Aggregations + windows return **exact expected** results on mini fixtures for **team** stats (FR-003 / CR-001).  
- **Preconditions:** Hand-built curated mini fixture with known answers (team_game_stats).  
- **Steps:**
  1. Rolling window over `game_start_time` → **exact** window membership / aggregates on the mini fixture (**MVP Must**).  
  2. Optional: in-memory top-scorer helper may exist for schema demo — it is **not** proof of loaded `player_game_stats` and is not a pipeline outcome.  
- **Expected result:** Query answers match fixture ground truth.  
- **Level:** unit  
- **Status:** Passing (in-memory; SQL templates asserted, not executed against Postgres)

### TEST-006 — Features, leakage, train/serve contract

- **Requirement IDs:** FR-004, ML-001, ML-002, ML-008, ADR-008  
- **IMP refs:** IMP-006  
- **Dependencies:** TEST-004  
- **Description:** No leakage; home orientation; cold start; feature contract/`feature_version` shared between train and API paths.  
- **Preconditions:** Mini timeline with known tip times.  
- **Steps:**
  1. Features for game at T use no stats from starts &gt; T (ML-001).  
  2. Label/orientation = home (ML-002).  
  3. &lt; `min_prior_games = 5` → season-to-date path.  
  4. **ML-008:** given the same `feature_version`, API preprocessing behavior **conforms to the training feature contract** (same definitions/preprocessing outcomes for a fixture vector). Do **not** require a specific import graph.  
  5. Persist uniqueness on `(game_id, feature_version)`.  
- **Expected result:** Leakage/cold-start/contract hold.  
- **Level:** unit  
- **Also:** integration (persist uniqueness)  
- **Status:** Passing

### TEST-007 — ML lifecycle (correctness + ML-005 quality gate)

- **Requirement IDs:** FR-005…008, ML-003…007, ML-009, CON-008, ADR-003, ADR-004, ADR-005  
- **IMP refs:** IMP-007  
- **Dependencies:** TEST-006  
- **Description:** One ML lifecycle suite with internal structure (not six TEST ids).  
- **Preconditions:** Feature table / synthetic timeline.  
- **Internal structure:**
  ```text
  TEST-007
  ├── Automated correctness (CI)
  │   ├── split correctness (~70/15/15 temporal)
  │   ├── baseline correctness (naive + domain-informed)
  │   ├── candidate training (LR + XGBoost)
  │   ├── validation-only selection (tie → LR)
  │   ├── test isolation (test scored only after pin)
  │   ├── artifact publication + lineage fields
  │   └── metrics report labels val vs test
  └── Quality gate / attestation (MVP-complete; not flaky PR unit)
      └── ML-005: selected model test log loss < domain-informed test log loss
  ```
- **Steps (automated):**
  1. Temporal split; no shuffle; approximate fractions on fixture (ML-003).  
  2. Baselines per ML-006; evaluate on same partitions (FR-005/006).  
  3. Train LR/XGB on train; select on **validation** log loss; tie → LR (ML-007).  
  4. Test metrics only after pin; selection metadata must not be test-driven.  
  5. Publish joblib + JSON lineage (ML-009).  
  6. Metrics report distinguishes validation vs test (ML-004).  
  7. Optional CI smoke: comparison *function* on tiny synthetic vectors (not ML-005 attestation).  
- **Steps (quality gate / attestation):**
  8. **Freeze** baseline definition, `dataset_version`, split boundaries, `feature_version`, metric (= log loss).  
  9. On agreed fixture (or local full run), assert min(LR, XGB) **test** log loss &lt; domain-informed **test** log loss (**ML-005**); write eval report. Changing freeze inputs after seeing test metrics voids the gate.  
- **Expected result:** Correctness green in CI; ML-005 attested for MVP complete.  
- **Level:** integration  
- **Also:** unit (pure split/baseline helpers); pipeline (full attestation run if not in default PR)  
- **Status:** Passing (automated + synthetic ML-005 mark)

### TEST-008 — Prediction API contract and errors

- **Requirement IDs:** FR-009, FR-014, CON-004, NFR-002, NFR-004, ADR-008, ADR-009  
- **IMP refs:** IMP-008  
- **Dependencies:** TEST-006; TEST-007 for full pin (stub allowed earlier); **TEST-014** for pin↔artifact deep check  
- **Description:** OpenAPI endpoints/errors; no auth; no silent baseline; NFR-002/004; lineage fields match pin.  
- **Preconditions:** App + fixture DB + pin (or stubs for negatives).  
- **Steps:**
  1. Health 200 / 503 `model_unavailable` | `db_unavailable`.  
  2. Predict → 200 with `p_home_win`, `home_win_pred`, `model_version`, `feature_version`.  
  3. Assert returned `model_version` / `feature_version` **equal the pinned artifact metadata** (not merely present).  
  4. Unknown game → 404 `game_not_found`; game lacking features for **pinned** `feature_version` → 404 `features_not_found` (explicit version mismatch).  
  5. Missing pin → 503 `model_unavailable` (never baseline).  
  6. Invalid params → 400.  
  7. No auth / no multi-tenant paid-account hooks (ADR-009, NFR-002).  
  8. OpenAPI/design cite no hard SLO (NFR-004).  
- **Expected result:** Contract + lineage consistency with pin.  
- **Level:** integration  
- **Status:** Passing (TestClient + fixture pin/features; deep pin↔artifact owned by TEST-014)

### TEST-009 — Pipeline orchestration

- **Requirement IDs:** FR-011, CON-006, CON-001, OPS-002, ADR-005  
- **IMP refs:** IMP-009  
- **Dependencies:** TEST-003…007 for full path (stubs OK earlier)  
- **Description:** Thin `run_pipeline.sh` → CLI; failures non-zero + logs.  
- **Preconditions:** Fixture/offline mode.  
- **Steps:**
  1. Happy path → exit 0; logs/artifacts present.  
  2. Forced stage failure → non-zero; stage identifiable in logs.  
  3. Script is thin wrapper to CLI (smoke — not a shell unit zoo).  
- **Expected result:** OPS-002 failure reporting.  
- **Level:** pipeline  
- **Status:** Passing (offline provider + CLI failure path; bash content smoke)

### TEST-010 — Compose deployment topology

- **Requirement IDs:** FR-012, CON-003, ADR-001, ADR-004, ADR-006  
- **IMP refs:** IMP-010  
- **Dependencies:** TEST-002; TEST-008 preferred for API health  
- **Description:** Verifies **`docker-compose.yml`** application deployment topology (not GHA).  
- **Preconditions:** Docker where offered.  
- **Steps:**
  1. `docker compose config` validates.  
  2. Services `database`, `etl`, `api` declared; raw + artifact volumes present.  
- **Expected result:** Compose **file** matches architecture (CON-003 / FR-012 topology). Bring-up, pipeline, and `/v1/health` are **not** this suite — see NFR-001 / root README.  
- **Level:** integration  
- **Status:** Passing (static topology always; `docker compose config` when daemon available)

### TEST-011 — CI workflow topology

- **Requirement IDs:** OPS-001, CON-005, NFR-003, SEC-002  
- **IMP refs:** IMP-011  
- **Dependencies:** none for static asserts  
- **Description:** Verifies **`.github/workflows/*.yml`** — jobs exist and **`needs`/DAG** enforce intended sequencing (not YAML textual order).  
- **Preconditions:** Workflow file present.  
- **Steps:**
  1. Assert jobs (or equivalent steps) for **lint**, **unit**, **integration**, **image build** exist.  
  2. Assert declared dependencies (`needs:` or documented equivalent) enforce the intended DAG — e.g. integration after unit (and lint as required by design); image after tests. Parallel lint∥unit is allowed if `needs` still gate integration/image correctly.  
  3. Test jobs do not require live `API_SPORTS_KEY` (fixture mode).  
  4. Secret hygiene / optional scanning checklist.  
  5. Image build present (build-only OK).  
- **Expected result:** OPS-001 + NFR-003.  
- **Level:** ci  
- **Status:** Passing (static workflow DAG + NFR-003/SEC-002 asserts)

### TEST-012 — Methodology and limitations disclosure

- **Requirement IDs:** FR-010  
- **IMP refs:** IMP-012, IMP-008  
- **Dependencies:** TEST-007, TEST-008  
- **Description:** Model card / methodology + `/v1/model` summary.  
- **Preconditions:** Published metadata + API.  
- **Steps:**
  1. Methodology artifact mentions baselines-not-served, temporal splits, log loss primary, limitations.  
  2. GET `/v1/model` aligns with FR-010 / card.  
- **Expected result:** Honest disclosure.  
- **Level:** integration  
- **Status:** Passing (model-card.md + `/v1/model` alignment)

### TEST-013 — Training reproducibility

- **Requirement IDs:** NFR-001, ML-009  
- **IMP refs:** IMP-001, IMP-007  
- **Dependencies:** TEST-006, TEST-007 (machinery)  
- **Description:** Same raw snapshot + code/config/seed → equivalent features, splits, selection, and metrics within **documented** tolerances. This is **training-repeatability**, not a clean-clone Compose demo (NFR-001 clean-machine AC).  
- **Preconditions:** Fixed fixture dataset; documented tolerance (exact match preferred for deterministic paths).  
- **Steps:**
  1. Run feature generation twice with identical inputs/config/seed.  
  2. Assert identical `feature_version` and feature values where deterministic.  
  3. Run train/eval twice with same seed.  
  4. Assert identical train/validation/test partition membership.  
  5. Assert same selected model family/version pin.  
  6. Assert metrics identical or within documented numerical tolerance.  
  7. Assert lineage metadata identifies the same `dataset_version` / config / `code_commit`.  
- **Expected result:** Reproducibility demonstrated (not merely knobs present).  
- **Level:** integration  
- **Also:** pipeline (optional full-path attestation)  
- **Status:** Passing (controlled synthetic fixture; exact structure/selection; numeric exact on pinned toolchain — see test module docstring)

### TEST-014 — Published artifact ↔ API compatibility

- **Requirement IDs:** FR-014, ML-009, ADR-003, ADR-008  
- **IMP refs:** IMP-007, IMP-008  
- **Dependencies:** TEST-007, TEST-008  
- **Description:** Metadata, on-disk artifact, and API-loaded model agree; incompatible `feature_version` refused.  
- **Preconditions:** Published pin + artifacts volume.  
- **Steps:**
  1. Read published JSON metadata (`model_version`, `feature_version`, artifact path/hash if present).  
  2. Assert API `/v1/model` and a successful `/v1/predict` use **that same** `model_version` / artifact (no silent older load).  
  3. Negative: pin requires `feature_version=vN` but DB only has `vN-1` for the game → prediction fails with `features_not_found` (or documented equivalent) — never invents features.  
- **Expected result:** Artifact/API consistency invariant held.  
- **Level:** integration  
- **Status:** Passing (pin→artifact path identity; success + composite-key negatives)

## Open (non-blocking)

- Exact ML-005 attestation fixture / `dataset_version` — choose at IMP-007; freeze before gate.  
- Compose smoke on every PR vs nightly — devops CI doc.  
- Remote GitHub Actions green — workflow defined; local verification does not claim remote green.
