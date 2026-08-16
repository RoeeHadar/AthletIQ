# Lead engineering re-review — CR-005 documentation slice

Status: Complete  
Date: 2026-08-16  
Reviewer role: Lead developer (docs only; no Gate 6 code)  
Scope: Re-review after REJECT `docs/00-meta/reviews/2026-08-16-cr005-lead-dev-docs-review.md` (CR5-001 blocker + CR5-002–009). Focused re-read of TEST-002/003/004/021/022/025, IMP-023/025, api-design `/slate` + `replace`, ml-design split prose, id-registry DR-001, traceability DR-001 Notes, ADR-006 vs ADR-017, infrastructure Status; spot-check SRS FR-021, ADR-015.

No Grill-Me. No primary-doc edits. No application code.

## Executive verdict

**APPROVE**

CR5-001 is closed. TEST-003 step 6 now requires keeping null-score NBA rows and forbids a hardcoded `Finished` status; the nba-stats mapper is **Planned** (IMP-020), not unqualified Passing. IMP-025 explicitly must **not** preserve skip-missing-scores. CR5-002–009 are closed in the scoped docs. Owner-confirmed Must locks remain held. Gate 6 (IMP-019–025) may start after this artifact.

**Score: 9 / 10** (prior 7/10; residual nits are non-blocking)

## Disposition of CR5-001…009

| ID | Prior | Now | Evidence |
|---|---|---|---|
| CR5-001 | **OPEN** (blocker) | **CLOSED** | TEST-003 step 6: keep null-score rows; status not hardcoded `Finished`; still skip non-NBA / unmappable teams; in-progress/boxes stay TEST-025. Status: Passing (fixture ingest/raw); mapper **Planned**. IMP-025: do not preserve skip-missing-scores. |
| CR5-002 | OPEN | **CLOSED** | TEST-021 step 3: win = **pre-lock 1000 + 20 = 1020** (unlocked 980 + 2×20). Step 4: lose path (`demo-2` 1000→990; stake gone). |
| CR5-003 | OPEN | **CLOSED** | api-design: optional `replace` boolean **default false**; 409 `duplicate_open_stake` only when `replace` is false. TEST-021 step 2 exercises `replace=true`. TEST-022 step 3: 409 only with `replace=false`. |
| CR5-004 | OPEN | **CLOSED** | TEST-002 step 2: after **003**, assert `users`, `wallets`, `ledger_entries`, `stakes`. Status qualified (001/002 Passing; 003 **Planned**). |
| CR5-005 | OPEN | **CLOSED** | Traceability Notes: DR-001 Implementation **Partial**; 2640-game run is CR-004-era, not CR-005 done. |
| CR5-006 | OPEN | **CLOSED** | Registry DR-001 title: live NBA uncapped; original mint noted. ml-design: do not treat a third season as a cap. |
| CR5-007 | OPEN | **CLOSED** | TEST-004 step 3: player grain via TEST-016/025; **Not reserved**. |
| CR5-008 | OPEN | **CLOSED** | api-design: `/slate` stake/cancel/replace + display of settlement **results**; does **not** settle (pipeline does). |
| CR5-009 | OPEN | **CLOSED** | `infrastructure.md` **Status: Approved**. Cloud Open Questions may remain. |

## Findings

| ID | Severity | Status | Area | Evidence | Owning skill | Required disposition |
|---|---|---|---|---|---|---|
| CR5-001 | Blocker | **CLOSED** | TEST-003 vs FR-001/FR-021 | Step 6 retargeted; Status not unqualified Passing for the mapper; IMP-025 retargeted. | `testing` | None — Gate 6 may implement IMP-020 against the new step. |
| CR5-002 | Major | **CLOSED** | TEST-021 settle math | Win formula + lose path present. | `testing` | None. |
| CR5-003 | Major | **CLOSED** | Replace API | `replace` default false; 409 gated. | `architecture` / `testing` | OpenAPI at IMP-023. |
| CR5-004 | Minor | **CLOSED** | TEST-002 vs DR-005 | Ledger tables listed after 003. | `testing` | None. |
| CR5-005 | Minor | **CLOSED** | DR-001 Notes | Notes match Partial column. | `requirements` | None. |
| CR5-006 | Minor | **CLOSED** | Registry / ML prose | Uncapped wording. | `requirements` / `architecture` | None. |
| CR5-007 | Minor | **CLOSED** | TEST-004 leftover | Players not re-reserved. | `testing` | None. |
| CR5-008 | Minor | **CLOSED** | `/slate` vs settle | Display-only vs pipeline settle. | `architecture` | None. |
| CR5-009 | Minor | **CLOSED** | Infra status | Local topology Approved. | `devops-operations` | None. |

### OPEN findings blocking Gate 6

None.

### Residual nits (non-blocking)

- TEST-021 step 4: house **unchanged** on a loss. FR-023 only requires “stake gone.” IMP-022 should pick one conservation story (forfeit to house vs burn) and keep the test aligned — not a Must-lock miss.
- TEST-003 now lists FR-021; canonical traceability still maps FR-021 → TEST-020/025 (TEST-003 remains FR-001). Additive, not contradictory.
- Code still drops null scores and hardcodes `Finished` (`src/athletiq/provider/nba_stats.py`) — **expected** until IMP-020. Docs no longer freeze that behavior.

## Gate snapshot

Gate status is artifact approval, not code. CR-005 application code is still absent (no `003` migration, no `/slate`/`/board`, mapper still drops null scores).

| Gate | Phase | Snapshot |
|---|---|---|
| 0 | Project initiation | **Approved** — Charter 1.0.3 |
| 1 | Product definition | **Approved** — PRD 1.2.0 |
| 2 | Requirements | **Approved** — SRS 1.6.1, traceability 1.7.0; CR5-001 disagreement **resolved** |
| 3 | Architecture | **Approved** — system/data/api 1.2.0; ADR-014–017 Accepted; ADR-011 Accepted (not superseded); ADR-006 prune notes ADR-017; ADR-009/012 held |
| 4 | Detailed design | **Approved** — DB/API/ML/error/model-card; `replace` default false; `/slate` display-only |
| 5 | Implementation planning | **Approved** — plan 1.2.0; IMP-019–025 **Not started**; IMP-025 does not preserve skip-missing-scores |
| 6 | Implementation | **Not started** — **unblocked** by this APPROVE |
| 7 | Verification docs | Strategy 1.2.0 + plan 1.2.0 **Approved**; TEST-020–028 **Planned**; TEST-003 mapper **Planned** |
| 8 | Release | **Draft** / out of this CR |
| 9 | Operations | infrastructure.md **Approved** for local three-service topology (cloud Open Questions remain) |

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

No Implementation=`Implemented` on FR-021–028, DR-005/006, ML-012, or ADR-014–017. NFR-003 stays **Implemented** for existing fixture CI.

No orphan FR/IMP/TEST among the CR-005 mint set. Canonical map is traceability.

## Lock checks

| Lock | Result | Evidence |
|---|---|---|
| Labeled simulation; fake e-coins; not a real-money book; sportsbook language off gamecast; `/slate` may use stake/settle | **Held** | PRD/SRS CON-009/ADR-014; TEST-019 vs TEST-028 |
| Basketball only; extra sports wait; Compose + Postgres; no Kafka/Redis/K8s/GCP | **Held** | Charter/PRD; infrastructure three services |
| `?user=demo-1\|demo-2`; Postgres users/wallet/stake; no passwords; ADR-009 stays | **Held** | ADR-014; api-design |
| Persist scheduled/unplayed; P from prior completed history; CI scheduled rows; live keeps null scores | **Held** | FR-021; TEST-003 step 6; TEST-020; TEST-025; ADR-015 |
| Even-money; lock until Finished; house = system wallet; one open stake per (user, game); settle **in pipeline**; `/slate` displays only | **Held** | FR-023; TEST-021; api-design; error-handling; ADR-015 |
| New stake only if scores null **and** `game_start_time` future UTC; cancel/replace before tip | **Held** | FR-023; `replace` default false; 409 only when false |
| Keep gamecast `GET /`; add `/slate` and `/board`; producer-bar three-way links; same instrument family | **Held** | ADR-016; FR-015/024/025 |
| Demo users start at **1000**; no refill; reject below-zero; house **1000000000** OK | **Held** | FR-022; database-design |
| `/slate` = next **20** unplayed pre-tip (NBA+WNBA mixed) **plus** that user’s open stakes | **Held** | FR-024; TEST-023 |
| Uncapped live NBA; no age-prune; CI fixtures small; retrain NBA **and** WNBA; CI 48-game pin unchanged; 0.623 does not bind; same protocol/hyperparameters/`feature_version`; test once | **Held** | DR-001; ML-012; ADR-006 prune vs ADR-017; ml-design |
| WNBA fixture 2021–2025 + 2026 scheduled; no live WNBA HTTP | **Held** | FR-016; ADR-017; TEST-026 |
| Live board = `GET /board` in-progress only; gamecast no score/clock; no invented clock | **Held** | FR-025; TEST-024 |
| Adapter-only newest-page poll in **etl** image; not a fourth service; browser polls AthletIQ; no WebSockets; default **30s** | **Held** | ADR-015; infrastructure Approved |
| Live NBA player boxes on same no-key host; CI/WNBA player rows fixture | **Held** as **target** | FR-027; TEST-025; code still `return []` until IMP-020 |
| Keep synthetic Market P (ADR-012); live odds wait | **Held** | ADR-012; FUTURE-006 not pulled |
| Integer stakes min 1, max unlocked balance | **Held** | FR-023; api-design |
| NFR-003: CI fixture-only / injected HTTP; no live provider in GHA | **Held** | TEST-025; IMP-025 |
| ADR-017 **extends** ADR-011; does **not** supersede | **Held** | ADR-017 decision 6; decisions README |

## Required independent checks

| Check | Result | Evidence |
|---|---|---|
| CR-005 registered and Accepted | **Pass** | `id-registry.md`; CR file |
| FR-021–028 / DR-005/006 / ML-012 / IMP-019–025 / TEST-020–028 registered | **Pass** | `id-registry.md` |
| No Implementation=`Implemented` for unbuilt CR-005 | **Pass** | traceability |
| CON-009 allows labeled e-coin sim; forbids real-money book | **Pass** | SRS CON-009 |
| ADR-011 not superseded by ADR-017 | **Pass** | ADR-017; README |
| Gamecast vs `/slate` vs `/board` separated | **Pass** | ADR-016 |
| Settle in pipeline, not on `/slate` | **Pass** | ADR-015; api-design; error-handling; TEST-021 step 7 |
| NFR-003 no live HTTP in CI | **Pass** | TEST-025; IMP-025 |
| CI 48-game pin unchanged; 0.623 non-binding | **Pass** | ML-012; TEST-027 |
| Code baseline not claimed Implemented | **Pass** | IMP-019–025 Not started |
| TEST-019 vs TEST-020–028 | **Pass** | TEST-019 Passing; CR-005 cases Planned |
| Orphan FR/IMP/TEST in the CR-005 mint set | **Pass** | traceability + plan maps |
| TEST-003 vs keep-null-score lock | **Pass** | CR5-001 CLOSED |
| SRS FR-021 / ADR-015 / TEST-025 still aligned | **Pass** | Keep null scores; pipeline settle; injected HTTP; status not hardcoded Finished |

## Accepted ADR consequences (014–017 + 009/012 + 006)

| ADR | Consequences present? | Follow-through in docs | Verdict |
|---|---|---|---|
| ADR-009 | Yes — `?user=` is not auth | api-design none | **Held** |
| ADR-012 | Yes — e-coin ≠ live odds | FUTURE-006 not pulled | **Held** |
| ADR-014 | Yes — schema + JSON; CON-009; house design constant | `replace` specified | **Held** |
| ADR-015 | Yes — status/scores; settle stage; poll default; WNBA board fixture | TEST-003 no longer breaks keep-null; `/slate` display-only | **Held** |
| ADR-016 | Yes — two extra static pages | PRODUCT.md / api-design | **Held** |
| ADR-017 | Yes — newest-page poll; 0.623 non-binding; depth-3 clamp removed on live path | ml-design; ADR-006 prune exception; does not supersede ADR-011 | **Held** |
| ADR-006 | Yes — immutable raw; prune does not age-cut live NBA | ADR-006 v1.1.1 vs ADR-017 | **Held** |

## Code drift baseline (target vs HEAD)

| Concern | Docs target | Code / contract today | Verdict |
|---|---|---|---|
| Null-score live games | Keep; status not hardcoded Finished | `to_provider_game` returns `None`; status always `"Finished"` | Expected until IMP-020; TEST-003 no longer freezes the old behavior |
| Live player boxes | Same host; persist rows | `fetch_players` / `fetch_player_game_stats` return `[]` | Expected until IMP-020 |
| Season cap | No live clamp / no age-prune | `season_depth: int = 3` + stop when mapped rows are before window | Expected until IMP-020 |
| Ledger / `/slate` / `/board` / `replace` | Migration 003 + routes + body flag | No `users` tables; OpenAPI not yet extended | Expected until IMP-019/023 |

Do not treat the current mapper as the CR-005 contract.

## What is sound

- Prior REJECT items CR5-001–009 are addressed in the owning docs without inventing extra sports, live WNBA HTTP, live odds, Kafka, or application auth.
- TEST-003 / IMP-025 no longer make “keep TEST-001–019 passing” require dropping null-score live rows.
- Replace discriminator is specified before OpenAPI (IMP-023).
- Settle math in TEST-021 is now falsifiable (win formula + lose path + replace + idempotence + window-closed + display-only).
- Infrastructure local topology is Approved; cloud Open Questions remain out of this CR.

## What not to do

- Do **not** keep skip-missing-scores in IMP-020 to make an old TEST-003 green.
- Do not supersede ADR-011, add a fourth Compose service, call `nbaapi.com` from the browser, settle on `GET /slate`, or bind 0.623 / retune the 48-game CI pin.
- Do not mark FR-021–028 Implemented until the IMPs are Done.
- Do not treat this APPROVE as code-complete; same-model code review remains IMP DoD after implementation.

## Disposition

**APPROVE.** Gate 6 (IMP-019–025) **may start**.

Must-fix from the prior REJECT: **none remaining.**

## Validation

- [x] Only this review artifact was authored (plus memory pointers to this APPROVE)
- [x] No Grill-Me
- [x] No Charter/PRD/SRS/ADR/design/IMP/test-plan/code edits
- [x] Accepted ADR-014–017 consequences checked; ADR-009/012/011/006 checked
- [x] CR-005 Implementation columns are not Implemented
- [x] Code spot-check used only as drift baseline
- [x] CR5-001…009 disposition table complete
