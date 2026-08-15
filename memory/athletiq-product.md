# AthletIQ product

## Must never miss

- Working name is **AthletIQ** — use it in Charter, PRD, and all project artifacts.
- **Product vs project purpose:** PRD = sports analytics + NBA ingestion/analysis + pre-game win/lose predictions via API; Charter = portfolio/engineering-demonstration objectives and deliberate **technical constraints** (Docker, FastAPI, GHA, API-Sports family constraint historically, LR/XGBoost). Solo **personal/portfolio** GitHub build — not an organizational product (yet). Full goals/non-goals: Approved PRD + Charter — do not copy bodies here.
- **Personas:** primary product user = sports/data **analyst or developer** (local/API); project **stakeholder** = project owner; **artifact audience** = technical reviewers (not product users).
- **MVP prediction / ML temporal invariant:** pre-game home win/lose — binary + `P(home wins)` (designated team = **home**, SRS ML-002). No post-tip information may influence features, training, selection, or evaluation (no leakage).
- **MVP models / split / selection (locks):** two baselines + LR + XGBoost; temporal ~70/15/15 by `game_start_time` (ML-003); select on validation log loss (ML-007 / ADR-003; tie → LR); test once for ML-005. Beat **domain-informed** baseline on **test log loss**. Historical depth: **CR-004** = **3 Must** completed NBA seasons + overlapping WNBA; older = prune (DR-001). Detail: Approved SRS + design.
- **Features:** MVP was team L5/L10 only. **CR-004** feature version `team_l5_l10_player_agg_v1` adds team-aggregated top-5-by-minutes L5 pts/minutes. Artifact + train/serve: joblib + JSON metadata (ML-009 / ADR-004); same `feature_version` train and inference (ML-008). Full feature/DQ/retry specs: Approved Gate 4 design — point, do not paste.
- **2026-08-15** · `SOURCE: consolidate` · **WHY:** Merged overlapping data-source and provider-access bullets (newest: user Accepted CR-002/ADR-011). **Data source:** **NBA Stats API** (`api.server.nbaapi.com`, no key) via **ADR-011 / CR-002** (ADR-002 superseded). Live CLI `--provider nba-stats` (no key). All provider I/O through adapter. CI/Compose demo stay **fixture**. PRD stays provider-abstract. `season` query param unreliable — page newest-first and filter by date/`gameId`. Do not send RapidAPI / Highlightly / BALLDONTLIE / API-Sports signup URLs. Live WNBA HTTP is **out** this CR (nbaapi.com is NBA-only). Adapter shape: `integration-invariants`. Live `--provider nba-stats` still games/teams only (player features cold-start 0.0).
- **Architecture locks:** Binding ADRs **001, 003–006, 008–013** (ADR-002 superseded; ADR-012 synthetic odds; ADR-013 per-league pins). Thin pointers only — PostgreSQL; immutable raw JSON (ADR-006); API `game_id` BIGINT + precomputed features (ADR-008/010); **no application auth** on MVP demo API (ADR-009); GHA lint/unit/integration/image only (NFR-003); NFR-004 no hard SLOs; GCP future only (ADR-007 non-binding). API error codes / ML-ops monitoring: Approved Gate 4 design.
- **CR-001 (Accepted 2026-08-13):** MVP persist/ingest = **teams, games, team_game_stats**. **CR-004 (Accepted 2026-08-15)** loads reserved `players` / `player_game_stats`, WNBA fixtures, labeled synthetic odds. Do not treat CR-001 “players reserved” as current scope.
- **2026-08-16** · `SOURCE: consolidate` · **WHY:** Gamecast user lock supersedes Comp A desk-density; dropped Gate-6 status gossip (CI/attest → `engineering-lifecycle`; migrate 002 → `integration-invariants`). **Vehicle:** Accepted `docs/11-change-management/CR-004-post-mvp-wnba-players-odds-ui.md`. **Locked:** WNBA only (same basketball grain); shared schema + feature builder with **separate pins per league** (no pooled classifier); history = 3 completed NBA seasons + overlapping WNBA; inference stays `game_id`-keyed; no injury feed; no embeddings; **no book**; odds this CR = fixture/synthetic `source=synthetic`; live odds adapter later when a provider is named; keep ADR-001/006/008/009 — extend in-plane only; no Kafka/Redis/K8s/GCP; predict does not call a book. **UI:** broadcast win-probability **gamecast** on same FastAPI `GET /` (producer bar; Home/Away model P vs implied 1−P; dormant dashes until lookup; Home/Away role colors only; thinner synthetic Market P; always-on methodology/limitations chyrons; no score/clock/quarter; no sportsbook language; predict adds team name/abbreviation from `teams` / FR-020). Dramatic-improvement bar still in force — incremental chrome on the old gray form is **not** enough. Comp A desk and Comp B/C / film-room are anti-references. Fixture `xgboost-v1` leaf overconfidence remains a separate pin from live `logistic_regression-v1`.
- **Baseline probability grain (CRIT-004):** Naive and domain-informed baselines emit hard 0/1 probabilities; wrong picks yield log loss near the clip epsilon. ML-005 is therefore easier vs a calibrated baseline — matches locked Grill-Me baseline definitions; **do not** recalibrate baselines to ease ML-005.
- **Live LR ConvergenceWarning (CRIT-001):** Pin `logistic_regression-v1` — approved disposition is disclosure in `docs/06-design/model-card.md` Known limitations + `api/app/methodology.py` `LIMITATIONS_TEXT`, not retune `max_iter` after inspecting test log loss 0.623. Process lock: `engineering-lifecycle`.
- **Publish bar / Gate status:** owned by `engineering-lifecycle`. Do not reopen CR-001 or the 9/10 docs loop unless a new contradiction. Owner ticked PRD MVP acceptance (v1.0.5, 2026-08-15).
- **2026-08-15** · `SOURCE: sweep` · **Fixture pin `xgboost-v1` extremes (audit):** On the attest/demo stack, repeating ~0.96 / ~0.08 `P(home_win)` and identical floats across `game_id`s are **expected** shallow-tree behavior on the 48-game two-team fixture — not UI cache and not calibrated NBA skill. **Do not** retune against these 48 scores (test already used for ML-005). **Do not** mix this pin with live NBA pin `logistic_regression-v1` when judging calibration. Pointer: `docs/06-design/model-card.md` Known limitations item 3.

## Notes

- **2026-08-13** · `SOURCE: sweep` · CR-001 propagated across SRS/PRD/design/traceability; dual docs review **9/10** closed honesty pass.
- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Dropped Approved-doc body copies (feature lists, retry/backoff, goals enumeration, architecture prose); kept agent-facing locks + ADR/SRS/CR pointers. Status (local ML-005 numbers, NFR-001 attest path) discarded — see review pointers in `engineering-lifecycle`.
- **2026-08-16** · `SOURCE: consolidate` · **WHY:** UI Must-never-miss now gamecast; ep_2026-08-15_002 desk-ship `next` superseded by later same-day gamecast grill (do not collapse episode).

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
