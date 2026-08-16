# Test plan

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.2.0

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
- **IMP refs:** IMP-002, IMP-019  
- **Dependencies:** none  
- **Description:** Migrations/schema apply; DR-002 themes including loaded players; CR-005 ledger tables after 003; indexes; BIGINT (**ADR-010**); `schema_migrations`; second apply is idempotent.  
- **Preconditions:** Ephemeral Postgres.  
- **Steps:**
  1. Apply migration set to empty DB — succeeds.  
  2. Assert required tables exist (teams, games, team_game_stats, features, players, player_game_stats; optional model_registry; schema_migrations). After **003**: `users`, `wallets`, `ledger_entries`, `stakes`.  
  3. Assert database-design indexes present (including partial unique open stakes).  
  4. Assert `game_id` / `team_id` / `player_id` / `user_id` are BIGINT-compatible.  
  5. Apply the **same** migration set again — succeeds; schema unchanged; no duplicate objects / corrupted state.  
- **Expected result:** Idempotent migrate; contract + ADR-010 hold. Empty player tables after migrate-only (no load) is expected. Seed demo users after 003 (TEST-022).  
- **Level:** integration  
- **Status:** Passing (local); Passing (remote)

### TEST-003 — Provider adapter and raw ingest (fixtures)

- **Requirement IDs:** FR-001, FR-021, CON-007, DR-001, SEC-001, ADR-011, ADR-006, CR-002  
- **IMP refs:** IMP-003, IMP-020  
- **Dependencies:** TEST-001  
- **Description:** Fixture-backed ingest to immutable raw FS; season window; retries without live network; mocked NBA Stats API pagination. **CR-005:** live mapper **keeps** null-score games (FR-021); does not hardcode `Finished`.  
- **Preconditions:** `tests/fixtures/provider/`; no API key required.  
- **Steps:**
  1. Ingest via fixture backend → raw files under configured path.  
  2. Re-run; assert immutability / batch layout per design.  
  3. Fixture path loads only authored fixture seasons (not a historical dump). Live NBA has **no** age cap (DR-001 / TEST-025) — do not assert a 3-season live prune.  
  4. API key only from env (unused API-Sports fallback).  
  5. **Also (unit):** retry helper — max 5, backoff+jitter, honor `Retry-After` (mocked HTTP/clock).  
  6. **Also (unit):** `NbaStatsApiProvider` with injected GET — multi-page newest-first; alias map; **keep** games whose points are null (status not hardcoded `Finished`); still skip non-NBA / unmappable teams; no live HTTP. In-progress + player boxes: TEST-025.  
- **Expected result:** No live HTTP; raw landing correct; null-score NBA rows are not dropped solely for missing scores.  
- **Level:** integration  
- **Also:** unit (retry helper; mocked nba-stats pages)  
- **Status:** Passing (local); Passing (remote)

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
     - `player_game_stats`: `(game_id, player_id)` when player fixtures are loaded (CR-004 / TEST-016). Live NBA boxes: TEST-025. Not reserved.  
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

### TEST-015 — League/sport schema and WNBA fixtures

- **Requirement IDs:** FR-016, DR-001, DR-002, ADR-013  
- **IMP refs:** IMP-013, IMP-014  
- **Dependencies:** TEST-002, TEST-003  
- **Description:** Schema has sport/league; fixture ingest loads a small NBA set and WNBA files; CI uses no live WNBA HTTP. CR-005 expands WNBA seasons via TEST-026; this suite still proves `league` split.  
- **Preconditions:** `tests/fixtures/provider/`.  
- **Steps:**
  1. Apply migrations including 002 — `games.league`, `odds_snapshots` exist.  
  2. Fixture ingest with depth 3 writes NBA 2022–2024 plus WNBA files.  
  3. Load distinguishes `league=nba` vs `league=wnba`.  
- **Expected result:** Both leagues present; no live HTTP.  
- **Level:** integration  
- **Also:** unit (fixture provider)  
- **Status:** Passing (local unit; live migrate when `TEST_DATABASE_URL` set)

### TEST-016 — Player load and aggregated features (no leakage)

- **Requirement IDs:** FR-017, FR-004, ML-011, ML-001, DR-003  
- **IMP refs:** IMP-014, IMP-015  
- **Dependencies:** TEST-004, TEST-006  
- **Description:** Players and player_game_stats upsert; top-5 L5 aggregates ignore post-tip lines; idempotent grain.  
- **Preconditions:** Fixture players + box scores.  
- **Steps:**
  1. Load twice — no duplicate `(game_id, player_id)`.  
  2. Build features; assert player keys present.  
  3. Inject a post-tip player line — feature values unchanged.  
- **Expected result:** Leakage guard holds; grain unique.  
- **Level:** unit  
- **Also:** integration (postgres upsert when DB available)  
- **Status:** Passing (local)

### TEST-017 — Synthetic odds labeled

- **Requirement IDs:** FR-018, DR-004, CON-009, ADR-012  
- **IMP refs:** IMP-014, IMP-017  
- **Dependencies:** TEST-008  
- **Description:** Snapshot load; predict returns `market_source=synthetic` or null if missing; no book HTTP.  
- **Preconditions:** Fixture odds file.  
- **Steps:**
  1. Load odds_snapshots; rerun idempotent.  
  2. Predict with snapshot → `market_p_home_win` in [0,1], source synthetic.  
  3. Predict without snapshot → fields null/omitted.  
- **Expected result:** Labeled comparison only.  
- **Level:** unit  
- **Status:** Passing (local)

### TEST-018 — Per-league pin routing

- **Requirement IDs:** FR-019, ML-010, ADR-013  
- **IMP refs:** IMP-016, IMP-017  
- **Dependencies:** TEST-007, TEST-008  
- **Description:** NBA game uses NBA pin; WNBA game uses WNBA pin; missing pin → model_unavailable.  
- **Preconditions:** Two published pins or one missing.  
- **Steps:**
  1. Train fixture both leagues.  
  2. Predict NBA id → nba model_version prefix/league.  
  3. Predict WNBA id → wnba pin.  
  4. Drop wnba pin → WNBA predict 503 model_unavailable.  
- **Expected result:** No pooled classifier.  
- **Level:** unit  
- **Status:** Passing (local)

### TEST-019 — Gamecast UI reconstruction

- **Requirement IDs:** FR-015, FR-020, CON-009  
- **IMP refs:** IMP-018  
- **Dependencies:** TEST-008  
- **Description:** GET / HTML is the broadcast gamecast (producer bar + Home/Away split + Game ID lookup), league control, Market P labeled synthetic, **no** stake/payout/moneyline chrome **on this page**. CR-005 stake/settle copy lives on `/slate` (TEST-023/028). Producer-bar links to `/slate` and `/board` (TEST-028).  
- **Preconditions:** FastAPI TestClient.  
- **Steps:**
  1. GET / is HTML.  
  2. Static JS/CSS reference league control, split, and Market P.  
  3. Assert no wager/stake/payout/moneyline copy.  
- **Expected result:** Gamecast surface present; not a book; no stake chrome on `GET /`.  
- **Level:** unit  
- **Status:** Passing (local)

---

## CR-005 cases (Passing)

### TEST-020 — Scheduled/unplayed persist; P from prior history only

- **Requirement IDs:** FR-001, FR-021, DR-006, ML-001  
- **IMP refs:** IMP-019, IMP-020, IMP-021  
- **Dependencies:** TEST-002, TEST-004, TEST-006  
- **Description:** Scheduled games persist with null scores and status not Finished. Feature/`P(home_win)` rows use prior **completed** history only.  
- **Preconditions:** Fixture includes at least one scheduled NBA row and one scheduled WNBA row.  
- **Steps:**
  1. Load fixtures — scheduled rows exist; scores null; status ≠ Finished.  
  2. Build features for a scheduled game — values do not use that game’s missing box.  
  3. Training labels exclude non-Finished games.  
- **Expected result:** Unplayed rows stored; no leakage from the unplayed game itself.  
- **Level:** integration  
- **Also:** unit (feature builder)  
- **Status:** Passing (local); Passing (remote)

### TEST-021 — Even-money settle idempotent; pre-tip cancel/replace

- **Requirement IDs:** FR-023, DR-003, DR-005, CON-009, ADR-014, ADR-015  
- **IMP refs:** IMP-022  
- **Dependencies:** TEST-020, TEST-022  
- **Description:** Pipeline settles when a game is ingested as Finished. Correct pick returns stake + equal house credit; wrong pick forfeits stake. Second run does not double-credit. Cancel/replace allowed only before tip. `/slate` does not settle.  
- **Preconditions:** Seeded demo user; scheduled then Finished fixture/load.  
- **Steps:**
  1. `demo-1` starts at **1000**. Place amount **10** (`replace=false`). Unlocked balance is **990**. Cancel restores **1000**.  
  2. Place **10** again; then `POST /v1/stakes` with `replace=true`, amount **20**, same game — still one open stake; unlocked **980**.  
  3. Ingest that game Finished with **matching** side → `demo-1` balance = **pre-lock 1000 + 20 = 1020** (equivalently unlocked 980 + 2×20). House decreases by 20.  
  4. `demo-2` starts at **1000**. Place **10**; ingest Finished with **opposite** side → balance = **990** (stake gone). House unchanged for a loss.  
  5. Re-run pipeline — neither balance nor ledger totals change (no double-credit).  
  6. After tip, cancel / new stake / replace rejected (`stake_window_closed`).  
  7. `/slate` does not settle (display only).  
- **Expected result:** Even-money win and lose; replace works before tip; idempotent settle; copy stake/settle not odds/juice/moneyline.  
- **Level:** integration  
- **Also:** unit (settle math)  
- **Status:** Passing (local); Passing (remote)

### TEST-022 — Integer stake bounds; one open stake per (user, game)

- **Requirement IDs:** FR-022, FR-023, DR-005, ADR-014  
- **IMP refs:** IMP-019, IMP-023  
- **Dependencies:** TEST-002  
- **Description:** Seed `demo-1`/`demo-2` at 1000 e-coins; house wallet exists; unknown user rejected; amount integer min 1 max unlocked; one open stake per `(user, game)`.  
- **Preconditions:** Migration 003 applied.  
- **Steps:**
  1. After migrate, balances are 1000; house ≥ enough for even-money.  
  2. Amount 0 / non-integer / over unlocked → `invalid_request` or `insufficient_balance`.  
  3. Second open stake with `replace=false` → `duplicate_open_stake`. `replace=true` is TEST-021.  
  4. Unknown slug and `house` → `user_not_found`.  
- **Expected result:** Bounds and uniqueness hold; no passwords/cookies.  
- **Level:** integration  
- **Also:** unit  
- **Status:** Passing (local); Passing (remote)

### TEST-023 — `/slate` next-20 + open stakes + `?user=`

- **Requirement IDs:** FR-024, FR-022, ADR-016  
- **IMP refs:** IMP-023  
- **Dependencies:** TEST-020, TEST-022  
- **Description:** `GET /slate` HTML + JSON: next 20 unplayed pre-tip games (NBA+WNBA mixed) plus that user’s open stakes; switcher updates `?user=`.  
- **Preconditions:** FastAPI TestClient; seeded users; mixed scheduled fixtures.  
- **Steps:**
  1. GET `/slate?user=demo-1` is HTML; JSON slate has ≤20 upcoming plus open stakes.  
  2. Switch to `demo-2` — URL query changes; balances differ if stakes differ.  
  3. Finished games are absent from the upcoming table.  
- **Expected result:** Next-20 rule; query-param identity; stake/settle copy allowed.  
- **Level:** unit  
- **Also:** integration  
- **Status:** Passing (local); Passing (remote)

### TEST-024 — `/board` in-progress; gamecast still no score/clock

- **Requirement IDs:** FR-025, FR-015, FR-026, CON-009, ADR-016  
- **IMP refs:** IMP-022, IMP-023  
- **Dependencies:** TEST-019, TEST-025  
- **Description:** `GET /board` shows in-progress only (scores allowed; clock only if provided). `GET /` still has no score/clock/quarter. No invented clock.  
- **Preconditions:** Fixture or injected in-progress row.  
- **Steps:**
  1. GET `/board` is HTML; in-progress scores visible when present.  
  2. GET `/` HTML/JS still has no score/clock/quarter.  
  3. Scheduled-only dataset → board empty (or no in-progress rows).  
- **Expected result:** Third surface is the board; gamecast lock holds.  
- **Level:** unit  
- **Also:** integration  
- **Status:** Passing (local); Passing (remote)

### TEST-025 — nba-stats maps null scores, in-progress, player boxes (injected HTTP)

- **Requirement IDs:** FR-001, FR-017, FR-021, FR-026, FR-027, DR-001, ADR-017, NFR-003  
- **IMP refs:** IMP-020, IMP-022  
- **Dependencies:** TEST-003  
- **Description:** Injected `get_json` payloads: persist null-score scheduled games; upsert in-progress; persist player boxes. **No live HTTP.**  
- **Preconditions:** Unit inject of provider HTTP.  
- **Steps:**
  1. Payload with null points → game stored, not dropped; status not hardcoded Finished.  
  2. Payload with scores + non-Finished status → in-progress upsert.  
  3. Payload with `playerGameBasicStats` (or equivalent) → `player_game_stats` rows.  
  4. Board-poll helper uses newest-page mapping, not full-history paging.  
- **Expected result:** Live mapper no longer returns `[]` for NBA boxes; CI never calls the host.  
- **Level:** unit  
- **Status:** Passing (local); Passing (remote)

### TEST-026 — WNBA fixture 2021–2025 + 2026 scheduled

- **Requirement IDs:** FR-016, DR-001, NFR-003  
- **IMP refs:** IMP-021  
- **Dependencies:** TEST-015  
- **Description:** Fixture provider loads five completed WNBA seasons 2021–2025 plus 2026 scheduled rows. No live WNBA HTTP.  
- **Preconditions:** Authored fixture files.  
- **Steps:**
  1. Load fixture — WNBA seasons 2021–2025 present; 2026 scheduled rows have null scores.  
  2. Assert no network call.  
- **Expected result:** Authored window only; CI stays fixture.  
- **Level:** integration  
- **Also:** unit (fixture provider)  
- **Status:** Passing (local); Passing (remote)

### TEST-027 — Retrain protocol: val select, test once; CI pin unchanged

- **Requirement IDs:** FR-028, ML-005, ML-007, ML-012, ADR-003  
- **IMP refs:** IMP-024  
- **Dependencies:** TEST-007  
- **Description:** CR-005 retrain uses validation for selection and test once. Same `feature_version`. CI 48-game fixture pin identity is not replaced. Old live log loss 0.623 is not an assert.  
- **Preconditions:** Fixture train path (small) plus documented pin-map shape.  
- **Steps:**
  1. Selection reads validation metrics only.  
  2. Test metrics written once; no second test pass in the same job.  
  3. Fixture `selected_pin.json` for the 48-game toy remains the existing pin identity (or a documented distinct CI pin).  
- **Expected result:** Protocol holds; CI pin unchurned.  
- **Level:** unit  
- **Status:** Passing (local); Passing (remote)

### TEST-028 — Producer-bar three-way links; no book language on `/slate` and `/board`

- **Requirement IDs:** FR-015, FR-024, FR-025, CON-009, ADR-016  
- **IMP refs:** IMP-023  
- **Dependencies:** TEST-019  
- **Description:** Producer bar on `/`, `/slate`, `/board` links the three. `/slate` and `/board` forbid odds/juice/moneyline/payout/wager. `/slate` **may** contain stake/settle. `GET /` still forbids stake chrome (TEST-019).  
- **Preconditions:** FastAPI TestClient; static HTML/JS.  
- **Steps:**
  1. Each surface HTML contains links to the other two paths.  
  2. `/slate` and `/board` have no odds/juice/moneyline/payout/wager copy.  
  3. `/slate` may include stake/settle; `/` must not.  
- **Expected result:** Three-way instrument family; not a book.  
- **Level:** unit  
- **Status:** Passing (local); Passing (remote)

## Open (non-blocking)

- Exact ML-005 attestation fixture / `dataset_version` — choose at IMP-007; freeze before gate.  
- Compose smoke on every PR vs nightly — devops CI doc.  
- Remote GitHub Actions green — attested CR-004 `491c5c0` ([31913410157](https://github.com/RoeeHadar/AthletIQ/actions/runs/31913410157)); CR-005 `657e5a1` ([31956566628](https://github.com/RoeeHadar/AthletIQ/actions/runs/31956566628)).
