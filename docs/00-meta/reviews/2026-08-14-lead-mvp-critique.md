# Lead review — MVP ready for owner manual test

Status: Complete  
Date: 2026-08-14  
Reviewer role: Lead manager / independent engineering reviewer  
Model: Cursor Grok Extra High (`cursor-grok-4.6-xhigh`), owner-authorized substitute for GPT 5.6 Sol (API limit)  
Scope: Full MVP critique against Approved PRD v1.0.4 acceptance criteria; IMP DoD code review of application source at `4a2f713`; live LR `ConvergenceWarning` disposition  
Baseline reviews (not reopened): docs 9/10; Step 1 QA; GHA `4a2f713`; NFR-001 attest; honesty+QA APPROVE with notes

## Decision

**APPROVE with notes.**

AthletIQ at commit `4a2f713ed4cf58966358c6dd12b3ea77813d905a` is **ready for owner manual test** on the clean-clone Compose fixture stack. The IMP DoD **code review** gate is performed by this document. Application source in the developer working tree is unchanged from that SHA.

This is **not** a rubber stamp that the owner has already ticked PRD acceptance. Every PRD MVP checkbox remains `[ ]`. Closeout **may proceed** after the notes below: disclose the live logistic-regression solver warning, then tick PRD boxes and IMP code-review boxes through the owning workflows — this review does not tick them.

LEAD-001 remains **closed**. Canonical Compose still requires `--store postgres`. TEST-010 is static topology; TEST-013 is training-repeatability; NFR-001 is the clean-clone attest. The two runtime stacks are not conflated.

## Notes that condition PRD closeout (not a REJECT)

1. **Live LR `ConvergenceWarning`.** The working-tree live pin is `logistic_regression-v1` with `solver=lbfgs`, `max_iter=500`. Solver non-convergence must be **disclosed as a known limitation** on the model card (and ideally the `/v1/model` limitations text) **before** criterion 12 / live ML-005 is treated as PRD-ticked. **Do not** retune `max_iter`, scaling, or regularization against the already-observed test log loss `0.6231052772493764`. A new test-isolated config is allowed only if frozen without using that test number to choose it. The attested serving stack is **XGBoost**, so owner manual test of the README Compose path is not blocked.
2. **Commit the already-drafted README honesty** (`Remote CI green deferred` at `4a2f713` vs working-tree wording that records run `31753742525`). Identified in the NFR-001 review; still uncommitted. Not a product defect.
3. **Lineage gap (non-blocking):** published metadata records `code_commit: null` (pipeline never stamps a git SHA inside Compose). ML-009 field is present; dataset/feature/training_config are recorded. Optional later improvement — not a PRD blocker.

No blocking functional, security, or honesty defects. CR-001 is not reopened. No Compose e2e pytest. No `API_SPORTS_KEY` / signup URLs. No player ingest, GCP, or application auth demanded.

## Dual-stack lock (independently corroborated)

| Stack | Where | Serving? | Evidence this review |
|---|---|---|---|
| **NFR-001 attest** | `C:\Users\roeeh\AthletIQ-nfr001-attest`, Compose project `athletiq-nfr001-attest`, ports `127.0.0.1:5432` / `8000` | **Yes** (only stack on those ports) | HEAD `4a2f713ed4cf58966358c6dd12b3ea77813d905a`; 48 games / 48 feature rows; pin **`xgboost-v1`** / `team_l5_l10_v1`; players=0 |
| **Working-tree live** | Developer repo; Compose **not** running; volumes `athletiq_pgdata` / `athletiq_artifacts` / `athletiq_raw_data` kept | **No** | Batch `20260813T231504Z`; **2640** games (**2023: 1319**, **2024: 1321**); 30 teams; pin **`logistic_regression-v1`**; test log loss **0.6231052772493764**; `used_test_for_selection: false` |

`GET http://127.0.0.1:8000/v1/model` returning `xgboost-v1` is the attest fixture pin. It does **not** contradict the live working-tree pin.

Working-tree **git** does not claim attest runtime came from this tree’s Compose. Committed README at `4a2f713` does not mention the attest clone. Working-tree README (uncommitted) states NFR-001 was attested on a clean clone of `main` at `4a2f713`, not the developer working tree.

## Per-PRD-criterion evidence

Do **not** tick these in `docs/02-product/PRD.md` from this review. After the owner accepts this APPROVE-with-notes, the **Tick?** column is the honest closeout recommendation.

| # | Criterion | Verdict | Tick? | Evidence |
|---|---|---|---|---|
| 1 | Clean environment can execute documented setup | **Met** | Yes after notes 2 (docs commit) | NFR-001 review APPROVE; this review: attest clone SHA `4a2f713`, project `athletiq-nfr001-attest` running 20h, `GET /v1/health` `{"status":"ok"}`, `GET /v1/model` `xgboost-v1`. README copy-paste includes `--store postgres --provider fixture`. |
| 2 | Historical NBA ingested for 2 Must completed seasons | **Met** (attestation, not pytest) | Yes | Live raw `games_2023.json` **1319**, `games_2024.json` **1321** (counted this review). Validation report: `games_loaded=2640`, `required_seasons=[2023,2024]`, `teams_loaded=30`. CLI: `--provider nba-stats --seasons 2023 2024`. Fixture CI/demo is a different stack. |
| 3 | ETL validation completes; reproducible validation report | **Met** | Yes | Code writes `artifacts/reports/validation_{batch}.json` (`write_validation_report`). Live report `validation_20260813T231504Z.json` present on `athletiq_artifacts`. TEST-004 Passing. |
| 4 | Required relational data persisted (teams, games, team stats); players unused | **Met** | Yes | Live: 30 teams, 2640 games, 5280 `team_game_stats` upserts. Attest DB: teams=2, games=48, tgs=96, **players=0**, **pgs=0**. Load path upserts teams/games/team_game_stats only (CR-001). |
| 5 | Required SQL analytics execute successfully | **Met** | Yes | FR-003 bar is TEST-005 (in-memory clone of team rolling windows), not live-Postgres execution. TEST-005 3 passed this QA. `ROLLING_TEAM_POINTS_SQL` is the MVP Must. Top-scorer SQL is a reserved helper (CR-001) — not demanded as a pipeline outcome. |
| 6 | Features without temporal leakage vs prediction time | **Met** | Yes | Builder filters `game_start_time < tip`. TEST-006 leakage + cold start (`min_prior_games=5`) + train/serve vector contract (18 keys, `team_l5_l10_v1`). TEST-006 5 passed. |
| 7 | Baseline evaluated on holdout | **Met** | Yes | Naive + domain-informed scored on the **same** test partition. Live test: naive log loss 15.613; domain-informed 10.990 / acc 0.682. Fixture pin metadata also records both. Baselines never served (`baselines_served: false` on `/v1/model`). |
| 8 | Logistic regression evaluated on same holdout | **Met** | Yes, with note 1 | Live val log loss 0.6195; test 0.6231; selected. Fixture also trained LR (not selected). `training_config` records `C=1.0`, `max_iter=500`, `lbfgs`, `random_state=42`. |
| 9 | XGBoost evaluated on same holdout | **Met** | Yes | Live val log loss 0.6271 (not selected). Fixture selected XGBoost; attest `/v1/model` serves `xgboost-v1`; test log loss 0.0507 on 48-game toy set (model-card limitation 3). |
| 10 | Evaluation results reproducible from documented steps | **Met** with grain | Yes | **Fixture:** NFR-001 attest + TEST-013. **Live 0.623:** one operator run; this review corroborated frozen artifacts, did **not** re-call NBA Stats. Documented live command exists in README. Numeric live replay is provider-dependent — do not claim bit-identical re-ingest. |
| 11 | Prediction API returns valid binary + probability | **Met** | Yes | Attest `GET /v1/predict?game_id=48` → 200, `home_win_pred: true`, `p_home_win: 0.964…` in `[0,1]`, lineage `xgboost-v1` / `team_l5_l10_v1`. Unknown id → 404 `game_not_found`. Missing query → 400 `invalid_request`. OpenAPI aligned. |
| 12 | Predictions accompanied by methodology and known limitations | **Met for fixture API; live pin disclosure incomplete** | **Hold until note 1** | Model card + `/v1/model` methodology (home-win, ~70/15/15, val log loss, tie→LR, baselines never served, `min_prior_games=5`, `FEATURE_VERSION`). Live LR non-convergence is **not** in the card. TEST-012 Passing. |
| 13 | Unit and integration tests pass | **Met** | Yes | This review: `python scripts/crews/qa/run_qa.py` exit 0, verdict **ACCEPT**. TEST-001…014 all PASS (TEST-002: 1 skip without `TEST_DATABASE_URL` — honest). Known non-blocking: runner prints “43 Must” = 42 Must + NFR-005 Should. |
| 14 | Container image build succeeds | **Met** | Yes | GHA `image` job success on `4a2f713` ([31753742525](https://github.com/RoeeHadar/AthletIQ/actions/runs/31753742525)). TEST-011 asserts Dockerfiles. Attest stack built and running. |
| 15 | GitHub Actions passes the agreed path | **Met** | Yes | Same run: `push`/`main`, conclusion `success`, head SHA `4a2f713…`. lint ∥ unit → integration → image. NFR-003 held (no live provider, no `secrets.API_SPORTS_KEY`). Reconfirmed with `gh` this review. |
| 16 | Documentation gates for the MVP slice | **Met** | Yes | Gates **0–5 and 7 Approved**; Gate 6 IMP-001…012 **Done**; binding ADRs **001, 003–006, 008–011** Accepted (002 Superseded; 007 Proposed / out of MVP). PRD checkboxes still unchecked (honest). Gate 8/9 not an MVP product Must. |
| 17 | No secrets committed | **Met** | Yes | `.env` gitignored and untracked; `.env.example` has empty `API_SPORTS_KEY=`. Local `.env` key is empty. `git grep` found no `sk-` tokens and no live key values. TEST-001/011 Passing. Compose uses demo `athletiq`/`athletiq` placeholders only. |

**Non-goals respected:** no betting, mobile, SaaS, in-game, paid accounts, production ML ops, player ingest, GCP, or application auth added or demanded.

## Code review (IMP DoD)

Reviewed application/contracts at **`4a2f713`** (working-tree diffs are docs/memory/skills/QA labels only — not product code).

### Findings

| ID | Severity | Finding | Owning skill |
|---|---|---|---|
| CRIT-001 | **Note (closeout)** | Live selected LR: `lbfgs` `max_iter=500`, no feature scaling. Mixed-scale L5/L10 points vs win rates is a classic non-convergence setup. Metric `0.623` is a real output of that fit; it is not a fully converged MLE. Disclose; do not peek-tune. | `architecture` (model card) |
| CRIT-002 | Minor | `code_commit` always `null` — `run_train_select_publish` never receives a SHA. | optional later IMP; not required for PRD |
| CRIT-003 | Nit | IMP plan “Proposed repo layout” still says `provider/ # API-Sports adapter`. Runtime is ADR-011 `nba_stats.py` + fixture + unused API-Sports fallback. | `implementation-planning` |
| CRIT-004 | Observation | Domain-informed / naive baselines emit hard 0/1 probabilities, so log loss is near the clip epsilon when they are wrong. ML-005 is therefore easy relative to a calibrated baseline. This **matches the locked Grill-Me definitions** — do not change the baseline to chase a stricter gate. Optional model-card sentence only. | `architecture` (optional) |
| CRIT-005 | Observation | `NbaStatsApiProvider.PAGE_SIZE = 100` vs Charter/memory “pageSize effectively 50”. If the API caps at 50, behavior is still “effective 50.” Align comment/docs if touched. | `architecture` / IMP-003 note |

No blocking design↔contract↔code drift on the MVP slice:

| Layer | Check | Result |
|---|---|---|
| DB | design envelope `{values, label_*, cold_start_*}` vs `schema.sql` JSONB vs `PostgresFeatureStore` | Aligned; legacy bare-map reader present |
| DB | BIGINT / reserved players / indexes | `schema.sql` = `001_initial.sql`; TEST-002 |
| API | OpenAPI `game_id` string, optional `provider_game_id`, no auth, no SLO, error codes | Routes + `TestClient` match |
| ML | `FEATURE_VERSION=team_l5_l10_v1`, `MIN_PRIOR_GAMES=5`, temporal split, val-only select, tie→LR, test once, baselines never served | Code + live pin metadata + attest `/v1/model` |
| Store | CLI default `memory`; Compose **must** `--store postgres`; API `ATHLETIQ_STORE=postgres` | Held |
| Provider | `--provider nba-stats` no key; CI fixture-only | Held |
| `# Implements` | IMP-listed modules annotated; tests use TEST ids only | Held |

`select_model` prefers lower validation log loss and LR on numerical ties. Live selection LR 0.6195 < XGB 0.6271 is not a tie. `selection.used_test_for_selection` is hard-coded `False`.

Feature history is built from all completed games then filtered with strict `< tip`, so a game cannot see its own scores or later games. TEST-006 covers future-game leakage.

### Accepted ADR consequences (binding)

| ADR | Consequences present? | Code/ops match? |
|---|---|---|
| 001 PostgreSQL 16 | Yes | Compose `postgres:16` |
| 003 val select / test once / pin / no baseline serve | Yes | `ml/pipeline.py`, `/v1/model` |
| 004 artifacts volume | Yes | Compose `artifacts`; gitignore |
| 005 batch Python orchestrator; limited resume | Yes | `athletiq.pipeline`; state file not restored |
| 006 immutable raw JSON | Yes | `raw_data` volume; new batch dirs |
| 008 `game_id` + precomputed `(game_id, feature_version)` | Yes | API lookup; 404 `features_not_found` path exists |
| 009 no auth; localhost bind | Yes | OpenAPI `security: []`; `127.0.0.1:8000` |
| 010 BIGINT | Yes | schema + OpenAPI decimal string |
| 011 NBA Stats live; fixture CI | Yes | `nba_stats.py`; CI pytest fixtures |
| 002 | Superseded by 011 | Unused `ApiSportsProvider` fallback kept (CR-002) |
| 007 GCP | Proposed / non-binding | Not demanded |

### Manual tests performed

| Check | Result |
|---|---|
| `GET /v1/health` | 200 `{"status":"ok"}` |
| `GET /v1/model` | `xgboost-v1`, `team_l5_l10_v1`, `baselines_served: false`, methodology + limitations + `model_card_ref` |
| `GET /v1/predict?game_id=48` | 200 valid binary + probability + lineage |
| `GET /v1/predict?game_id=99999` | 404 `game_not_found` |
| `GET /v1/predict` | 400 `invalid_request` |
| Docker | Only `athletiq-nfr001-attest` running; working-tree Compose down |
| Attest DB | 48 games, empty reserved player tables |
| Working-tree volumes | Live pin + 2640-game validation report + per-season raw counts |
| Secrets | `.env` ignored; example placeholders; no committed keys |
| QA | ACCEPT (TEST-001…014) |
| GHA | run 31753742525 `success` @ `4a2f713` |

## LR-convergence disposition

**Choose disclosure, not retuning.**

- Observed live `training_config`: `{"C": 1.0, "max_iter": 500, "random_state": 42, "solver": "lbfgs"}`.
- The selected model **is** this LR object; test log loss **0.6231052772493764** is what it produced; `ml005` vs domain-informed 10.99 is True under the locked rule.
- Non-convergence means coefficients may not be at the MLE. That is a **limitation of the live pin**, not a license to increase `max_iter` or add `StandardScaler` in order to improve the already-seen test number (test-strategy freeze rule).
- Required text (owning skill `architecture`, file `docs/06-design/model-card.md` Known limitations), after owner approval of this review:

  > Live NBA holdout pin `logistic_regression-v1` was fit with sklearn `LogisticRegression(solver="lbfgs", max_iter=500)` on unscaled team L5/L10 features. The solver emitted `ConvergenceWarning`. Reported test log loss 0.623 is the output of that fit, not a claim of full optimizer convergence. Config was not changed after inspecting test metrics.

- Optional alternative: freeze a **new** preprocessor/iter config, retrain, and evaluate test **once** on that new frozen config **without** using 0.623 to pick it. Then the previous 0.623 remains historical, not the served attestation.

Attest/fixture serving (`xgboost-v1`) is unaffected.

## Required fixes (ordered)

None that **block** owner manual test.

Before **PRD acceptance ticks**:

1. **`architecture`** — add the live LR non-convergence limitation to `docs/06-design/model-card.md` (wording above). Optionally mirror a short clause in the `/v1/model` limitations string (IMP-012 / API) without changing model selection.
2. **Owner / docs commit** — land the working-tree README (and related honesty recording already drafted) so `4a2f713`’s “Remote CI green deferred” is not the published status. Do not tick PRD as part of that commit unless the owner is doing closeout in the same change.
3. **`implementation-planning`** — tick IMP-001…012 **Code review passed** using the wording in the next section. Optionally align remaining IMP **CI passed** boxes with IMP-011’s already-recorded remote green. Do not invent new IMPs.

Non-required: Compose e2e pytest; player ingest; scaler/iter retune; GCP; auth; reopening CR-001.

## Recommended checkbox wording (do not apply here)

### Implementation plan — every IMP-001…012 Code review line

Replace the open box with:

```text
- [x] Code review passed — 2026-08-14 lead MVP critique APPROVE with notes (`docs/00-meta/reviews/2026-08-14-lead-mvp-critique.md`); application source `4a2f713`
```

### PRD MVP acceptance

Tick **1–11 and 13–17** only after this review is accepted. Tick **12** only after model-card note 1 is merged. Leave boxes unchecked until the owner performs that closeout.

## Gate snapshot (MVP slice)

| Gate | Status |
|---|---|
| 0 Charter | Approved v1.0.2 |
| 1 PRD | Approved v1.0.4; acceptance **unchecked** |
| 2 SRS + traceability | Approved v1.4.3 / v1.5.4 |
| 3 Architecture + binding ADRs | Approved / Accepted |
| 4 Design + contracts | Approved (`schema.sql`, `openapi.yaml`, model card) |
| 5 Implementation plan | Approved; IMP-001…012 Done; code-review boxes open until owner ticks |
| 6 Code | Present at `4a2f713`; this review |
| 7 Test strategy/plan + execution | Approved docs; local QA ACCEPT; remote CI green |
| 8–9 Release/ops | Not required to start owner manual test |

## Scope and lock validation

- [x] Only this review artifact authored
- [x] No primary product document or application-code edits
- [x] No Grill-Me invocation
- [x] PRD acceptance remains unchecked
- [x] IMP checkboxes not ticked by this review
- [x] CR-001 not reopened; no player ingest demanded
- [x] No Compose e2e pytest added or recommended
- [x] No `API_SPORTS_KEY` / signup URLs invented
- [x] Fixture CI / NFR-003 preserved
- [x] Attest `xgboost-v1` and live `logistic_regression-v1` not treated as contradictory
- [x] TEST-007 remains synthetic
- [x] LEAD-001 not re-litigated; no new overclaim of TEST-010/013 as NFR-001
- [x] Binding ADR consequences checked
- [x] LR warning not “fixed” by test-peek tuning
