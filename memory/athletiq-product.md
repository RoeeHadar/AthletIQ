# AthletIQ product

## Must never miss

- Working name is **AthletIQ** — use it in Charter, PRD, and all project artifacts.
- **Product vs project purpose:** PRD = sports analytics + NBA ingestion/analysis + pre-game win/lose predictions via API; Charter = portfolio/engineering-demonstration objectives and deliberate **technical constraints** (Docker, FastAPI, GHA, API-Sports family constraint historically, LR/XGBoost). Solo **personal/portfolio** GitHub build — not an organizational product (yet). Full goals/non-goals: Approved PRD + Charter — do not copy bodies here.
- **Personas:** primary product user = sports/data **analyst or developer** (local/API); project **stakeholder** = project owner; **artifact audience** = technical reviewers (not product users).
- **MVP prediction / ML temporal invariant:** pre-game home win/lose — binary + `P(home wins)` (designated team = **home**, SRS ML-002). No post-tip information may influence features, training, selection, or evaluation (no leakage).
- **MVP models / split / selection (locks):** two baselines + LR + XGBoost; temporal ~70/15/15 by `game_start_time` (ML-003); select on validation log loss (ML-007 / ADR-003; tie → LR); test once for ML-005. Beat **domain-informed** baseline on **test log loss**. Historical depth: **CR-005 live NBA** = **no season cap** (page everything `nba-stats` returns; do not age-prune). **CI fixtures stay small.** **WNBA fixture Must** = 2021–2025 completed + 2026 scheduled. CR-004’s 3-season live window is superseded for live NBA. Detail: Approved SRS + design.
- **Features:** MVP was team L5/L10 only. **CR-004** feature version `team_l5_l10_player_agg_v1` adds team-aggregated top-5-by-minutes L5 pts/minutes. Artifact + train/serve: joblib + JSON metadata (ML-009 / ADR-004); same `feature_version` train and inference (ML-008). Full feature/DQ/retry specs: Approved Gate 4 design — point, do not paste.
- **2026-08-16** · `SOURCE: agent` · **WHY:** CR-005 Gate 6 code landed locally. **HOW:** Live NBA player boxes are on the same `nba-stats` host; mapper does not hard-return `[]`. Adapter shape: `integration-invariants`. Do not send RapidAPI / Highlightly / BALLDONTLIE / API-Sports signup URLs. Live WNBA HTTP is **out**.
- **Architecture locks:** Binding ADRs **001, 003–006, 008–017** (ADR-002 superseded; ADR-012 synthetic odds; ADR-013 per-league pins; ADR-014 e-coin ledger / no auth; ADR-015 scheduled + board poll + pipeline settle; ADR-016 three surfaces; ADR-017 uncapped live NBA + player boxes). Thin pointers only — PostgreSQL; immutable raw JSON (ADR-006); API `game_id` BIGINT + precomputed features (ADR-008/010); **no application auth** on MVP demo API (ADR-009; `?user=` is not auth); GHA lint/unit/integration/image only (NFR-003); NFR-004 no hard SLOs; GCP future only (ADR-007 non-binding). API error codes / ML-ops monitoring: Approved Gate 4 design.
- **CR-001 (Accepted 2026-08-13):** MVP persist/ingest = **teams, games, team_game_stats**. **CR-004 (Accepted 2026-08-15)** loads reserved `players` / `player_game_stats`, WNBA fixtures, labeled synthetic odds. Do not treat CR-001 “players reserved” as current scope.
- **2026-08-16** · `SOURCE: consolidate` · **WHY:** Gamecast user lock supersedes Comp A desk-density; dropped Gate-6 status gossip (CI/attest → `engineering-lifecycle`; migrate 002 → `integration-invariants`); fixture-pin sentence moved to dedicated bullet below. **Vehicle:** Accepted `docs/11-change-management/CR-004-post-mvp-wnba-players-odds-ui.md`. **Locked:** WNBA only (same basketball grain); shared schema + feature builder with **separate pins per league** (no pooled classifier); history = **3 completed NBA seasons** + overlapping WNBA (Accepted CR-004 — do not rewrite as CR-005); inference stays `game_id`-keyed; no injury feed; no embeddings; **no book**; odds this CR = fixture/synthetic `source=synthetic`; live odds adapter later when a provider is named; keep ADR-001/006/008/009 — extend in-plane only; no Kafka/Redis/K8s/GCP; predict does not call a book. **UI:** broadcast win-probability **gamecast** on same FastAPI `GET /` (producer bar; Home/Away model P vs implied 1−P; dormant dashes until lookup; Home/Away role colors only; thinner synthetic Market P; always-on methodology/limitations chyrons; no score/clock/quarter; no sportsbook language; predict adds team name/abbreviation from `teams` / FR-020). Dramatic-improvement bar still in force — incremental chrome on the old gray form is **not** enough. Comp A desk and Comp B/C / film-room are anti-references.
- **Baseline probability grain (CRIT-004):** Naive and domain-informed baselines emit hard 0/1 probabilities; wrong picks yield log loss near the clip epsilon. ML-005 is therefore easier vs a calibrated baseline — matches locked Grill-Me baseline definitions; **do not** recalibrate baselines to ease ML-005.
- **Live LR ConvergenceWarning (CRIT-001):** Pin `logistic_regression-v1` — approved disposition is disclosure in `docs/06-design/model-card.md` Known limitations + `api/app/methodology.py` `LIMITATIONS_TEXT`, not retune `max_iter` after inspecting test log loss 0.623. Process lock: `engineering-lifecycle`.
- **Publish bar / Gate status:** owned by `engineering-lifecycle`. Do not reopen CR-001 or the 9/10 docs loop unless a new contradiction. Owner ticked PRD MVP acceptance (v1.0.5, 2026-08-15).
- **2026-08-15** · `SOURCE: sweep` · **Fixture pin `xgboost-v1` extremes (audit):** On the attest/demo stack, repeating ~0.96 / ~0.08 `P(home_win)` and identical floats across `game_id`s are **expected** shallow-tree behavior on the 48-game two-team fixture — not UI cache and not calibrated NBA skill. **Do not** retune against these 48 scores (test already used for ML-005). **Do not** mix this pin with live NBA pin `logistic_regression-v1` when judging calibration. Pointer: `docs/06-design/model-card.md` Known limitations item 3.
- **2026-08-16** · `SOURCE: agent` · **WHY:** Lead-dev docs rereview APPROVE. **HOW:** CR-005 Gate 6 (IMP-019–025) may start. Pointer: `docs/00-meta/reviews/2026-08-16-cr005-lead-dev-docs-rereview.md`.
- **2026-08-16** · `SOURCE: user` · **WHY:** Owner confirmed Grill-Me Q1–Q27; documenting then lead-developer review then code. **CR-005 (Accepted):** labeled e-coin simulation (not a real-money book); basketball platform slice; pick-a-demo-user `?user=demo-1|demo-2` (ADR-009 stays); persist scheduled/unplayed; even-money stake/settle in pipeline (idempotent); keep gamecast at `GET /`; add `GET /slate` (next 20 + open stakes) and `GET /board` (in-progress); 1000 e-coins no refill; pre-tip only; cancel/replace before tip; no NBA season cap; retrain NBA+WNBA same `feature_version` (CI 48-game pin unchanged; 0.623 does not bind); WNBA fixture 2021–2025 + 2026 scheduled; no live WNBA HTTP; live NBA player boxes on same host; keep synthetic Market P; adapter-only newest-page board poll (etl image, default 30s); no Kafka/Redis/WebSockets; browser never calls `nbaapi.com`. Gate 6 unblocked by rereview APPROVE (see newer bullet). Full locks: Approved CR/SRS/ADRs — point, do not paste.

## Notes

- **2026-08-16** · `SOURCE: consolidate` · **WHY:** Merged prior Notes hygiene (2026-08-13 honesty, 2026-08-14 dropped Approved-doc copies, 2026-08-16 gamecast supersession). Keep agent-facing locks + ADR/SRS/CR pointers; status/attest gossip → `engineering-lifecycle`. ep_2026-08-15_002 desk-ship `next` superseded by gamecast lock (do not collapse episode).

```yaml
id: ep_2026-08-16_001
time: 2026-08-16T08:47:00+03:00
what: "Owner opened CR-005 (more data/sports, users, e-coin simulation, upcoming-game board, live gameboard, platform scale) and required Grill-Me before implementation."
source_type: user
confidence: high
tags: [cr-005, grill-me, product-fork]
cause: "CR-005 is a product fork, not a small add-on — scope must be locked before Gate 2+"
next: "Superseded by ep_2026-08-16_002 (Q1=B, Q2=A locked)"
```

```yaml
id: ep_2026-08-16_002
time: 2026-08-16T08:52:00+03:00
what: "Owner answered Grill-Me Q2=A: CR-005 is the basketball platform slice — local accounts, e-coin ledger, upcoming NBA/WNBA slate with existing P(home_win), more history via live nba-stats; extra sports and live gameboard deferred; Compose+Postgres."
source_type: user
confidence: high
tags: [cr-005, grill-me, q2-lock, platform-slice]
cause: "Scope fork between basketball-first platform vs broader multi-sport sim"
next: "Superseded by ep_2026-08-16_003 (Q4=A locked)"
```

```yaml
id: ep_2026-08-16_003
time: 2026-08-16T14:48:00+03:00
what: "Owner answered Grill-Me Q4=A: persist scheduled/unplayed games as real rows (null scores, not Finished); P(home_win) from prior completed history only; CI fixtures include scheduled NBA/WNBA rows; live ingest keeps null-score rows when provider sends them."
source_type: user
confidence: high
tags: [cr-005, grill-me, q4-lock, scheduled-games]
cause: "Upcoming slate needs real DB rows without post-tip leakage into model features"
next: "Superseded by ep_2026-08-16_004 (Q5=A locked)"
```

```yaml
id: ep_2026-08-16_004
time: 2026-08-16T14:51:00+03:00
what: "Owner answered Grill-Me Q5=A: even-money simulation settle — pick home/away + stake; lock until Finished ingest; correct → stake+equal credit; wrong → stake gone; system house wallet; copy stake/settle not odds/juice/moneyline; model P is analytics not a price; one open stake per (user, game)."
source_type: user
confidence: high
tags: [cr-005, grill-me, q5-lock, e-coin, even-money-settle]
cause: "Stake/settle semantics must be locked before Gate 2 to avoid sportsbook drift"
next: "Superseded by ep_2026-08-16_005 (Q7=A locked)"
```

```yaml
id: ep_2026-08-16_005
time: 2026-08-16T14:55:00+03:00
what: "Owner answered Grill-Me Q7=A: each seeded demo user starts at 1000 e-coins; no refill this CR; reject a stake that would go below zero; house wallet large enough to pay even-money wins."
source_type: user
confidence: high
tags: [cr-005, grill-me, q7-lock, e-coin, wallet-seed]
cause: "Wallet scarcity is what makes the ledger worth storing and testing"
next: "Superseded by ep_2026-08-16_006 (Q8=A locked)"
```

```yaml
id: ep_2026-08-16_006
time: 2026-08-16T15:13:00+03:00
what: "Owner answered Grill-Me Q8=A: settle in the pipeline when a previously unplayed game is ingested as Finished; re-runs are idempotent; /slate only displays balances and open/settled rows."
source_type: user
confidence: high
tags: [cr-005, grill-me, q8-lock, e-coin, pipeline-settle]
cause: "Ledger should move when the game becomes real, not when a browser refreshes"
next: "Superseded by ep_2026-08-16_007 (Q9=A locked)"
```

```yaml
id: ep_2026-08-16_007
time: 2026-08-16T15:15:00+03:00
what: "Owner answered Grill-Me Q9=A: new stake only if scores are still null and game_start_time is still in the future (UTC); after tip, reject new stakes; open stakes wait for Finished ingest then settle."
source_type: user
confidence: high
tags: [cr-005, grill-me, q9-lock, e-coin, pre-tip-stake]
cause: "Tip time is already on the row; do not invent a live clock this CR"
next: "Superseded by ep_2026-08-16_008 (Q10=A locked)"
```

```yaml
id: ep_2026-08-16_008
time: 2026-08-16T15:16:00+03:00
what: "Owner answered Grill-Me Q10=A: cancel or replace an open stake before tip (still one open row per user, game); after tip, frozen until pipeline settle."
source_type: user
confidence: high
tags: [cr-005, grill-me, q10-lock, e-coin, cancel-replace]
cause: "Demo needs undo while the game has not started"
next: "Superseded by ep_2026-08-16_009 (Q11=A locked)"
```

```yaml
id: ep_2026-08-16_009
time: 2026-08-16T15:17:00+03:00
what: "Owner answered Grill-Me Q11=A: /slate upcoming table is next 20 unplayed pre-tip games by game_start_time (NBA+WNBA mixed) plus that user’s open stakes; Finished games leave the table."
source_type: user
confidence: high
tags: [cr-005, grill-me, q11-lock, slate-window]
cause: "Twenty plus open stakes is demo-sized and still a real upcoming board"
next: "Superseded by ep_2026-08-16_010 (Q12=B locked)"
```

```yaml
id: ep_2026-08-16_010
time: 2026-08-16T15:18:00+03:00
what: "Owner answered Grill-Me Q12=B: widen DR-001 this CR (more completed NBA seasons). Depth number not yet chosen. Live player-box HTTP and live WNBA HTTP still not implied."
source_type: user
confidence: high
tags: [cr-005, grill-me, q12-lock, dr-001, season-depth]
cause: "Owner wants more live NBA history in this CR, not only scheduled-row ingest"
next: "Superseded by ep_2026-08-16_011 (Q13=C locked)"
```

```yaml
id: ep_2026-08-16_011
time: 2026-08-16T15:20:00+03:00
what: "Owner answered Grill-Me Q13=C: no NBA season cap — live nba-stats pages everything the API returns; NBA prune window goes away; CI fixtures stay small. Not 4 or 5 seasons."
source_type: user
confidence: high
tags: [cr-005, grill-me, q13-lock, dr-001, unbounded-history]
cause: "Owner chose unbounded live NBA history over a 4/5-season window"
next: "Superseded by ep_2026-08-16_012 (Q14=B locked)"
```

```yaml
id: ep_2026-08-16_012
time: 2026-08-16T15:22:00+03:00
what: "Owner answered Grill-Me Q14=B: retrain + reselect this CR on the new uncapped history — new pin, new temporal split, new ML-005 (test once). Old live test log loss 0.623 does not bind the new pin. Which artifacts get replaced is still open."
source_type: user
confidence: high
tags: [cr-005, grill-me, q14-lock, retrain, ml-005]
cause: "Uncapped NBA history is not useful if the live pin stays trained on the old window"
next: "Superseded by ep_2026-08-16_013 (Q15=A amended NBA+WNBA pins)"
```

```yaml
id: ep_2026-08-16_013
time: 2026-08-16T15:24:00+03:00
what: "Owner answered Grill-Me Q15 as A amended: retrain NBA and WNBA pins this CR; do not retrain the CI 48-game fixture pin. Owner: add WNBA to this plan, not just NBA. Live WNBA HTTP not yet chosen."
source_type: user
confidence: high
tags: [cr-005, grill-me, q15-lock, wnba, pins]
cause: "Owner rejected NBA-only retrain; CI toy pin still should not be churned"
next: "Superseded by ep_2026-08-16_014 (Q16=A locked)"
```

```yaml
id: ep_2026-08-16_014
time: 2026-08-16T15:26:00+03:00
what: "Owner answered Grill-Me Q16=A: WNBA stays fixture this CR (no live WNBA HTTP); expand authored WNBA fixtures and scheduled rows; retrain WNBA pin on fixture; WNBA history is not unbounded like live NBA. How many fixture seasons still open."
source_type: user
confidence: high
tags: [cr-005, grill-me, q16-lock, wnba, fixture]
cause: "nbaapi.com is NBA-only; owner chose fixture WNBA over naming a live WNBA host"
next: "Superseded by ep_2026-08-16_015 (Q17=C locked)"
```

```yaml
id: ep_2026-08-16_015
time: 2026-08-16T15:27:00+03:00
what: "Owner answered Grill-Me Q17=C: author five completed WNBA fixture seasons (2021–2025) plus 2026 scheduled rows. Not four and not 2023–2024-only."
source_type: user
confidence: high
tags: [cr-005, grill-me, q17-lock, wnba, fixture-depth]
cause: "Owner wanted a larger authored WNBA window than the recommended four completed seasons"
next: "Superseded by ep_2026-08-16_016 (Q18=A locked)"
```

```yaml
id: ep_2026-08-16_016
time: 2026-08-16T15:31:00+03:00
what: "Owner answered Grill-Me Q18=A: same training protocol, same hyperparameters, same feature_version; new artifacts only; do not iterate on the new test set; live player HTTP still out."
source_type: user
confidence: high
tags: [cr-005, grill-me, q18-lock, train-protocol]
cause: "Data window is the experiment; do not hunt hyperparameters or redesign features in the same CR"
next: "Superseded by ep_2026-08-16_017 (Q19=A locked)"
```

```yaml
id: ep_2026-08-16_017
time: 2026-08-16T15:33:00+03:00
what: "Owner answered Grill-Me Q19=A: two-way producer-bar links between gamecast GET / and GET /slate; same origin; do not restyle the bar into a marketing nav."
source_type: user
confidence: high
tags: [cr-005, grill-me, q19-lock, slate, navigation]
cause: "Slate must be discoverable without fighting the gamecast instrument chrome"
next: "Superseded by ep_2026-08-16_018 (Q20=A locked)"
```

```yaml
id: ep_2026-08-16_018
time: 2026-08-16T15:34:00+03:00
what: "Owner answered Grill-Me Q20=A: selected demo user is a query param ?user=demo-1 (or demo-2); switcher updates the URL; refresh keeps identity; no cookies / ADR-009 stays."
source_type: user
confidence: high
tags: [cr-005, grill-me, q20-lock, demo-user, query-param]
cause: "Visible shareable identity without pretending the API is a login product"
next: "Superseded by ep_2026-08-16_019 (Q21=A locked)"
```

```yaml
id: ep_2026-08-16_019
time: 2026-08-16T15:35:00+03:00
what: "Owner answered Grill-Me Q21=A: /slate is the same broadcast-instrument family as gamecast; dramatic-improvement bar applies; not a gray admin table, not a second NBA.com desk, not sportsbook chrome."
source_type: user
confidence: high
tags: [cr-005, grill-me, q21-lock, slate, visual-bar]
cause: "Owner already rejected incremental gray UI on gamecast; /slate must not regress to an admin table"
next: "Superseded by ep_2026-08-16_020 (Q22=A locked; frontier empty pending confirm)"
```

```yaml
id: ep_2026-08-16_020
time: 2026-08-16T15:36:00+03:00
what: "Owner answered Grill-Me Q22=A: stakes are positive integers; min 1; max = available unlocked balance; no fractional coins. Grill frontier empty pending owner confirmation of shared understanding."
source_type: user
confidence: high
tags: [cr-005, grill-me, q22-lock, e-coin, integer-stake]
cause: "Integer stakes are enough to prove the ledger"
next: "Superseded by ep_2026-08-16_021 (recap amended; confirmation withdrawn)"
```

```yaml
id: ep_2026-08-16_021
time: 2026-08-16T15:38:00+03:00
what: "Owner amended CR-005 recap before confirm: wants to add live gameboard, live player boxes, live odds, and a real book. Q1–Q22 not reversed yet. Charter/PRD still list betting products / live book as non-goals until an explicit reversal."
source_type: user
confidence: high
tags: [cr-005, grill-me, amendment, real-book, live-gameboard]
cause: "Four deferred branches were reopened as one amendment; they are not one decision"
next: "Superseded by ep_2026-08-16_022 (Q23=A locked)"
```

```yaml
id: ep_2026-08-16_022
time: 2026-08-16T15:40:00+03:00
what: "Owner answered Grill-Me Q23=A: keep Q1=B labeled sim; no real-money book, no payments, no sportsbook license; Charter/PRD book non-goal stays. Live gameboard, live player boxes, and live odds remain to be grilled."
source_type: user
confidence: high
tags: [cr-005, grill-me, q23-lock, labeled-sim, no-real-book]
cause: "Real book would be a licensed gambling product, not this portfolio sim"
next: "Superseded by ep_2026-08-16_023 (Q24=A locked)"
```

```yaml
id: ep_2026-08-16_023
time: 2026-08-16T15:42:00+03:00
what: "Owner answered Grill-Me Q24=A: live gameboard this CR as GET /board (in-progress only); gamecast stays no score/clock; no invented clock; producer-bar links; same instrument family; no sportsbook chrome."
source_type: user
confidence: high
tags: [cr-005, grill-me, q24-lock, live-gameboard, board]
cause: "Owner wanted a live board without putting score/clock on the gamecast"
next: "Superseded by ep_2026-08-16_024 (Q25=A locked)"
```

```yaml
id: ep_2026-08-16_024
time: 2026-08-16T15:43:00+03:00
what: "Owner answered Grill-Me Q25=A: adapter-only Compose board poll of newest nba-stats pages; upsert in-progress NBA games; full unbounded history stays the pipeline job; browser polls AthletIQ not nbaapi.com; no Kafka/WebSockets."
source_type: user
confidence: high
tags: [cr-005, grill-me, q25-lock, board-poll, adapter]
cause: "Newest-page poll makes /board live without re-paging all history"
next: "Superseded by ep_2026-08-16_025 (Q26=A locked)"
```

```yaml
id: ep_2026-08-16_025
time: 2026-08-16T15:44:00+03:00
what: "Owner answered Grill-Me Q26=A: live NBA player boxes this CR on the same no-key nba-stats host; live NBA player_agg no longer cold-start 0.0; CI and WNBA player rows stay fixture; no keyed signup. Live odds still open."
source_type: user
confidence: high
tags: [cr-005, grill-me, q26-lock, live-player-boxes, nba-stats]
cause: "Same host already documents per-game player boxes; retrain already in the CR"
next: "Superseded by ep_2026-08-16_026 (Q27=B locked; frontier empty pending confirm)"
```

```yaml
id: ep_2026-08-16_026
time: 2026-08-16T15:46:00+03:00
what: "Owner answered Grill-Me Q27=B: keep synthetic Market P this CR; live odds adapter waits until a later CR when a provider is named. Amendment branch closed: no real book, live /board + poll, live NBA player boxes, synthetic odds stay."
source_type: user
confidence: high
tags: [cr-005, grill-me, q27-lock, synthetic-odds, adr-012]
cause: "nbaapi.com is not an odds feed; even-money settle does not need a live price"
next: "Superseded by ep_2026-08-16_confirm (owner confirmed; CR-005 Accepted)"
```

```yaml
id: ep_2026-08-16_confirm
time: 2026-08-16T12:48:00Z
what: "Owner confirmed CR-005 shared understanding and authorized documentation, then lead-developer docs review, then Gate 6 only if that review APPROVES."
source_type: user
confidence: high
tags: [cr-005, confirmed, documentation, lead-review]
cause: "Grill-Me Q1–Q27 closed; product fork is Accepted CR-005"
next: "Lead-developer docs review; no application code until APPROVE"
```

```yaml
id: ep_2026-08-15_001
time: 2026-08-15T01:16:00+03:00
what: "Owner flagged repeating extreme P(home_win) on UI; live audit of attest pin xgboost-v1 (48 games, 2 teams) found 12 distinct probabilities, 44/48 below 0.10 or above 0.90, identical floats from shared XGBoost leaves — serving is honest, not a cache bug."
source_type: observation
confidence: high
tags: [fixture-pin, xgboost-v1, probability-audit, calibration]
cause: "Shallow XGBoost on two-team fixture with discrete rolling features collapses to pure leaves"
next: "Do not retune on fixture 48; use live NBA pipeline for meaningful probability spread"
```

```yaml
id: ep_2026-08-15_002
time: 2026-08-15T20:51:00+03:00
what: "Owner rejected CR-004 UI pass as visually unchanged — league dropdown + Market P column on old Comp A shell did not meet dramatic-improvement bar; agent rebuilt GET / as NBA.com/Stats desk (mast, Q disc, STATS lockup, league in header, box-score chrome, Market P); Impeccable finish review ship."
source_type: user_feedback
confidence: high
tags: [cr-004, ui, comp-a, impeccable, desk-density]
cause: "Prior pass added features without changing first-viewport visual identity"
next: "Superseded same day by gamecast UI lock in Must never miss — desk is anti-reference"
```
