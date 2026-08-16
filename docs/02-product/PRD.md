# Product Requirements Document — AthletIQ

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.2.0

> Product / user view. Sponsorship, portfolio objectives, and deliberate technical constraints: `docs/01-project/project-charter.md`.  
> No implementation decisions belong here (specific vendors, container orchestrators, ML algorithms as mandated designs, table DDL, class structures). Those live in Charter constraints (portfolio must-demonstrate), ADRs, and design docs.

## Product overview

**AthletIQ** is a sports analytics system that collects and analyzes historical **NBA and WNBA** basketball data and provides ML-based predictions of game outcomes through an API and a local same-origin UI.

The **project** is designed as a reproducible portfolio artifact demonstrating end-to-end data, ML, software, and DevOps engineering (see Charter for project purpose and technical constraints).

## Problem statement

Sports outcome questions (“who is more likely to win?”) are hard to answer without a coherent path from historical data → validated storage → analysis → models → a queryable prediction interface. Fragmented tutorials rarely produce one system a user can run end-to-end.

AthletIQ’s **product** problem: enable a local analyst/developer to ingest NBA (and overlapping WNBA) history, analyze performance, evaluate predictive models under a defined methodology, obtain pre-game win/lose predictions via an API, inspect an upcoming slate and an in-progress board, and run a **labeled e-coin simulation** of even-money home/away stakes — with known limitations documented.

## Goals

1. Reproducible local run: documented setup yields a working end-to-end pipeline and prediction API without manually patching source.
2. Predictive evaluation: a defined baseline and ML models are trained and compared on the same held-out games using only pre-game information.
3. Prediction access: the system returns a binary winner designation and `P(designated team wins)` for a supported matchup context.
4. Quality automation: continuous integration verifies lint, unit tests, integration tests, and container image build on mainline changes.
5. Data trust: ingestion validates required fields, handles invalid/duplicate records per documented rules, and produces a reproducible validation report.



## Non-goals

- **Real-money betting book** (payments, licensed gambling, juice, moneyline as a price). A **labeled e-coin simulation** (fake coins, even-money stake/settle, copy is stake/settle) is in scope (**CR-005**). A live odds adapter is **not** this CR; labeled **synthetic Market P(home)** stays the comparison column (**CR-004** / ADR-012).
- Mobile app
- Multi-tenant SaaS
- Live in-game *prediction* (using live score/clock as model features). An in-progress **gameboard** that *displays* provider scores is in scope (**CR-005**); gamecast at `GET /` still has no score/clock.
- Paid user accounts / passwords. Pick-a-demo-user (`demo-1` / `demo-2`) is in scope; ADR-009 stays.
- Production-grade model serving (feature store, automated retraining, A/B testing, drift monitoring as required capabilities). A one-shot retrain/select this CR is in scope.
- Anything beyond a demo-grade API + documentation for external “customers”
- Extra sports/leagues beyond **WNBA** this iteration (further leagues later via `sport`/`league` columns)
- Injury feeds, player embeddings, or Comp B/C / film-room UI directions
- Live WNBA HTTP; Kafka / Redis / Kubernetes / GCP
- Sportsbook chrome (odds, juice, moneyline, payout tables) on any UI surface



## Target users / personas


| Role                             | Kind                                       | Description                            | Needs                                                                       |
| -------------------------------- | ------------------------------------------ | -------------------------------------- | --------------------------------------------------------------------------- |
| Sports/data analyst or developer | **Primary product user**                   | Uses the system locally and/or via API | Ingest/inspect NBA and WNBA data; run analytics; evaluate models; obtain predictions |
| Project owner                    | **Project stakeholder**                    | Sole sponsor/operator (Charter)        | Publish a credible, gated engineering artifact                              |
| Technical reviewer               | **Artifact audience** (not a product user) | Evaluates the repository               | Architecture, code quality, tests, CI/CD, ML methodology, reproducibility   |




## Prediction semantics (MVP)

**Task:** Given two teams and a prediction context representing information available **before** the game, AthletIQ predicts:

- **Binary outcome:** designated team wins / opponent wins  
- **Probability:** `P(designated team wins)`

Binary and probability are the **same prediction task** (probability is the presentation of confidence for the binary outcome), not a separate product capability.

**Temporal boundary:** Predictions and training features must use only information that would have been available **before the predicted game’s start time**. Post-start or post-game information for that contest is out of bounds for that prediction.

**Designated team:** **Home team** (resolved in SRS ML-002, Grill-Me requirements Q1).

## Simulation semantics (CR-005)

**Not a book.** Fake e-coins. Copy is stake/settle — not odds, juice, moneyline, or payout tables. Model `P(home_win)` and synthetic Market P are analytics, not a price.

**Identity:** Two seeded demo users (`demo-1`, `demo-2`). No passwords. Selected user is `?user=` on `/slate`. ADR-009 stays (no login middleware).

**Wallets:** Each demo user starts at **1000** e-coins. No refill this CR. Reject a stake that would go below zero. House is a system wallet large enough to pay even-money wins.

**Stake:** Pick home or away and a **positive integer** (min 1, max = unlocked balance). One open stake per `(user, game)`. New stakes only if scores are still null **and** `game_start_time` is still in the future (UTC). Before tip: cancel (unlock) or replace. After tip: frozen until Finished ingest.

**Settle:** When the pipeline ingests a previously unplayed game as Finished, it settles every open stake on that game (correct → stake returned + equal credit; wrong → stake gone). Re-runs are idempotent. `/slate` displays only.

**Slate:** Next **20** unplayed pre-tip games by `game_start_time` (NBA + WNBA mixed) **plus** that user’s open stakes. Finished games leave this table.

**Board:** In-progress games only. Score + status; clock only if the provider sends one (do not invent). Live score updates are NBA via a Compose newest-page poll. WNBA board rows, if any, are fixture.

## User journeys / use cases (MVP + CR-004 + CR-005)

1. **Bootstrap & ingest:** Configure documented environment → start local containerized stack → run documented pipeline orchestration → migrations, ingestion, and validation complete with logs/report.
2. **Analyze:** Inspect persisted NBA/WNBA entities/stats (including player box scores when loaded); run documented analytical queries (aggregations, windowed recent form).
3. **Evaluate models:** Train/evaluate baseline + ML models **per league** on held-out games; review reproducible metrics and limitations.
4. **Predict:** Request a pre-game win/lose prediction (binary + probability) via the HTTP API; optionally see labeled synthetic Market P; receive a documented response.
5. **Verify change:** Push triggers CI (lint, unit, integration, image build).
6. **Local UI — gamecast:** Broadcast win-probability graphic at `GET /`; choose league; look up `game_id`; read model split vs synthetic Market P. No score/clock/quarter.
7. **Local UI — slate:** At `GET /slate`, pick `demo-1` / `demo-2` (`?user=`), see the next 20 unplayed pre-tip games plus open stakes, place/cancel/replace an integer even-money stake, read balance.
8. **Local UI — board:** At `GET /board`, see in-progress games (score + status; clock only if the provider sends one). Browser talks only to AthletIQ.
9. **Settle:** When ingest writes a game as Finished, the pipeline settles open stakes (idempotent). `/slate` displays; it does not settle.



## High-level features


| Feature (product capability)                                                                                                                                 | MVP | This iteration (CR-005)                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Ingest NBA data from an external sports data provider via a reproducible ingestion process (adapter boundary)                                                | Yes | Live NBA Stats API remains NBA-only; **no live season cap** (page everything); keep scheduled/in-progress rows; **live player boxes** |
| Persist teams, games, and team statistics                                                                                                                    | Yes | Unplayed games (null scores, not Finished); in-progress scores allowed on `/board` path                                               |
| Player / player-stat persistence                                                                                                                             | Schema reserved (CR-001) | **Load** live NBA boxes via `nba-stats`; WNBA/CI stay **fixture**                                                             |
| SQL analytics (aggregations, window functions) over persisted **team** stats                                                                                 | Yes | Unchanged grain                                                                                                                                 |
| Feature engineering from recent team stats **without temporal leakage**                                                                                      | Yes | Same `feature_version`; live NBA `player_agg` no longer all zeros                                                                     |
| Train/evaluate a baseline **and** at least two ML approaches on the same holdout                                                                             | Yes | **Retrain + reselect NBA and WNBA pins** (same protocol; test once). CI 48-game pin **unchanged**                                     |
| Win/lose prediction only (binary + probability)                                                                                                              | Yes | Plus labeled synthetic **Market P(home)** (not a book; **not** live odds this CR)                                                     |
| HTTP prediction API (demo-grade)                                                                                                                             | Yes | Plus slate/board/ledger JSON; no auth; `?user=` identity                                                                              |
| Local prediction UI                                                                                                                                          | CR-003 pulled | Gamecast `GET /` **unchanged** (no score/clock) + **`GET /slate`** + **`GET /board`**; producer-bar links; dramatic-improvement bar    |
| WNBA (same basketball grain)                                                                                                                                 | Future | **Fixture** 2021–2025 completed + 2026 scheduled (no live WNBA HTTP)                                                                  |
| Labeled e-coin simulation                                                                                                                                    | No  | Pick-a-demo-user; 1000 seed; integer even-money; pipeline settle; not a real book                                                     |
| Reproducible containerized local deployment + pipeline orchestration                                                                                         | Yes | Compose **board poll** (newest pages); 3-service topology + poll loop; no Kafka                                                       |
| Automated CI: lint → unit → integration → image build                                                                                                        | Yes | Fixture-only (NFR-003)                                                                                                                |
| Documented evaluation methodology and known limitations with predictions                                                                                     | Yes | Disclose uncapped history, live player boxes, new pins, synthetic Market P                                                            |




## MVP scope

- **Domain:** NBA historical data. **CR-004** was 3 completed NBA seasons Must + overlapping WNBA fixture. **CR-005** live NBA has **no season cap** (page everything `nba-stats` returns); CI fixtures stay small. WNBA Must = authored fixtures **2021–2025 completed + 2026 scheduled**.
- **Provider:** external sports data provider (specific vendor/plan is a Charter/architecture decision, not a PRD lock). Live NBA = NBA Stats API (ADR-011) including **player boxes** (CR-005). WNBA live HTTP = not this CR. Live odds = not this CR.
- **Prediction:** pre-game win/lose with binary + `P(win)` for a designated team; temporal boundary enforced. Upcoming `P(home_win)` uses **prior completed history only**.
- **Models (product expectation):** baseline, logistic regression, and XGBoost, compared on the **same** held-out evaluation set, **inside each league**. **CR-005:** retrain NBA and WNBA pins on the new history (same hyperparameters and `feature_version`; test once). CI 48-game fixture pin unchanged.
- **Delivery capabilities:** reproducible containerized local deployment; documented pipeline orchestration; demo HTTP API; CI through image build; gamecast + slate + board UI.
- **Documentation:** full roadmap (including post-MVP) and engineering decisions documented; **Approved** docs before non-trivial build (Charter/gates).



## MVP acceptance criteria

MVP is complete when all of the following are true:

- [x] Clean environment can execute documented setup
- [x] Historical NBA data is successfully ingested for the agreed season depth
- [x] ETL validation completes successfully and emits a reproducible validation report
- [x] Required relational data is persisted (teams, games, team statistics). Player tables may exist unused until a future CR.
- [x] Required SQL analytics execute successfully
- [x] Features can be generated without temporal leakage relative to prediction time
- [x] Baseline model is evaluated on the holdout set
- [x] Logistic regression is evaluated on the same holdout set
- [x] XGBoost is evaluated on the same holdout set
- [x] Evaluation results are reproducible from documented steps
- [x] Prediction API returns a valid binary + probability prediction for supported inputs
- [x] Predictions are accompanied by documented methodology and known limitations
- [x] Unit and integration tests pass
- [x] Container image build succeeds
- [x] GitHub Actions (or equivalent CI defined in devops docs) passes the agreed path
- [x] Documentation gates for the MVP slice are satisfied
- [x] No secrets are committed



## Future scope

- NumPy neural net from scratch (no PyTorch), after LR/XGBoost path works
- Richer predictions (score / spread)
- Live WNBA HTTP adapter (when a no-key or named provider is chosen)
- Live odds adapter (when the owner names a provider)
- Further leagues via `sport` / `league` columns
- Deploy/CD beyond image build — **future consideration**; GCP is a **candidate** host (ADR-007 Proposed), not an Accepted decision

Still **no** real-money betting **book**. The CR-005 e-coin ledger is a labeled simulation. Architecture may **document** where production ML ops would plug in later without implementing them in this iteration.



## Constraints (product-level)

- Secrets only via environment variables; never commit keys
- No SLA to external end customers
- Portfolio **technical must-demonstrate** constraints (Docker, CI, stack families, preferred provider): see **Charter** — not restated as product features here



## Assumptions

- The chosen external provider can support **uncapped** live NBA paging for a local demo (CR-005); CI stays on small fixtures. Multi-day backfill is acceptable. `[ASSUMPTION]`
- Baseline methodology defined in SRS ML-006 (naive + domain-informed); approved via requirements Grill-Me Q2 before evaluation.



## Success metrics


| Metric           | Target                                                                                                                                                                                                    |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reproducibility  | A new developer can clone the repo, configure the documented environment, and reproduce the documented pipeline and model evaluation **without manually modifying source code**                           |
| Local demo       | Scripted/documented path succeeds on a clean machine with documented prerequisites                                                                                                                        |
| Data quality     | ETL validates required fields, handles invalid/duplicate records per documented rules, and produces a reproducible validation report                                                                      |
| Model quality    | Per league: logistic regression and XGBoost compared to the approved baseline on the same held-out games; at least one ML model **beats** the domain-informed baseline on **test log loss** (SRS **ML-005**, **ML-010**) |
| API              | Returns valid binary + probability for supported pre-game inputs                                                                                                                                          |
| CI               | Lint, unit, integration, image build green on mainline pushes                                                                                                                                             |
| Security hygiene | No API keys or secrets in git history                                                                                                                                                                     |
| Docs             | README + docs through implementation plan; gates respected before build                                                                                                                                   |
| Honesty          | Evaluation methodology and known limitations are documented alongside predictions                                                                                                                         |


Exact numeric accuracy/AUC cutoffs are **not** product Musts. The relative quality bar is **ML-005**: strictly lower **test** log loss than the domain-informed baseline (synthetic TEST-007 is not NBA attestation).

## Risks


| Risk                                                             | Product impact                                          |
| ---------------------------------------------------------------- | ------------------------------------------------------- |
| Data leakage (post-game or in-game features used as if pre-game) | Inflated validation performance; misleading predictions |
| External provider schema / rate-limit changes                    | Ingestion failure or incomplete data                    |
| Historical data gaps                                             | Reduced training/evaluation quality                     |
| Class / season distribution shift                                | Poor generalization to future games                     |
| Provider quota / plan limits                                     | Incomplete seasons → weaker models / delayed MVP        |
| Over-scoping post-MVP or production ML ops into v1               | Delays publish bar                                      |
| Undocumented decisions during coding                             | Breaks docs-before-build goal                           |




## Limitations (product expectation)

AthletIQ does **not** claim to “accurately predict NBA games” as a product guarantee. It evaluates whether available historical information provides predictive signal under a **defined evaluation methodology**, and surfaces **known limitations** with predictions and model cards.

## Source

Grill-Me Rounds 1–4 (2026-08-12); PRD revision from owner review (2026-08-12); **CR-001** (2026-08-13) team-level MVP persist; **CR-003** (2026-08-15) local UI; **CR-004** (2026-08-15) post-MVP Grill-Me close (WNBA, players, synthetic Market P, Comp A reconstruction); **CR-005** (2026-08-16) platform-slice Grill-Me Q1–Q27 confirmed. Charter: `docs/01-project/project-charter.md`.