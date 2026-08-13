# Software Requirements Specification — AthletIQ

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-14  
Version: 1.4.2

> Gate 2 **Approved** (amended 1.4.0 / **CR-001**: team-level persist; **CR-002**: live provider ADR-011).

## Sources

- `docs/01-project/project-charter.md` (Approved 1.0.1)
- `docs/02-product/PRD.md` (Approved 1.0.4; CR-001)
- Grill-Me requirements Q1–Q6 (accepted as recommended)
- `docs/11-change-management/CR-001-mvp-team-stats-not-players.md` (Accepted)
- `docs/11-change-management/CR-002-nba-stats-api-provider.md` (Accepted)

## Conventions

Each requirement includes: ID, Description, Rationale, Priority (`Must` | `Should` | `Could`), Source, Acceptance Criteria, Dependencies, Architecture refs, Design refs, Tests.

Unresolved items use `[OPEN QUESTION: …]` only after Grill-Me.

Post-MVP (NumPy NN, score/spread, second league, minimal UI, cloud deploy): **Could** / Future — not required for Gate 2 MVP Must set.

---

## Functional requirements

### FR-001 — Ingest NBA data via provider adapter

- **Description:** The system shall ingest NBA historical data from an external sports data provider through a dedicated adapter boundary (provider-specific HTTP/schema isolated from core transform/load).
- **Rationale:** PRD ingestion capability + replaceable provider; Charter adapter boundary.
- **Priority:** Must  
- **Source:** PRD features; Charter CON provider  
- **Acceptance Criteria:**
  - Adapter can fetch teams, games, and team statistics needed for DR-002 **MVP** themes for the configured seasons.
  - Player fetch/persist is **out of MVP** (**CR-001**); `players` / `player_game_stats` may exist as reserved schema only.
  - Core ETL transform/load does not embed provider-specific URLs/auth beyond configuration injected at the adapter.
  - Ingestion is runnable via the documented pipeline (FR-011).
- **Dependencies:** CON-001, CON-007, DR-001  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/error-handling.md`; `docs/05-decisions/ADR-006-raw-landing.md`  
- **Tests:** TEST-003  

### FR-002 — Persist core entities and statistics

- **Description:** The system shall persist **teams, games, and team statistics** in the system of record. Player and player-statistics tables may exist as **reserved schema** and are not an MVP load outcome (**CR-001**).
- **Rationale:** PRD MVP persistence (amended CR-001).  
- **Priority:** Must  
- **Source:** PRD; CR-001  
- **Acceptance Criteria:**
  - After a successful pipeline run, each **MVP** entity theme in DR-002 (teams, games, team statistics) has stored rows for the configured seasons (allowing documented provider gaps).
  - Game records include enough information to determine home/away and final winner for completed games used in training/eval.
  - Empty `players` / `player_game_stats` after a pipeline run is expected, not a defect.
- **Dependencies:** CON-002, FR-001, DR-002  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/database-design.md`  
- **Tests:** TEST-002, TEST-004  

### FR-003 — SQL analytics

- **Description:** The system shall support SQL analytics including aggregations (e.g. totals by season) and window functions (e.g. rolling recent performance) over persisted **team** statistics.
- **Rationale:** PRD analytics journey; Charter SQL constraint; **CR-001**.  
- **Priority:** Must  
- **Source:** PRD; Charter; CR-001  
- **Acceptance Criteria:**
  - Documented example SQL for aggregation and windowed rolling **team** stats exists and is covered by TEST-005 (exact results on mini fixtures; in-memory clone of the window semantics). Executing those queries against a live Postgres after pipeline load is **not** the TEST-005 bar.
  - Player top-scorer SQL is **not** an MVP pipeline outcome (reserved schema / optional in-memory helper only).
- **Dependencies:** FR-002, CON-002  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/database-design.md`  
- **Tests:** TEST-005  

### FR-004 — Feature engineering under temporal boundary

- **Description:** The system shall generate model features from recent **team** statistics such that no feature for a game uses information unavailable before that game’s start (ML-001). Player-level ML features are post-MVP (**CR-001** / ml-design).
- **Rationale:** PRD features + leakage risk.  
- **Priority:** Must  
- **Source:** PRD; CR-001  
- **Acceptance Criteria:**
  - Feature generation for game G uses only data with timestamps &lt; start of G.
  - Automated tests or documented validation checks fail the build/pipeline if a known leakage pattern is introduced (details in test plan).
- **Dependencies:** FR-002, FR-003, ML-001  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-006  

### FR-005 — Naive baseline evaluation

- **Description:** The system shall evaluate a **naive baseline** on the **test** partition (ML-003) and record primary/secondary metrics (ML-004). Validation metrics may be reported for comparison but do not drive selection of baselines as served models.
- **Rationale:** Grill-Me Q2; PRD; architecture review train/val/test.  
- **Priority:** Must  
- **Source:** PRD; Grill-Me Q2; architecture review  
- **Acceptance Criteria:**
  - Naive baseline per ML-006 evaluated on the **test** set.
  - Metrics written to a reproducible evaluation artifact/report.
- **Dependencies:** ML-003, ML-004, ML-006, FR-004  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

### FR-006 — Domain-informed baseline evaluation

- **Description:** The system shall evaluate a **domain-informed baseline** on the **same test** partition and record metrics.
- **Rationale:** Grill-Me Q2; architecture review.  
- **Priority:** Must  
- **Source:** Grill-Me Q2; PRD  
- **Acceptance Criteria:**
  - Domain-informed baseline per ML-006 evaluated on the same **test** game IDs as FR-005/007/008 final report.
  - Metrics appear in the same evaluation report format.
- **Dependencies:** ML-003, ML-004, ML-006, FR-004  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

### FR-007 — Logistic regression train/evaluate

- **Description:** The system shall train logistic regression on the **train** partition, score **validation** for selection candidacy, and report **test** metrics once.
- **Rationale:** PRD; CON-008; ADR-003.  
- **Priority:** Must  
- **Source:** PRD; Charter; ADR-003  
- **Acceptance Criteria:**
  - Trained using only pre-game features (ML-001).
  - Validation and test log loss + accuracy recorded; test not used for fitting or selection.
- **Dependencies:** FR-004, ML-001, ML-002, ML-003, CON-008  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

### FR-008 — XGBoost train/evaluate

- **Description:** The system shall train XGBoost on **train**, score **validation** for selection candidacy, and report **test** metrics once.
- **Rationale:** PRD; CON-008; ADR-003.  
- **Priority:** Must  
- **Source:** PRD; Charter; ADR-003  
- **Acceptance Criteria:**
  - Same temporal constraints as FR-007.
  - Validation and test metrics recorded alongside baselines and LR.
- **Dependencies:** FR-004, ML-001, ML-002, ML-003, CON-008  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

### FR-009 — Prediction API

- **Description:** The system shall expose a **synchronous** HTTP API that, given a **`game_id`**, returns binary home win/lose and `P(home wins)` using the feature row `(game_id, feature_version)` and the batch-pinned model (ADR-008).
- **Rationale:** PRD; ADR-008; architecture review.  
- **Priority:** Must  
- **Source:** PRD; ADR-008  
- **Acceptance Criteria:**
  - Completes within a single HTTP request lifecycle (no async job for MVP).
  - Uses shared feature implementation / precomputed row; does not live-recompute a divergent feature path.
  - Includes lineage fields per FR-014 / ML-009.
  - Does not train, fetch provider data, mutate datasets, or select models per request.
- **Dependencies:** ML-002, ML-008, ML-009, FR-014, CON-004, ADR-003, ADR-008  
- **Architecture refs:** `docs/04-architecture/api-architecture.md`  
- **Design refs:** `docs/06-design/api-design.md`; `docs/06-design/error-handling.md`  
- **Tests:** TEST-008  

### FR-014 — Prediction lineage

- **Description:** Predictions shall be traceable to `model_version`, `feature_version`, and published training lineage metadata (dataset/code/config as available).
- **Rationale:** Architecture review — ML reproducibility.  
- **Priority:** Must  
- **Source:** Architecture review 2026-08-12  
- **Acceptance Criteria:** Predict responses include `model_version` and `feature_version`; model metadata documents dataset_version, code_commit, training_config.  
- **Dependencies:** FR-009, ML-009, ADR-003, ADR-004, ADR-008  
- **Architecture refs:** `docs/04-architecture/api-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/api-design.md`  
- **Tests:** TEST-008, TEST-014  

### FR-010 — Methodology and limitations disclosure

- **Description:** Predictions and evaluation outputs shall be accompanied by documented evaluation methodology and known limitations (model card or equivalent).
- **Rationale:** PRD honesty / limitations.  
- **Priority:** Must  
- **Source:** PRD  
- **Acceptance Criteria:**
  - Documented methodology describes split, metrics, baselines, and temporal boundary.
  - Known limitations are linked or returned in a documented location for API consumers/operators.
- **Dependencies:** FR-005, FR-006, FR-007, FR-008, FR-009  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`; `docs/06-design/model-card.md`  
- **Tests:** TEST-012

### FR-011 — Pipeline orchestration

- **Description:** The system shall provide `scripts/run_pipeline.sh` (or documented equivalent) as a thin entrypoint that checks environment and invokes a **Python pipeline orchestrator** implementing staged: ingest → validate → transform/load → features → train/validate → test-eval → publish. Stages should be independently rerunnable where safe.
- **Rationale:** Charter CON-006; architecture review (Python owns orchestration).  
- **Priority:** Must  
- **Source:** Charter; architecture review  
- **Acceptance Criteria:**
  - Documented script + Python module path succeed on configured env.
  - Execution failures → non-zero exit; quality-gate failures recorded without requiring infra crash semantics.
- **Dependencies:** FR-001, FR-013, OPS-002, CON-006, ADR-005  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/error-handling.md`  
- **Tests:** TEST-009  

### FR-012 — Containerized local deployment

- **Description:** The MVP shall provide a reproducible containerized local deployment with distinct services for ETL workload, database, and API.
- **Rationale:** PRD delivery; Charter Compose default.  
- **Priority:** Must  
- **Source:** PRD; Charter CON-003  
- **Acceptance Criteria:**
  - Documented Compose file defines database, ETL-capable environment, and API (TEST-010 = static topology / `docker compose config`).
  - End-to-end local demo (pipeline into Postgres + API serving the pin) is **NFR-001**, documented in root `README.md`. It is **not** closed by TEST-010.
- **Dependencies:** CON-003, FR-009, FR-011  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/09-devops/infrastructure.md`  
- **Tests:** TEST-010

### FR-013 — ETL validation report

- **Description:** ETL shall validate required fields, apply documented rules for invalid/duplicate records, and emit a reproducible validation report.
- **Rationale:** PRD data-quality success metric.  
- **Priority:** Must  
- **Source:** PRD  
- **Acceptance Criteria:**
  - Each successful or partially successful run produces a report artifact (path documented).
  - Rules for invalid/duplicate handling are documented and reflected in the report counts.
- **Dependencies:** FR-001, FR-002  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/error-handling.md`  
- **Tests:** TEST-004

### DR-001 — Season depth

- **Description:** MVP shall ingest **at least 2** recent completed NBA seasons (**Must**). Ingesting **3** recent completed seasons is **Should** when provider quotas allow.
- **Rationale:** PRD 2–3 seasons; Grill-Me Q4 free-tier safety.  
- **Priority:** Must (2) / Should (3)  
- **Source:** PRD; Grill-Me Q4  
- **Acceptance Criteria:**
  - Configuration documents which seasons were ingested.
  - Must fails if fewer than 2 completed seasons are successfully loaded without an approved CR.
- **Dependencies:** FR-001, CON-007  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md` (active window)  
- **Tests:** TEST-003, TEST-004  

### DR-002 — Entity themes

- **Description:** System of record shall support **MVP** entity themes: teams, games, team statistics. Schema may also define **reserved** player and player-statistics tables for post-MVP; those themes are not an MVP persistence Must (**CR-001**).
- **Rationale:** PRD (amended CR-001).  
- **Priority:** Must (MVP themes) / Future (player themes)  
- **Source:** PRD; CR-001  
- **Acceptance Criteria:** Schema/design lists MVP themes; FR-002 persistence verified for teams, games, team statistics. Reserved player tables may be empty after a pipeline run.  
- **Dependencies:** FR-002  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/database-design.md`  
- **Tests:** TEST-002, TEST-004  

### DR-003 — Idempotent curated loads

- **Description:** ETL load into curated tables shall be idempotent (or explicitly deduplicated) so rerunning the pipeline does not create duplicate teams/games/team statistics (MVP grain). Reserved player grain is out of MVP load (**CR-001**).
- **Rationale:** Architecture review; NFR-001 reproducibility.  
- **Priority:** Must  
- **Source:** Architecture review 2026-08-12  
- **Acceptance Criteria:** Running transform/load twice against the same raw batch does not duplicate curated grain rows.  
- **Dependencies:** FR-002, FR-001, ADR-006  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/database-design.md`  
- **Tests:** TEST-004  

---

## Machine learning requirements

### ML-001 — Temporal boundary

- **Description:** Training and inference features for a game must not include information generated at or after that game’s start time.
- **Rationale:** PRD temporal boundary; leakage risk.  
- **Priority:** Must  
- **Source:** PRD  
- **Acceptance Criteria:** Enforced in feature pipeline; covered by tests (FR-004).  
- **Dependencies:** FR-004  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-006  

### ML-002 — Designated team = home

- **Description:** The designated team for binary outcome and probability is the **home team**. API and labels use home-win formulation.
- **Rationale:** Grill-Me Q1.  
- **Priority:** Must  
- **Source:** Grill-Me Q1  
- **Acceptance Criteria:** Labels, metrics, and API probability all refer to home win.  
- **Dependencies:** FR-009  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/api-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`; `docs/06-design/api-design.md`  
- **Tests:** TEST-006, TEST-007, TEST-008  

### ML-003 — Temporal train / validation / test

- **Description:** Games shall be partitioned by start time into **train**, **validation**, and **test** sets (no random shuffle across time). Exact cut points are defined in ML design. All models share the same partitions.
- **Rationale:** Architecture review — avoid selecting on the final test set; supersedes single ~20% holdout selection.  
- **Priority:** Must  
- **Source:** Architecture review 2026-08-12 (amends Grill-Me Q5)  
- **Acceptance Criteria:**
  - Documented temporal cuts; identical partition membership for all models.
  - Train games strictly earlier than validation; validation strictly earlier than test.
  - Test used only for final reporting, not fitting or model selection.
- **Dependencies:** FR-005–FR-008, ML-007  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

### ML-004 — Metrics

- **Description:** **Primary** metric is **log loss**. **Secondary** metric is classification **accuracy**. Selection uses validation primary metric; “beats baseline” (ML-005) uses **test** primary metric.
- **Rationale:** Grill-Me Q3; architecture review.  
- **Priority:** Must  
- **Source:** Grill-Me Q3; architecture review  
- **Acceptance Criteria:** Reports label validation vs test metrics distinctly.  
- **Dependencies:** FR-005–FR-008  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

### ML-005 — Beat domain-informed baseline on test

- **Description:** At least one of logistic regression or XGBoost shall achieve **strictly lower test log loss** than the domain-informed baseline. Naive baseline reported for context. Failure is a **quality gate** failure, not necessarily an execution crash.
- **Rationale:** PRD; architecture review.  
- **Priority:** Must  
- **Source:** PRD; architecture review  
- **Acceptance Criteria:** Final report shows min(LR, XGB) **test** log loss &lt; domain-informed baseline **test** log loss.  
- **Dependencies:** FR-006, FR-007, FR-008, ML-004  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007 (quality gate; synthetic until NBA attestation)  

### ML-006 — Baseline definitions

- **Description:**
  - **Naive:** predict home win for every game (constant home-win prior).
  - **Domain-informed:** predict the team with the better pre-game **season win rate** available before tip-off (temporal boundary respected); if tied, predict home.
- **Rationale:** Grill-Me Q2.  
- **Priority:** Must  
- **Source:** Grill-Me Q2  
- **Acceptance Criteria:** Definitions implemented and documented in ML design / model card; used by FR-005/006.  
- **Dependencies:** ML-001, ML-002  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`; `docs/06-design/model-card.md`  
- **Tests:** TEST-007  

### ML-007 — Model selection uses validation only

- **Description:** Served-model selection among LR and XGBoost shall use **validation** log loss only (ADR-003). Test metrics must not influence selection.
- **Rationale:** Architecture review — prevent test leakage into selection.  
- **Priority:** Must  
- **Source:** ADR-003; architecture review  
- **Acceptance Criteria:** Selection pin metadata records validation scores; test scores recorded separately after pin.  
- **Dependencies:** ML-003, ML-004, ADR-003  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`; `docs/05-decisions/ADR-003-served-model-selection.md`  
- **Tests:** TEST-007  

### ML-008 — Training–serving feature consistency

- **Description:** Training and inference shall use a **single authoritative feature implementation** (shared module or machine-readable spec) and the same preprocessing for a given `feature_version`.
- **Rationale:** Architecture review — avoid divergent train/serve functions.  
- **Priority:** Must  
- **Source:** Architecture review 2026-08-12  
- **Acceptance Criteria:** One feature-builder path feeds feature tables; API reads those rows; tests catch divergent windows/imputation.  
- **Dependencies:** FR-004, FR-009, ADR-008  
- **Architecture refs:** `docs/04-architecture/api-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`; `docs/05-decisions/ADR-008-inference-feature-contract.md`  
- **Tests:** TEST-006  

### ML-009 — Published model lineage metadata

- **Description:** Every published model artifact shall record `model_version`, `feature_version`, `dataset_version`, `code_commit`, and `training_config` (or documented equivalents).
- **Rationale:** Architecture review — dataset→model→API lineage.  
- **Priority:** Must  
- **Source:** Architecture review 2026-08-12  
- **Acceptance Criteria:** Publish step writes metadata consumed by API pin; model card references the same ids.  
- **Dependencies:** FR-010, FR-014, ADR-003, ADR-004  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`; `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`; `docs/05-decisions/ADR-004-artifact-storage.md`  
- **Tests:** TEST-007, TEST-013, TEST-014  

---

## Security requirements

### SEC-001 — Secrets via environment

- **Description:** Provider API keys and credentials shall be supplied only via environment variables (or equivalent secret injection), never hard-coded.
- **Rationale:** PRD/Charter.  
- **Priority:** Must  
- **Source:** PRD; Charter  
- **Acceptance Criteria:** Documented env vars; no secrets in source.  
- **Dependencies:** —  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/error-handling.md`  
- **Tests:** TEST-001, TEST-003  

### SEC-002 — No secrets in version control

- **Description:** The repository shall not contain API keys or secrets.
- **Rationale:** PRD security hygiene.  
- **Priority:** Must  
- **Source:** PRD  
- **Acceptance Criteria:** Secret scanning / review checklist in CI or docs; sample `.env.example` without real secrets.  
- **Dependencies:** SEC-001  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/09-devops/ci-cd.md`  
- **Tests:** TEST-001, TEST-011  

---

## Non-functional requirements

### NFR-001 — Reproducibility

- **Description:** A new developer shall be able to clone the repository, configure the documented environment, and reproduce the documented pipeline and model evaluation without manually modifying source code.
- **Rationale:** PRD reproducibility metric.  
- **Priority:** Must  
- **Source:** PRD  
- **Acceptance Criteria:** Documented steps exist in root `README.md` (copy `.env.example`, `docker compose up -d --build`, canonical `--store postgres` fixture pipeline, `/v1/health` + `/v1/model`). Clean-machine success is **owner attestation or scripted smoke** — not TEST-013. TEST-013 covers training-repeatability only. Until owner attestation is recorded, the clean-machine slice is **Partial**.  
- **Dependencies:** FR-011, FR-012, FR-005–FR-008  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-001, TEST-013  

### NFR-002 — Demo-grade; no external SLA

- **Description:** The system is demo-grade for local/portfolio use; it shall not require multi-tenant tenancy, paid accounts, or production uptime SLAs.
- **Rationale:** PRD non-goals.  
- **Priority:** Must  
- **Source:** PRD  
- **Acceptance Criteria:** No requirements or features introduce paid auth/multi-tenant SaaS in MVP.  
- **Dependencies:** —  
- **Architecture refs:** `docs/04-architecture/api-architecture.md`  
- **Design refs:** `docs/06-design/api-design.md`  
- **Tests:** TEST-008  

### NFR-003 — CI independent of live provider

- **Description:** Continuous integration shall not depend on availability, rate limits, or mutable live responses from API-Sports (or other production sports APIs).
- **Rationale:** Architecture review — deterministic CI.  
- **Priority:** Must  
- **Source:** Architecture review 2026-08-12  
- **Acceptance Criteria:** Default CI uses fixtures/recorded payloads; no required live provider call for green builds.  
- **Dependencies:** OPS-001, CON-005  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/09-devops/ci-cd.md`  
- **Tests:** TEST-011  

### NFR-004 — No hard latency/availability SLOs in MVP

- **Description:** MVP shall **not** require published numeric latency (e.g. p99) or availability SLOs for the prediction API or database. The API remains **synchronous** (single request lifecycle). Soft expectation: local demo predict completes without async offload.
- **Rationale:** NFR-002 demo-grade; earlier Grill-Me deferred SLOs as N/A for portfolio MVP. Makes the N/A **explicit** so design does not invent load-test targets.  
- **Priority:** Must  
- **Source:** Design review 2026-08-12; PRD non-goals  
- **Acceptance Criteria:** No Must requirement for cloud-style SLOs in MVP docs; OpenAPI/API design cite NFR-004; indexes may still exist for local usability (not as SLO proof).  
- **Dependencies:** NFR-002, FR-009  
- **Architecture refs:** `docs/04-architecture/api-architecture.md`  
- **Design refs:** api-design.md, database-design.md  
- **Tests:** TEST-008  

### NFR-005 — Local query access paths indexed

- **Description:** Schema shall include indexes supporting common ordered analytics/feature paths (e.g. stats joined to `games.game_start_time`, lookups by `team_id`; reserved `player_id` indexes may exist for post-MVP) so local demo queries and feature builds are practical — **without** implying a latency SLO (see NFR-004).
- **Rationale:** Design review — rolling-window access patterns need indexes even when SLOs are N/A.  
- **Priority:** Should  
- **Source:** Design review 2026-08-12  
- **Acceptance Criteria:** `schema.sql` / migrations define the indexes listed in database-design.  
- **Dependencies:** FR-003, FR-004, CON-002  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** database-design.md  
- **Tests:** TEST-002  

---

## Operational requirements

### OPS-001 — CI path

- **Description:** Continuous integration on push/PR shall run lint → unit tests → integration tests → container image build.
- **Rationale:** PRD; Charter; Grill-Me Q6 (stop before deploy).  
- **Priority:** Must  
- **Source:** PRD; Charter; Grill-Me Q6  
- **Acceptance Criteria:** GitHub Actions workflow implements the four stages; **local** TEST-011 asserts the DAG. Mainline **remote** green is a publish-bar item, not implied by IMP-011 Done.  
- **Dependencies:** CON-005  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/09-devops/ci-cd.md`  
- **Tests:** TEST-011  

### OPS-002 — Pipeline logging and failure reporting

- **Description:** Pipeline and services shall emit logs sufficient to diagnose failures; orchestration reports failures clearly.
- **Rationale:** Charter script intent; PRD bootstrap journey.  
- **Priority:** Must  
- **Source:** Charter; PRD  
- **Acceptance Criteria:** Failed ETL/migration steps leave inspectable logs and non-zero exit from FR-011.  
- **Dependencies:** FR-011  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/error-handling.md`; `docs/10-operations/logging.md`  
- **Tests:** TEST-001, TEST-009  

Cloud deploy/CD after image build: **out of MVP** (Grill-Me Q6). Future Consideration only.

---

## Constraints

### CON-001 — Python-based ETL

- **Description:** ETL shall be implemented in Python, exercising requests/pagination/JSON parsing/validation/error handling/logging/env configuration.
- **Priority:** Must  
- **Source:** Charter  
- **Acceptance Criteria:** ETL codebase is Python; behaviors demonstrable in tests/docs.  
- **Dependencies:** FR-001  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/07-implementation/implementation-plan.md` (IMP-001/009)  
- **Tests:** TEST-001, TEST-009  

### CON-002 — Relational SQL system of record

- **Description:** System of record shall be a relational SQL database supporting the analytics in FR-003.
- **Priority:** Must  
- **Source:** Charter  
- **Acceptance Criteria:** Data for DR-002 **MVP** themes lives in relational tables queryable by SQL.  
- **Dependencies:** FR-002, FR-003  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/06-design/database-design.md`  
- **Tests:** TEST-002  

### CON-003 — Docker Compose local topology (MVP default)

- **Description:** MVP local multi-service deployment shall use Docker Compose unless an Accepted ADR supersedes.
- **Priority:** Must  
- **Source:** Charter  
- **Acceptance Criteria:** Compose file defines database, ETL-related, and API services (FR-012).  
- **Dependencies:** FR-012  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/09-devops/infrastructure.md`  
- **Tests:** TEST-010  

### CON-004 — FastAPI (MVP default)

- **Description:** Prediction HTTP API shall use FastAPI unless an Accepted ADR supersedes.
- **Priority:** Must  
- **Source:** Charter  
- **Acceptance Criteria:** API service is FastAPI implementing FR-009.  
- **Dependencies:** FR-009  
- **Architecture refs:** `docs/04-architecture/api-architecture.md`  
- **Design refs:** `docs/06-design/api-design.md`  
- **Tests:** TEST-008  

### CON-005 — GitHub Actions

- **Description:** CI shall run on GitHub Actions implementing OPS-001.
- **Priority:** Must  
- **Source:** Charter  
- **Acceptance Criteria:** Workflows under `.github/workflows/` perform OPS-001.  
- **Dependencies:** OPS-001  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/09-devops/ci-cd.md`  
- **Tests:** TEST-011  

### CON-006 — Linux orchestration script

- **Description:** Provide a Linux-oriented orchestration script (`scripts/run_pipeline.sh`) meeting FR-011.
- **Priority:** Must  
- **Source:** Charter  
- **Acceptance Criteria:** Script exists and is documented for supported environments (WSL/Linux/macOS-bash as documented).  
- **Dependencies:** FR-011  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/05-decisions/ADR-005-training-as-batch.md`  
- **Tests:** TEST-009  

### CON-007 — External provider via adapter; NBA Stats API preferred

- **Description:** Ingestion shall use an adapter-facing external NBA provider. **Preferred** live provider is the no-key NBA Stats API (`api.server.nbaapi.com`) per ADR-011 / CR-002. Alternate adapters (fixtures; unused API-Sports fallback) may exist.
- **Priority:** Must  
- **Source:** Charter; PRD provider abstraction; CR-002  
- **Acceptance Criteria:** Adapter interface exists; live CLI path `--provider nba-stats` needs no API key; CI uses fixtures (NFR-003); secrets via SEC-001 when a keyed adapter is used.  
- **Dependencies:** FR-001, SEC-001  
- **Architecture refs:** `docs/04-architecture/data-architecture.md`  
- **Design refs:** `docs/05-decisions/ADR-011-nba-stats-api-provider.md`  
- **Tests:** TEST-003  

### CON-008 — MVP model families

- **Description:** MVP shall include naive baseline, domain-informed baseline, logistic regression, and XGBoost (FR-005–FR-008). NumPy-from-scratch NN is post-MVP (Could).
- **Priority:** Must  
- **Source:** Charter; PRD; Grill-Me Q2  
- **Acceptance Criteria:** All four evaluation paths present for MVP.  
- **Dependencies:** FR-005–FR-008  
- **Architecture refs:** `docs/04-architecture/system-architecture.md`  
- **Design refs:** `docs/06-design/ml-design.md`  
- **Tests:** TEST-007  

---

## Future / Could (not MVP Must)

| ID | Summary |
|---|---|
| FUTURE-001 | NumPy neural net from scratch (no PyTorch) |
| FUTURE-002 | Score / spread predictions |
| FUTURE-003 | Second league adapter |
| FUTURE-004 | Minimal prediction UI |
| FUTURE-005 | Deploy/CD beyond image build — platform TBD at Gate 8 (GCP was a candidate only; no binding ADR) |

No requirement IDs minted for these until pulled into scope via CR.

---

## Open questions remaining

| Item | Status |
|---|---|
| Served model policy | **Resolved** — ADR-003 / ML-007 |
| Inference key | **Resolved** — `game_id` + `(game_id, feature_version)` (ADR-008) |
| Feature formulas / season cut points | **Resolved** — `docs/06-design/ml-design.md` (L5/L10, `min_prior_games=5`, temporal ~70/15/15) |
| Validation invalid-record policy (fail vs skip) | **Resolved** — `docs/06-design/error-handling.md` (skip+count; fail if zero teams/games for a required season) |
| Raw directory layout / retention | **Resolved** — ADR-006; ingest writes `teams.json`, `games_{season}.json`, `manifest.json` under an immutable batch path |
| Numeric ML success threshold | **Resolved** — ML-005 (strictly lower **test** log loss vs domain-informed baseline; no absolute accuracy/AUC Must) |
| Player persist/ingest in MVP | **Resolved** — CR-001 (team-level MVP; player tables reserved) |
| API-Sports free-tier vs DR-001 | Assumption — still needs live confirmation |
| Cloud deploy platform | Future — not binding (ADR-007 Proposed only) |

## Traceability

See `traceability.md`.
