# Gate 6 code review — CR-005 (IMP-019–025)

Status: Complete  
Date: 2026-08-16  
Reviewer role: Gate 6 code reviewer (lead-engineer bar)  
Scope: AthletIQ CR-005 implementation vs Accepted CR, IMP-019–025, TEST-020–028  
No Grill-Me. No primary-doc edits. No implementation fixes.

## Verdict

**APPROVE**

The working tree matches Accepted CR-005. Must requirements for IMP-019–025 are implemented. TEST-020–028 exist and cover the plan’s material steps (scheduled persist, even-money settle, `replace=false` 409, slate/board surfaces, injected nba-stats mapping, WNBA 2021–2026 fixtures, val-only select, three-way producer links). Remaining items are nits or defensive gaps that do not fire on the fixture/demo path.

Code-review DoD for IMP-019–025 is this verdict. This file does not tick plan checkboxes.

## SHA / working-tree note

| Ref | SHA | Note |
|---|---|---|
| Base (CR-004 DoD close) | `e5b2f7fc03460dfcb83013c19a172f1dd1fd3e3c` | Exclusive start: `e5b2f7f` (`main`) |
| Implementation | **working tree** (uncommitted) | No CR-005 commit at review time |
| HEAD (git) | `e5b2f7fc03460dfcb83013c19a172f1dd1fd3e3c` | Same as base; **not** the reviewed snapshot |
| Remote CI | not attested on this tree | Last recorded green: CR-004 `491c5c0` ([run 31913410157](https://github.com/RoeeHadar/AthletIQ/actions/runs/31913410157)) |

Range reviewed: **working tree vs Accepted CR-005 + IMP-019–025**, including untracked sources (`003` migration, `src/athletiq/ledger/`, `src/athletiq/board_poll/`, `api/app/ledger_routes.py`, `api/static/{slate,board}.*`, `tests/unit/test_cr005.py`, WNBA 2021/2022/2025/2026 + NBA 2026 fixtures). Git `HEAD` alone is insufficient.

Local pytest note (implementer): unit+integration **86 passed**, 1 skipped, **4 errors** in `tests/integration/test_postgres_stores.py` (`psycopg` `ConnectionTimeout`). Those tests run only when `TEST_DATABASE_URL` is set and do not skip on connect failure (`test_schema.py` does). Not a CR-005 product defect.

## Gates (this slice)

| Gate | Artifacts | Status |
|---|---|---|
| 0–5 | Charter/PRD/SRS/architecture/ADRs 014–017/design/IMP plan | Approved (docs rereview APPROVE 2026-08-16) |
| 7 docs | Test strategy/plan TEST-020–028 | Approved before code (§22) |
| 6 | IMP-019–025 in the working tree | **APPROVE** (this review) |

Traceability still lists FR-021–028, DR-005/006, ML-012, ADR-014–017 as Implementation **Not started**, and IMP-019–025 Status remains **Not started**. Correct until IMP DoD is ticked after this review — the implementer did **not** prematurely mark `Implemented`.

## Per-IMP

| IMP | Evidence | Result |
|---|---|---|
| **019** schema | `database/schema.sql` + `003_cr005_ledger_game_lifecycle.sql`: `users` / `wallets` / `stakes` / `ledger_entries`; partial unique open `(user_id, game_id)`; `games.status` CHECK `scheduled` \| `in_progress` \| `Finished` \| `unknown`; nullable scores. 003 seeds `demo-1`/`demo-2` at **1000** and house **1000000000**. No password columns. Compose initdb mounts 001+002+**003**. `migrations_dir()` still probes cwd `/app/database/migrations`, env, then checkout. | Pass |
| **020** provider | `to_provider_game` keeps null scores; status not hardcoded Finished for those rows. `map_game_status` uses provider text (final / Qx / live). When `seasons is None`, paging has no age stop (`_wanted` unset; `_season_depth` unused). `include=playerGameBasicStats`; `to_player_game_stats` maps boxes (no hard `return []` on `fetch_player_game_stats`). `leagues()` is NBA-only. Tests inject `get_json`. | Pass |
| **021** fixtures | Authored WNBA 2021–2025 completed + 2026 scheduled (null scores); NBA `games_2026.json` scheduled. Counts stay small (not a live dump): NBA 24+24+24+2; WNBA 4+4+12+12+4+2. Fixture provider discovers `games_wnba_*.json`. | Pass |
| **022** settle + poll | `settle_finished_on_store` runs at end of `stage_load` (even-money; idempotent; house pays wins; losses leave house unchanged). `STAGE_ORDER` remains `ingest, load, features, train` — **no** new settle stage. `/slate` does not settle. `python -m athletiq.board_poll` in etl image; `DEFAULT_INTERVAL = 30`; Compose still **three** services; poll documented as `compose exec`, not a fourth service. | Pass |
| **023** API/UI | HTML `GET /slate` + `GET /board`; gamecast stays `GET /` with no score/clock/stake chrome. Producer-bar three-way links. `?user=demo-1\|demo-2` (JS clamps; API `house` → `user_not_found`). `replace` boolean default false; 409 `duplicate_open_stake` when false. OpenAPI matches. `Cache-Control: no-store` on `/`, `/slate`, `/board`, `/static`. Compose publishes `127.0.0.1:8000` only. PRODUCT.md / DESIGN.md updated as listed IMP files (facts not reopened here). | Pass |
| **024** retrain/disclose | Same `FEATURE_VERSION = team_l5_l10_player_agg_v1`. `run_train_select_publish` still selects on `val_scores`; `selection_used_test = False`; one test pass when `evaluate_test=True`. No `0.623` bind in train code. `/v1/model` + model-card disclose CI 48-game pin unchurned and 0.623 non-binding. No committed pin file was replaced (none in git). | Pass |
| **025** tests + CI | `tests/unit/test_cr005.py` implements TEST-020–028. TEST-003 step 6 retargeted (keep null scores). No `# Implements` on test files. GHA still fixture-only; no `API_SPORTS_KEY`; unit job does not set live provider env. | Pass |

`# Implements` present on listed Python/SQL/OpenAPI/Compose modules. `api/static/` HTML/JS has no Implements comment; not a Must miss (same as IMP-018).

## TEST-020–028 mapping

| ID | Plan steps | Where | Coverage |
|---|---|---|---|
| TEST-020 | Scheduled rows persist; scores null; status ≠ Finished; features from prior completed; labels exclude non-Finished | `test_cr005.py` `test_scheduled_persist_and_features_from_prior_only`; `stage_features` skips non-Finished for history/`y` | **Present.** History filter in pipeline is code-reviewed; the unit test builds history from Finished rows only (does not invoke `stage_train`). |
| TEST-021 | Cancel restore 1000; replace 10→20 → 980; win 1020; lose 990 house unchanged; idempotent; window closed; `/slate` display-only | `test_even_money_settle_cancel_replace` | **Present.** After-tip **new** stake asserted; after-tip cancel/replace not separately posted (ledger uses the same window guard). |
| TEST-022 | Seed 1000; house exists; amount 0 / over unlocked; 409 `replace=false`; `house` + unknown → `user_not_found` | `test_integer_bounds_and_one_open_stake`; live migrate seed in `test_schema.py` | **Present.** Live TEST-002 house assert is `>= 1000` (003 inserts `1000000000`; unit asserts `HOUSE_START`). |
| TEST-023 | HTML `/slate`; JSON ≤20 upcoming + open stakes; `?user=` switch; Finished absent | `test_slate_next_twenty_and_user_query` | **Present.** |
| TEST-024 | `/board` in-progress + scores; gamecast no clock/quarter; scheduled-only → empty board | `test_board_in_progress_gamecast_has_no_clock` | **Present.** Clock assertion is InMemoryGameRepo JSON; Postgres/`GameRecord` have no `clock` column (see findings). |
| TEST-025 | Injected HTTP: null scores kept; in-progress + boxes; newest-page helper (not full history) | `test_nba_stats_injected_null_in_progress_boxes_and_newest_pages`; TEST-003 mapper keep-null | **Present.** `fetch_newest_pages(pages=1)` one call despite `pagination.pages=50`. `include=playerGameBasicStats` asserted. |
| TEST-026 | WNBA 2021–2025 Finished; 2026 scheduled null; NBA 2026 scheduled; no network | `test_wnba_fixture_window_2021_to_2026` | **Present.** Fixture files only. |
| TEST-027 | Val select; test once; `feature_version` unchanged; 0.623 not an assert; CI pin identity | `test_retrain_protocol_ci_pin_unchanged` | **Present.** Source-inspect of `run_train_select_publish` (no on-disk 48-game pin in git to fingerprint). |
| TEST-028 | Three-way links; no odds/juice/moneyline/payout/wager; `/slate` may stake; `GET /` must not | `test_producer_bar_three_way_links_and_copy`; TEST-019 still forbids stake on gamecast | **Present.** Board HTML is not separately asserted stake-free (it has none). |

## Findings

### Medium

1. **Live `/board` cannot surface provider clock.** `to_provider_game` maps `clock` / `gameStatusText`, but `parse_game` / `GameRecord` / `schema.sql` / `PostgresGameRepo.list_in_progress` drop it. Board poll upserts scores only. TEST-024’s clock check holds only for `InMemoryGameRepo`. FR-025 AC requires scores and **no invented** clock; Description says show clock if sent. Does not invent a clock; live demo is scores-only. Follow-up: persist optional clock or document scores-only on the Postgres path.

2. **`map_game_status` falls back to `Finished` when both scores exist and status text is empty/unrecognized.** Null-score rows stay `scheduled` (TEST-003/025). In-progress with `gameStatusText` like `Q2 3:12` maps `in_progress`. An in-progress payload with scores and **no** status text would set `home_win` and could enter train history. Does not fire on authored fixtures or the injected TEST-025 live row. Follow-up: treat unknown+scores as `in_progress` or `unknown`, never Finished, unless provider text says final.

### Low (nits)

3. **TEST-027** does not fingerprint a committed 48-game `selected_pin.json` (none in git). Protocol + `FEATURE_VERSION` + “no 0.623 in train source” are asserted. Canonical `--provider fixture` with **no** `--seasons` now lands every authored fixture year via `available_seasons()` (extra WNBA 2021–2025/2026 and NBA 2026 scheduled). GHA does not publish a new pin. NBA 2022–2024 labeled files remain the toy set.

4. **`schema.sql` has ledger DDL but not seed DML.** 003 inserts demo users / house; live TEST-002 migrate path asserts balances. Same contract-vs-migrate pattern as `schema_migrations` INSERT.

5. **Slate UI always posts `replace: false`.** Replace exists on `POST /v1/stakes` (TEST-021). Demo undo is cancel-then-lock.

6. **TEST-021** does not POST after-tip cancel/replace (only new stake → `stake_window_closed`). Memory/Postgres ledger share the same window predicate.

7. **`NbaStatsApiProvider._season_depth` is stored and unused.** Uncapped live path is `seasons is None`. CLI help still says “else season_depth window.”

8. **`test_postgres_stores.py`** errors instead of skip when `TEST_DATABASE_URL` is set but Postgres is down. `test_schema.py` skips on connect failure. Not a product defect.

9. **`api/static/`** (IMP-023 HTML/JS) has no `# Implements` banner; Python/SQL/OpenAPI/Compose modules listed on IMP-019–024 do.

No High findings. No secrets in source. CI does not set `API_SPORTS_KEY` or call live providers. Demo Cache-Control `no-store` is accepted. Three Compose services still (database, etl, api).

## Drift (§13a) — this slice

| Layer | DB | API | ML |
|---|---|---|---|
| Design | users/wallets/stakes; status + nullable scores; house `1000000000` | three surfaces; `replace` default false; `/slate` display-only | same `feature_version`; val select; test once; 0.623 does not bind |
| Contract | `schema.sql` + 003 match end-state DDL; seeds in 003 | `openapi.yaml` slate/board/wallet/stake/cancel + error codes | FEATURE_VERSION + v2 pin schema unchanged |
| Implementation | migrate 003 + ledger adapters | `ledger_routes.py` / static slate+board / gamecast links | `stage_load` settle; `stage_features` Finished-only history; methodology disclose |

No design-vs-contract-vs-code contradiction that would ship a real-money book, skip scheduled rows, leak in-progress boxes into labels on the tested path, add sportsbook chrome on gamecast, or replace the CI pin identity in git.

Clock on live `/board` is the only material design-vs-contract gap (finding 1).

## Must-lock hold table (CR-005)

| Lock | Result | Evidence |
|---|---|---|
| Labeled e-coin simulation; not a real-money book; sportsbook words off gamecast; `/slate` may use stake/settle | **Held** | Gamecast HTML/JS: no stake/payout/wager/moneyline (TEST-019). Slate: “stake / settle · not a book”. Board: no book copy (TEST-028). |
| ADR-009 stays; `?user=` is not auth; demo-1/demo-2 only; `?user=house` rejected | **Held** | No auth middleware. `MemoryLedger`/`PostgresLedger.require_user`: `house` → `user_not_found`. TEST-022. |
| Persist scheduled/unplayed (null scores, not hardcoded Finished); P(home_win) from prior completed history only; in-progress scores must not enter train/`home_win` until Finished | **Held** | Mapper keeps null scores; `parse_game` sets `home_win` only if `status == "Finished"`; `stage_features` history requires Finished. TEST-020/025. Finding 2 is an untested empty-status edge. |
| Even-money; `replace` boolean default false; 409 `duplicate_open_stake` when `replace=false`; settle in pipeline after load (not a new `STAGE_ORDER` entry); `/slate` display only | **Held** | OpenAPI + `ledger_routes` default false; TEST-021/022. `STAGE_ORDER` unchanged; settle at end of `stage_load`. Slate GET does not call settle. |
| GET `/` gamecast: no score/clock, no stake chrome (TEST-019). GET `/slate` + GET `/board`. Producer-bar three-way links. Demo UI only `127.0.0.1:8000`. Cache-Control `no-store` | **Held** | `main.py` FileResponse + static `no-store`. Compose `127.0.0.1:8000:8000`. TEST-019/024/028. |
| Uncapped live NBA paging when `seasons is None`; CI fixtures small; no live WNBA HTTP | **Held** | `_wanted is None` pages until pagination ends. Fixture counts above. `fetch_games(..., league!="nba")` → `[]`. |
| Live NBA player boxes on nba-stats host; CI/WNBA boxes fixture | **Held** | `include=playerGameBasicStats`; `to_player_game_stats`. Odds still `fetch_odds_snapshots` → `[]` (ADR-012). |
| Board poll `python -m athletiq.board_poll` in etl image, default 30s, not a fourth Compose service | **Held** | `board_poll/__main__.py`; `DEFAULT_INTERVAL = 30`; Compose comment; three services in `docker-compose.yml` + TEST-010. |
| CI pin identity not replaced; 0.623 does not bind; same `feature_version` `team_l5_l10_player_agg_v1` | **Held** | Builder constant; methodology + TEST-027; no pin artifact in git to churn. |
| NFR-003: no live HTTP in tests (inject `get_json`) | **Held** | TEST-003/025 inject; CI unit env has no provider key. |
| Three Compose services (database, etl, api) | **Held** | `docker-compose.yml`; TEST-010. |
| Migration 003 users/wallets/stakes/ledger; house 1000000000; demo users 1000 | **Held** | 003 SQL; TEST-022; live TEST-002 seed asserts. |

## Locks honored (not demanded)

- No betting book (CON-009 / ADR-012 / ADR-014).
- CI fixture-only (NFR-003).
- No live WNBA HTTP; nba-stats stays NBA games/teams.
- No Kafka/Redis/K8s/GCP / WebSockets.
- ADR-009: no application auth.
- No retune of live LR vs test log loss 0.623.
- Fixture `xgboost-v1` not mixed with live `logistic_regression-v1`.
- Browser never calls `nbaapi.com` (board JS polls `/v1/board`).

## Out of scope / what this review did not re-open

- Product facts locked in Grill-Me Q1–Q27 / Accepted CR-005 (docs reviews CR5-001–009).
- CR-004 pin-fallback follow-up (already fixed after that review).
- Live WNBA HTTP; named live odds adapter; betting product.
- Comp B/C, film-room, pooled NBA+WNBA classifier.
- NFR-001 clean-clone attest outside this tree; ticking IMP/TEST plan checkboxes.
- Retuning fixture XGBoost leaf extremes or live LR `max_iter`.
- Application auth, GCP, Kafka, Redis, Kubernetes.
- Auto-starting board poll on `compose up` (batch etl remains `sleep infinity`; poll is `exec`).
- Marking traceability Implementation=`Implemented` (still correctly Not started).

## Post-review attest (implementer, 2026-08-16)

Implementation committed as `657e5a1`. Remote CI [31956566628](https://github.com/RoeeHadar/AthletIQ/actions/runs/31956566628) succeeded (lint, unit, integration, image). IMP/TEST/traceability closeout is a follow-up docs commit — this review file is not rewritten.

## Owning skills if follow-up

- Live board clock (finding 1): **architecture** (api/database design) then implementation.
- Status fallback Finished (finding 2): provider mapper in `nba_stats.py` (IMP-020 owner).
- Fixture default `--seasons` window vs 48-game toy (finding 3): **implementation-planning** / ingest CLI help only if the attest recipe must stay 48-game-only.
