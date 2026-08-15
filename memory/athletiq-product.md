# AthletIQ product

## Must never miss

- Working name is **AthletIQ** — use it in Charter, PRD, and all project artifacts.
- **Product vs project purpose:** PRD = sports analytics + NBA ingestion/analysis + pre-game win/lose predictions via API; Charter = portfolio/engineering-demonstration objectives and deliberate **technical constraints** (Docker, FastAPI, GHA, API-Sports family constraint historically, LR/XGBoost). Solo **personal/portfolio** GitHub build — not an organizational product (yet). Full goals/non-goals: Approved PRD + Charter — do not copy bodies here.
- **Personas:** primary product user = sports/data **analyst or developer** (local/API); project **stakeholder** = project owner; **artifact audience** = technical reviewers (not product users).
- **MVP prediction / ML temporal invariant:** pre-game home win/lose — binary + `P(home wins)` (designated team = **home**, SRS ML-002). No post-tip information may influence features, training, selection, or evaluation (no leakage).
- **MVP models / split / selection (locks):** two baselines + LR + XGBoost; temporal ~70/15/15 by `game_start_time` (ML-003); select on validation log loss (ML-007 / ADR-003; tie → LR); test once for ML-005. Beat **domain-informed** baseline on **test log loss**. Historical depth: **2 Must / ≤3 Should** completed NBA seasons (DR-001); older = prune. Detail: Approved SRS + design.
- **MVP features (locks):** **team-level only**; rolling last-5/10 + season-to-date; cold start `min_prior_games = 5` → season aggregates. **No player-level features in MVP.** Artifact + train/serve: joblib + JSON metadata (ML-009 / ADR-004); same `feature_version` train and inference (ML-008). Full feature/DQ/retry specs: Approved Gate 4 design — point, do not paste.
- **2026-08-15** · `SOURCE: consolidate` · **WHY:** Merged overlapping data-source and provider-access bullets (newest: user Accepted CR-002/ADR-011). **Data source:** **NBA Stats API** (`api.server.nbaapi.com`, no key) via **ADR-011 / CR-002** (ADR-002 superseded). Live CLI `--provider nba-stats` (no key). All provider I/O through adapter. CI/Compose demo stay **fixture**. PRD stays provider-abstract. `season` query param unreliable — page newest-first and filter by date/`gameId`. Do not send RapidAPI / Highlightly / BALLDONTLIE / API-Sports signup URLs. Do not expand to multi-sport in this CR. Adapter shape: `integration-invariants`.
- **Architecture locks:** Binding ADRs **001, 003–006, 008–011** (ADR-002 superseded). Thin pointers only — PostgreSQL; immutable raw JSON (ADR-006); API `game_id` BIGINT + precomputed features (ADR-008/010); **no application auth** on MVP demo API (ADR-009); GHA lint/unit/integration/image only (NFR-003); NFR-004 no hard SLOs; GCP future only (ADR-007 non-binding). API error codes / ML-ops monitoring: Approved Gate 4 design.
- **CR-001 (Accepted 2026-08-13):** MVP persist/ingest = **teams, games, team_game_stats** (+ features). `players` / `player_game_stats` = **reserved / post-MVP**; do not advertise or implement player load unless a later CR.
- **Baseline probability grain (CRIT-004):** Naive and domain-informed baselines emit hard 0/1 probabilities; wrong picks yield log loss near the clip epsilon. ML-005 is therefore easier vs a calibrated baseline — matches locked Grill-Me baseline definitions; **do not** recalibrate baselines to ease ML-005.
- **Live LR ConvergenceWarning (CRIT-001):** Pin `logistic_regression-v1` — approved disposition is disclosure in `docs/06-design/model-card.md` Known limitations + `api/app/methodology.py` `LIMITATIONS_TEXT`, not retune `max_iter` after inspecting test log loss 0.623. Process lock: `engineering-lifecycle`.
- **Publish bar / Gate status:** owned by `engineering-lifecycle`. Do not reopen CR-001 or the 9/10 docs loop unless a new contradiction. **2026-08-15** · `SOURCE: user` · Owner ticked PRD MVP acceptance (v1.0.5).
- **2026-08-15** · `SOURCE: user` · **Stated next (not Accepted scope):** generalize the model — more data, more sports, more context — then consider betting, then further UI. Betting and multi-sport remain PRD non-goals / FUTURE until a CR is Accepted. Do not implement from this preference. Player-level context still needs a CR past CR-001.
- **2026-08-15** · `SOURCE: sweep` · **Local prediction UI (FR-015 / CR-003 Approved):** Same-origin `GET /` static on FastAPI (`api/static/`), not a separate frontend. Pointer: `docs/11-change-management/CR-003-minimal-prediction-ui.md`. Visual world: category-standard sports dashboard (owner rejected film-room); craft bar **NBA.com/Stats**; approved comp A (`.impeccable/mocks/comp-a-header-lookup.png`). Design refs: `PRODUCT.md`, shipped `DESIGN.md`. Prediction as box-score table row, not gauge. Lookup by integer `game_id` only — no game list, betting, or odds chrome.
- **2026-08-15** · `SOURCE: sweep` · **Fixture pin `xgboost-v1` extremes (audit):** On the attest/demo stack, repeating ~0.96 / ~0.08 `P(home_win)` and identical floats across `game_id`s are **expected** shallow-tree behavior on the 48-game two-team fixture — not UI cache and not calibrated NBA skill. **Do not** retune against these 48 scores (test already used for ML-005). **Do not** mix this pin with live NBA pin `logistic_regression-v1` when judging calibration. Pointer: `docs/06-design/model-card.md` Known limitations item 3.

## Notes

- **2026-08-13** · `SOURCE: sweep` · CR-001 propagated across SRS/PRD/design/traceability; dual docs review **9/10** closed honesty pass.
- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Dropped Approved-doc body copies (feature lists, retry/backoff, goals enumeration, architecture prose); kept agent-facing locks + ADR/SRS/CR pointers. Status (local ML-005 numbers, NFR-001 attest path) discarded — see review pointers in `engineering-lifecycle`.

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
