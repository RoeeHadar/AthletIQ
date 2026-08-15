# Product Requirements Document — AthletIQ

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-15  
Version: 1.1.1

> Product / user view. Sponsorship, portfolio objectives, and deliberate technical constraints: `docs/01-project/project-charter.md`.  
> No implementation decisions belong here (specific vendors, container orchestrators, ML algorithms as mandated designs, table DDL, class structures). Those live in Charter constraints (portfolio must-demonstrate), ADRs, and design docs.

## Product overview

**AthletIQ** is a sports analytics system that collects and analyzes historical **NBA and WNBA** basketball data and provides ML-based predictions of game outcomes through an API and a local same-origin UI.

The **project** is designed as a reproducible portfolio artifact demonstrating end-to-end data, ML, software, and DevOps engineering (see Charter for project purpose and technical constraints).

## Problem statement

Sports outcome questions (“who is more likely to win?”) are hard to answer without a coherent path from historical data → validated storage → analysis → models → a queryable prediction interface. Fragmented tutorials rarely produce one system a user can run end-to-end.

AthletIQ’s **product** problem: enable a local analyst/developer to ingest NBA (and overlapping WNBA) history, analyze performance, evaluate predictive models under a defined methodology, and obtain pre-game win/lose predictions via an API — with known limitations documented.

## Goals

1. Reproducible local run: documented setup yields a working end-to-end pipeline and prediction API without manually patching source.
2. Predictive evaluation: a defined baseline and ML models are trained and compared on the same held-out games using only pre-game information.
3. Prediction access: the system returns a binary winner designation and `P(designated team wins)` for a supported matchup context.
4. Quality automation: continuous integration verifies lint, unit tests, integration tests, and container image build on mainline changes.
5. Data trust: ingestion validates required fields, handles invalid/duplicate records per documented rules, and produces a reproducible validation report.



## Non-goals

- Betting **book** (stakes, accounts, payouts, live odds shopping). A labeled **synthetic Market P(home)** comparison is in scope (**CR-004**); a live book adapter is not.
- Mobile app
- Multi-tenant SaaS
- Live in-game prediction
- Paid user accounts
- Production-grade model serving (feature store, automated retraining, A/B testing, drift monitoring as required capabilities)
- Anything beyond a demo-grade API + documentation for external “customers”
- Extra sports/leagues beyond **WNBA** this iteration (further leagues later via `sport`/`league` columns)
- Injury feeds, player embeddings, or Comp B/C / film-room UI directions



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

## User journeys / use cases (MVP + CR-004)

1. **Bootstrap & ingest:** Configure documented environment → start local containerized stack → run documented pipeline orchestration → migrations, ingestion, and validation complete with logs/report.
2. **Analyze:** Inspect persisted NBA/WNBA entities/stats (including player box scores when loaded); run documented analytical queries (aggregations, windowed recent form).
3. **Evaluate models:** Train/evaluate baseline + ML models **per league** on held-out games; review reproducible metrics and limitations.
4. **Predict:** Request a pre-game win/lose prediction (binary + probability) via the HTTP API; optionally see labeled synthetic Market P; receive a documented response.
5. **Verify change:** Push triggers CI (lint, unit, integration, image build).
6. **Local UI:** Broadcast win-probability graphic at `GET /`; choose league; look up `game_id`; read model split vs synthetic Market P.



## High-level features


| Feature (product capability)                                                                                                                                 | MVP | This iteration (CR-004)                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Ingest NBA data from an external sports data provider via a reproducible ingestion process (adapter boundary)                                                | Yes | Live NBA Stats API remains NBA-only; **3** completed NBA seasons                                                                      |
| Persist teams, games, and team statistics                                                                                                                    | Yes | `sport` / `league` on teams and games                                                                                                 |
| Player / player-stat persistence                                                                                                                             | Schema reserved (CR-001) | **Load** `players` / `player_game_stats` (fixture-backed this CR)                                                             |
| SQL analytics (aggregations, window functions) over persisted **team** stats                                                                                 | Yes | Player-grain rolls used only as **team-aggregated** ML features                                                                       |
| Feature engineering from recent team stats **without temporal leakage**                                                                                      | Yes | New `feature_version`: team windows + top-5-by-minutes L5 pts/minutes                                                                 |
| Train/evaluate a baseline **and** at least two ML approaches on the same holdout (Charter constrains which families; algorithms finalized in ML design/ADRs) | Yes | **Separate pins per league** (no pooled classifier); same selection rule inside each league                                           |
| Win/lose prediction only (binary + probability)                                                                                                              | Yes | Plus labeled synthetic **Market P(home)** (not a book)                                                                                |
| HTTP prediction API (demo-grade)                                                                                                                             | Yes | League pin routing; nullable Market P                                                                                                 |
| Local prediction UI                                                                                                                                          | CR-003 pulled | **Broadcast gamecast** (producer bar + WP split + Market P); same FastAPI `GET /`                                                      |
| WNBA (same basketball grain)                                                                                                                                 | Future | **Yes** via **fixture** adapter this CR (no live WNBA HTTP; no BALLDONTLIE/key)                                                       |
| Reproducible containerized local deployment + pipeline orchestration                                                                                         | Yes | Unchanged 3-service Compose                                                                                                           |
| Automated CI: lint → unit → integration → image build                                                                                                        | Yes | Fixture-only (NFR-003)                                                                                                                |
| Documented evaluation methodology and known limitations with predictions                                                                                     | Yes | Disclose synthetic Market P and per-league pins                                                                                       |




## MVP scope

- **Domain:** NBA historical data; depth target **2–3 recent completed seasons** (MVP). **CR-004** raises live/fixture NBA depth to **3 completed seasons Must** and adds overlapping **WNBA** (fixture this CR).
- **Provider:** external sports data provider (specific vendor/plan is a Charter/architecture decision, not a PRD lock). Live NBA = NBA Stats API (ADR-011). WNBA live HTTP = not this CR.
- **Prediction:** pre-game win/lose with binary + `P(win)` for a designated team; temporal boundary enforced.
- **Models (product expectation):** MVP **shall** implement a **baseline**, **logistic regression**, and **XGBoost**, compared on the **same** held-out evaluation set. (How they are packaged/trained is ML design.) **CR-004:** repeat that selection **inside each league**.
- **Delivery capabilities:** reproducible containerized local deployment; documented pipeline orchestration; demo HTTP API; CI through image build.
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

Still **no** betting **book**. Architecture may **document** where production ML ops would plug in later without implementing them in this iteration.



## Constraints (product-level)

- Secrets only via environment variables; never commit keys
- No SLA to external end customers
- Portfolio **technical must-demonstrate** constraints (Docker, CI, stack families, preferred provider): see **Charter** — not restated as product features here



## Assumptions

- The chosen external provider’s free/affordable tier can support MVP historical depth (2–3 seasons), possibly with multi-day backfill. `[ASSUMPTION — needs confirmation]`
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

Grill-Me Rounds 1–4 (2026-08-12); PRD revision from owner review (2026-08-12); **CR-001** (2026-08-13) team-level MVP persist; **CR-003** (2026-08-15) local UI; **CR-004** (2026-08-15) post-MVP Grill-Me close (WNBA, players, synthetic Market P, Comp A reconstruction). Charter: `docs/01-project/project-charter.md`.