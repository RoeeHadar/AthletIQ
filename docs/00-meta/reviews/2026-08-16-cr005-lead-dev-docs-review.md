# Lead engineering review — CR-005 documentation slice

Status: Complete  
Date: 2026-08-16  
Reviewer role: Lead developer (docs only; no Gate 6 code)  
Scope: CR-005 docs (CR, Charter/PRD, SRS/traceability, ADR-014–017, architecture, design, IMP-019–025, TEST-020–028)

No Grill-Me. No primary-doc edits. No application code.

## Executive verdict

**REJECT**

Owner-confirmed locks are present and mostly consistent across CR-005, Charter/PRD, SRS FR-021–028, ADR-014–017, architecture, and design: labeled e-coin simulation (not a book), `?user=` without auth, pipeline even-money settle, three surfaces, uncapped live NBA with ADR-017 extending ADR-011, fixture WNBA 2021–2025 + 2026 scheduled, synthetic Market P, NFR-003 fixture CI, IMP-019–025 Not started. Gate 6 must not start while an Approved FR-001 test still requires the pre-CR-005 mapper to **drop** null-score games. That contradicts FR-021 / TEST-025 and would make IMP-025’s “TEST-001–019 remain passing” unsatisfiable without silently violating the persist-unplayed lock.

**Score: 7 / 10** (locks are written; Gate 7 still encodes the old drop behavior)

## Findings

| ID | Severity | Status | Area | Evidence | Owning skill | Required disposition |
|---|---|---|---|---|---|---|
| CR5-001 | **Blocker** | **OPEN** | TEST-003 vs FR-001/FR-021 | Amended FR-001 AC: live ingest **shall not drop** games solely because scores are null (`docs/03-requirements/SRS.md`). FR-021 / ADR-015 / TEST-025 invert the current mapper. TEST-003 step 6 still requires `NbaStatsApiProvider` to **skip missing scores** and remains **Passing**, mapped to FR-001 (`docs/08-testing/test-plan.md`). Current code matches that old step (`to_provider_game` returns `None` when `homePts`/`visitorPts` are null; `src/athletiq/provider/nba_stats.py`). IMP-025 requires TEST-001–019 to remain passing (`docs/07-implementation/implementation-plan.md`). | `testing` | Before Gate 6: retarget TEST-003 step 6 (keep null-score rows; do not hardcode `Finished`; still skip non-NBA / unmappable teams). TEST-025 remains the injected in-progress / player-box case. Do not keep “skip missing scores” as a Passing FR-001 step. |
| CR5-002 | Major | **OPEN** | TEST-021 settle math | FR-023 even-money: correct → stake returned + equal house credit; wrong → stake gone. TEST-021 describes both, but steps only cover cancel, win (`balance = prior + stake`), idempotent re-run, and window-closed. No lose-path step. `prior` is undefined if `wallets.balance` is unlocked-after-lock (990+10=1000) vs pre-lock (1000+10=1010). | `testing` | Add a lose-path step. State that win balance is **pre-lock balance + stake** (or unlocked + 2×stake). |
| CR5-003 | Major | **OPEN** | Replace API | FR-023 cancel **or replace** before tip. `POST /v1/stakes` is “Place or replace” with body `user, game_id, side, amount` only, yet 409 `duplicate_open_stake` fires when replace was **not** requested (`docs/06-design/api-design.md`). No `replace` flag / query. TEST-022 asserts 409 without replace; TEST-021 never exercises replace. | `architecture` (api-design) + `testing` | Specify the replace discriminator (body/query) before or on IMP-023 OpenAPI. Add one pre-tip replace step. |
| CR5-004 | Minor | **OPEN** | TEST-002 vs DR-005 | IMP-019 lists TEST-002; TEST-022 covers seed balances. TEST-002 steps still list CR-001 reserved players and do not assert `users` / `wallets` / `ledger_entries` / `stakes` (`docs/08-testing/test-plan.md`). | `testing` | Extend TEST-002 required tables (or keep ledger asserts only on TEST-022 and drop the IMP-019→TEST-002 implication that schema suite covers DR-005). |
| CR5-005 | Minor | **OPEN** | Traceability Notes vs matrix | Matrix DR-001 Implementation = **Partial** (correct for uncapped + WNBA window). Notes still say DR-001 Implementation **Implemented** on the 2023–2024 2640-game live run (`docs/03-requirements/traceability.md`). | `requirements` | Align Notes with the Partial column; do not treat the old 2-season live run as CR-005 DR-001 done. |
| CR5-006 | Minor | **OPEN** | Registry / ML prose | ID registry DR-001 title remains “MVP season depth (2 Must / 3 Should)”. `ml-design.md` still says “Third NBA season extends early train.” SRS/ADR-017 are uncapped. | `requirements` / `architecture` | Update registry summary (append-only title can note superseded window). Drop “third season” as if live NBA were still depth 3. |
| CR5-007 | Minor | **OPEN** | TEST-004 leftover | TEST-004 step 3 still says `player_game_stats` is **reserved** (CR-001) and not a load grain. CR-004 already loads players; CR-005 adds live NBA boxes. | `testing` | Point player grain at TEST-016/025; do not re-reserve players. |
| CR5-008 | Minor | **OPEN** | `/slate` copy vs settle | api-design HTML table: `GET /slate` role includes “stake/settle”. ADR-015 / error-handling: `/slate` **displays only** and does not settle. | `architecture` | Say stake/cancel/replace + display of settlement; pipeline settle stays off the page. |
| CR5-009 | Minor | **OPEN** | Infra status | Board-poll Must (etl image, 30s, three services, no Kafka) is written in Approved system-architecture and in `docs/09-devops/infrastructure.md`, but infrastructure remains **Draft**. | `devops-operations` | Not a Gate 6 content hole; optional Approve of that file so the poll command is not only in a Draft doc. |

### OPEN findings blocking Gate 6

- **CR5-001** — TEST-003 still requires skip-missing-scores; FR-021 requires keeping those rows.

## Gate snapshot

Gate status is artifact approval, not code. CR-005 application code is absent (no `003` migration, no `/slate`/`/board`, `nba_stats.py` still drops null scores and returns `[]` for players).

| Gate | Phase | Snapshot |
|---|---|---|
| 0 | Project initiation | **Approved** — Charter 1.0.3 (e-coin simulation in effort boundary; real-money book out) |
| 1 | Product definition | **Approved** — PRD 1.2.0 (simulation semantics; three journeys) |
| 2 | Requirements | **Approved** — SRS 1.6.1, traceability 1.7.0; **CR5-001** is Gate 7 vs Gate 2 disagreement |
| 3 | Architecture | **Approved** — system/data/api 1.2.0; ADR-014–017 Accepted; ADR-011 Accepted (not superseded); ADR-009/012 held |
| 4 | Detailed design | **Approved** — DB/API/ML/error/model-card (CR-005). House `1000000000` is the design constant. |
| 5 | Implementation planning | **Approved** — plan 1.2.0; IMP-019–025 **Not started** |
| 6 | Implementation | **Not started** — do not start until this review is APPROVE |
| 7 | Verification docs | Strategy 1.2.0 + plan 1.2.0 **Approved**; TEST-020–028 **Planned**; TEST-003 still encodes pre-CR-005 drop (**CR5-001**) |
| 8 | Release | **Draft** / out of this CR |
| 9 | Operations | infrastructure.md **Draft** (CR5-009); no Kafka/Redis/K8s/GCP in the CR-005 topology |

## ID / mapping checks

| ID | Registered | Cross-linked | Implementation column | Result |
|---|---|---|---|---|
| CR-005 | Yes | CR file Accepted | — | Pass |
| FR-021–028 | Yes | SRS + traceability + IMP + TEST | **Not started** | Pass |
| DR-005/006 | Yes | SRS + IMP-019 | **Not started** | Pass |
| ML-012 | Yes | SRS + IMP-024 + TEST-027 | **Not started** | Pass |
| ADR-014–017 | Yes | Accepted; consequences present | **Not started** | Pass |
| IMP-019–025 | Yes | Plan Status **Not started**; DoD unticked | — | Pass |
| TEST-020–028 | Yes | Plan **Planned** | — | Pass |
| Amended FR-001/002/015/016/017 | Yes | Implementation **Partial** | Pass (allowed) |
| CON-009 | Yes | Amended Partial / Planned | Pass |
| FUTURE-006/007 | Not pulled | SRS Future table | Pass |
| FUTURE-008 | Pulled as FR-025/026 | SRS | Pass |

No Implementation=`Implemented` on FR-021–028, DR-005/006, ML-012, or ADR-014–017. NFR-003 stays **Implemented** for existing fixture CI, with Verification **Passing (local) / Planned** for TEST-025 — not a claim that CR-005 board poll already runs in GHA.

No orphan FR/IMP/TEST among the CR-005 mint set. Canonical map is traceability; IMP coverage table defers to it.

## Lock checks

| Lock | Result | Evidence |
|---|---|---|
| Labeled simulation; fake e-coins; not a real-money book; sportsbook language off gamecast; `/slate` may use stake/settle | **Held** in PRD/SRS CON-009/ADR-014/PRODUCT.md | TEST-019 still forbids stake chrome on `GET /`; TEST-028 allows stake/settle on `/slate` only |
| Basketball only; extra sports wait; Compose + Postgres; no Kafka/Redis/K8s/GCP | **Held** | Charter/PRD non-goals; system-architecture §9; infrastructure three services |
| `?user=demo-1\|demo-2`; Postgres users/wallet/stake; no passwords; ADR-009 stays | **Held** | ADR-014; ADR-009 v1.1.0: query param is **not** auth |
| Persist scheduled/unplayed; P from prior completed history; CI scheduled rows; live keeps null scores | **Contradicted in TEST-003** | SRS/ADR-015/TEST-020/025 vs TEST-003 step 6 (**CR5-001**) |
| Even-money; lock until Finished; house = system wallet; one open stake per (user, game); settle **in pipeline**; `/slate` displays only | **Held** (settle math underspecified in TEST-021 — CR5-002) | ADR-015; error-handling; no settle endpoint on `/slate` |
| New stake only if scores null **and** `game_start_time` future UTC; cancel/replace before tip | **Held** as requirements; replace HTTP underspecified (CR5-003) | FR-023; `stake_window_closed` |
| Keep gamecast `GET /`; add `/slate` and `/board`; producer-bar three-way links; same instrument family | **Held** | ADR-016; FR-015/024/025; PRODUCT.md |
| Demo users start at **1000**; no refill; reject below-zero; house **1000000000** OK | **Held** | FR-022; database-design; IMP-019 notes |
| `/slate` = next **20** unplayed pre-tip (NBA+WNBA mixed) **plus** that user’s open stakes | **Held** | FR-024; TEST-023 `≤20 upcoming plus open stakes` |
| Uncapped live NBA; no age-prune; CI fixtures small; retrain NBA **and** WNBA; CI 48-game pin unchanged; 0.623 does not bind; same protocol/hyperparameters/`feature_version`; test once | **Held** | DR-001; ML-012; FR-028; model-card items 7/9; TEST-027 |
| WNBA fixture 2021–2025 + 2026 scheduled; no live WNBA HTTP | **Held** | FR-016; ADR-017; TEST-026 |
| Live board = `GET /board` in-progress only; gamecast no score/clock; no invented clock | **Held** | FR-025; TEST-024 |
| Adapter-only newest-page poll in **etl** image; not a fourth service; browser polls AthletIQ; no WebSockets; default **30s** | **Held** | ADR-015; infrastructure; system-architecture etl row |
| Live NBA player boxes on same no-key host; CI/WNBA player rows fixture | **Held** as **target**; code still `return []` | FR-027; ADR-017; IMP-020 Not started |
| Keep synthetic Market P (ADR-012); live odds wait | **Held** | ADR-012 v1.1.0; FUTURE-006 not pulled |
| Integer stakes min 1, max unlocked balance | **Held** | FR-023; api-design |
| NFR-003: CI fixture-only / injected HTTP; no live provider in GHA | **Held** | SRS NFR-003; TEST-025 “No live HTTP”; IMP-025 |
| ADR-017 **extends** ADR-011; does **not** supersede | **Held** | ADR-017 decision 6; decisions README; ADR-011 still Accepted |

## Required independent checks

| Check | Result | Evidence |
|---|---|---|
| CR-005 registered and Accepted | **Pass** | `id-registry.md`; CR file Decision status Accepted |
| FR-021–028 / DR-005/006 / ML-012 / IMP-019–025 / TEST-020–028 registered | **Pass** | `id-registry.md` |
| No Implementation=`Implemented` for unbuilt CR-005 | **Pass** (matrix); Notes nit CR5-005 | traceability FR-021–028, ADR-014–017 = Not started |
| CON-009 allows labeled e-coin sim; forbids real-money book | **Pass** | SRS CON-009 amended |
| ADR-011 not superseded by ADR-017 | **Pass** | ADR-017; README |
| Gamecast vs `/slate` vs `/board` separated | **Pass** | ADR-016; PRODUCT.md |
| Settle in pipeline, not on `/slate` | **Pass** | ADR-015; error-handling |
| NFR-003 no live HTTP in CI | **Pass** | test strategy principles; TEST-025 |
| CI 48-game pin unchanged; 0.623 non-binding | **Pass** | ML-012; TEST-027; model-card |
| Code baseline not claimed Implemented | **Pass** for CR-005 FRs | No `003` migration; Compose has no board poll; `nba_stats.py` drops null scores and empty player fetches — described as IMP-020 target |
| TEST-019 vs TEST-020–028 | **Pass** | TEST-019 = gamecast no stake chrome (Passing); CR-005 cases Planned; stake copy on `/slate` only |
| Orphan FR/IMP/TEST in the CR-005 mint set | **Pass** | traceability + plan maps |
| TEST-003 vs keep-null-score lock | **Fail** | CR5-001 |

## Accepted ADR consequences (014–017 + 009/012)

| ADR | Consequences present? | Follow-through in docs | Verdict |
|---|---|---|---|
| ADR-009 | Yes — `?user=` is not auth | api-design none; PRD pick-a-demo-user | **Held** |
| ADR-012 | Yes — e-coin ≠ live odds | FR-018 unchanged; FUTURE-006 not pulled | **Held** |
| ADR-014 | Yes — schema + JSON; CON-009 amended; house is a design constant | database-design `1000000000`; no password columns | **Held**; replace flag is design (CR5-003) |
| ADR-015 | Yes — status/scores; settle stage; poll interval design default; WNBA board fixture | infrastructure 30s etl; TEST-025 step 4 newest-page | **Held** in architecture; **broken** in TEST-003 (CR5-001) |
| ADR-016 | Yes — two extra static pages; TEST-019 vs 024/028 | PRODUCT.md three surfaces | **Held** |
| ADR-017 | Yes — slow paging; newest-page poll; 0.623 non-binding; depth-3 clamp removed on live path | ml-design / DR-001; does not supersede ADR-011 | **Held** |

## Code drift baseline (target vs HEAD)

| Concern | Docs target | Code / contract today | Verdict |
|---|---|---|---|
| Null-score live games | Keep; status not hardcoded Finished | `to_provider_game` returns `None`; status always `"Finished"` | Expected until IMP-020; TEST-003 must not freeze the old behavior |
| Live player boxes | Same host; persist rows | `fetch_players` / `fetch_player_game_stats` return `[]` | Expected until IMP-020 |
| Season cap | No live clamp / no age-prune | `season_depth: int = 3` + stop when all mapped rows are before window | Expected until IMP-020 |
| Ledger / `/slate` / `/board` | Migration 003 + routes | No `users` tables; Compose has three services and no poll command | Expected until IMP-019/022/023 |

Do not treat the current mapper as the CR-005 contract.

## What is sound

- Grill-Me Q1–Q27 locks are written as product/SRS/ADR text without inventing extra sports, live WNBA HTTP, live odds, Kafka, or application auth.
- CON-009 amendment is precise: simulation allowed; sportsbook words forbidden; gamecast has no stake chrome; `/slate` may say stake/settle.
- Three-surface IA (ADR-016) and settle-vs-display (ADR-015) are consistent with PRODUCT.md.
- Retrain protocol (ML-012) keeps `feature_version = team_l5_l10_player_agg_v1`, CI 48-game pin, and unbound 0.623.
- Traceability Implementation columns for the new IDs are honest (**Not started** / **Planned**).

## What not to do

- Do not start IMP-019–025 until TEST-003 is retargeted and this review is re-run to APPROVE.
- Do not “keep TEST-003 passing” by continuing to drop null-score live rows.
- Do not supersede ADR-011, add a fourth Compose service, call `nbaapi.com` from the browser, settle on `GET /slate`, or bind 0.623 / retune the 48-game CI pin.
- Do not mark FR-021–028 Implemented until the IMPs are Done.

## Disposition

**REJECT.** Gate 6 may **not** start.

Must-fix (owning skill `testing`; do not implement code in this review):

1. **CR5-001** — Amend TEST-003 so FR-001 no longer requires skip-missing-scores. Align with FR-021 / TEST-025. Keep NFR-003 (injected HTTP only).

Should-fix before or with the first IMP that touches the API/tests (not required to reverse REJECT by themselves):

2. CR5-002 — TEST-021 lose path + explicit win formula  
3. CR5-003 — replace discriminator on `POST /v1/stakes`  
4. CR5-004–CR5-008 — TEST-002 ledger tables, DR-001 Notes, registry/ML “third season”, TEST-004 reserved-players leftover, `/slate` display-only wording  

## Validation

- [x] Only this review artifact was authored  
- [x] No Grill-Me  
- [x] No Charter/PRD/SRS/ADR/design/IMP/test-plan/code edits  
- [x] Accepted ADR-014–017 consequences checked; ADR-009/012/011 checked  
- [x] CR-005 Implementation columns are not Implemented  
- [x] Code spot-check used only as drift baseline  
