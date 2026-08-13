# ID registry

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 0.4.2

Append-only. Register an ID here **before** using it in any document. Do not reuse IDs.

| ID | Type | Title / summary | First used in | Date |
|---|---|---|---|---|
| FR-001 | FR | Ingest NBA data via provider adapter | SRS.md | 2026-08-12 |
| FR-002 | FR | Persist core NBA entities and statistics | SRS.md | 2026-08-12 |
| FR-003 | FR | SQL analytics (aggregations + window functions) | SRS.md | 2026-08-12 |
| FR-004 | FR | Feature engineering under temporal boundary | SRS.md | 2026-08-12 |
| FR-005 | FR | Evaluate naive baseline on holdout | SRS.md | 2026-08-12 |
| FR-006 | FR | Evaluate domain-informed baseline on holdout | SRS.md | 2026-08-12 |
| FR-007 | FR | Train/evaluate logistic regression on same holdout | SRS.md | 2026-08-12 |
| FR-008 | FR | Train/evaluate XGBoost on same holdout | SRS.md | 2026-08-12 |
| FR-009 | FR | HTTP prediction API (binary + P(home wins)) | SRS.md | 2026-08-12 |
| FR-010 | FR | Document methodology and limitations with predictions | SRS.md | 2026-08-12 |
| FR-011 | FR | Pipeline orchestration script | SRS.md | 2026-08-12 |
| FR-012 | FR | Containerized local multi-service deployment | SRS.md | 2026-08-12 |
| FR-013 | FR | ETL validation report | SRS.md | 2026-08-12 |
| DR-001 | DR | MVP season depth (2 Must / 3 Should) | SRS.md | 2026-08-12 |
| DR-002 | DR | Required entity themes | SRS.md | 2026-08-12 |
| ML-001 | ML | Temporal boundary (no leakage) | SRS.md | 2026-08-12 |
| ML-002 | ML | Designated team = home | SRS.md | 2026-08-12 |
| ML-003 | ML | Temporal train / validation / test (~70/15/15) | SRS.md | 2026-08-12 |
| ML-004 | ML | Primary metric = log loss; accuracy secondary | SRS.md | 2026-08-12 |
| ML-005 | ML | At least one ML model beats domain-informed baseline | SRS.md | 2026-08-12 |
| ML-006 | ML | Baseline definitions (naive + domain-informed) | SRS.md | 2026-08-12 |
| SEC-001 | SEC | Secrets via environment only | SRS.md | 2026-08-12 |
| SEC-002 | SEC | No secrets in version control | SRS.md | 2026-08-12 |
| NFR-001 | NFR | Reproducibility without source edits | SRS.md | 2026-08-12 |
| NFR-002 | NFR | Demo-grade local/API; no external SLA | SRS.md | 2026-08-12 |
| OPS-001 | OPS | CI: lint → unit → integration → image build | SRS.md | 2026-08-12 |
| OPS-002 | OPS | Structured pipeline logging and failure reporting | SRS.md | 2026-08-12 |
| CON-001 | CON | Python-based ETL | SRS.md | 2026-08-12 |
| CON-002 | CON | Relational SQL system of record | SRS.md | 2026-08-12 |
| CON-003 | CON | Docker Compose local topology (MVP default) | SRS.md | 2026-08-12 |
| CON-004 | CON | FastAPI prediction HTTP API (MVP default) | SRS.md | 2026-08-12 |
| CON-005 | CON | GitHub Actions CI | SRS.md | 2026-08-12 |
| CON-006 | CON | Linux pipeline orchestration script | SRS.md | 2026-08-12 |
| CON-007 | CON | External NBA provider via adapter; API-Sports preferred | SRS.md | 2026-08-12 |
| CON-008 | CON | MVP model families: baseline + LR + XGBoost | SRS.md | 2026-08-12 |
| ADR-001 | ADR | PostgreSQL as system of record | ADR-001-postgresql.md | 2026-08-12 |
| ADR-002 | ADR | API-Sports NBA as MVP provider | ADR-002-api-sports-provider.md | 2026-08-12 |
| ADR-003 | ADR | Served model selection policy | ADR-003-served-model-selection.md | 2026-08-12 |
| ADR-004 | ADR | Artifact storage MVP local / GCP later | ADR-004-artifact-storage.md | 2026-08-12 |
| ADR-005 | ADR | Training as pipeline batch | ADR-005-training-as-batch.md | 2026-08-12 |
| ADR-006 | ADR | Raw landing before curated | ADR-006-raw-landing.md | 2026-08-12 |
| ADR-007 | ADR | Post-MVP GCP candidate (Proposed) | ADR-007-post-mvp-gcp.md | 2026-08-12 |
| FR-014 | FR | Prediction lineage (model + feature version) | SRS.md | 2026-08-12 |
| DR-003 | DR | Idempotent curated loads | SRS.md | 2026-08-12 |
| ML-007 | ML | Model selection uses validation only | SRS.md | 2026-08-12 |
| ADR-008 | ADR | Inference feature contract game_id | ADR-008-inference-feature-contract.md | 2026-08-12 |
| ADR-009 | ADR | No auth on MVP demo API | ADR-009-no-auth-mvp-api.md | 2026-08-12 |
| NFR-004 | NFR | No hard latency/availability SLOs in MVP | SRS.md | 2026-08-12 |
| NFR-005 | NFR | Local query access paths indexed | SRS.md | 2026-08-12 |
| ML-009 | ML | Published model lineage metadata | SRS.md | 2026-08-12 |
| ML-008 | ML | Training–serving feature consistency | SRS.md | 2026-08-12 |
| NFR-003 | NFR | CI independent of live provider | SRS.md | 2026-08-12 |
| IMP-001 | IMP | Project bootstrap, config, logging, secrets | implementation-plan.md | 2026-08-12 |
| IMP-002 | IMP | Database schema and migrations | implementation-plan.md | 2026-08-12 |
| IMP-003 | IMP | Provider adapter and raw ingest | implementation-plan.md | 2026-08-12 |
| IMP-004 | IMP | Validate, transform/load, validation report | implementation-plan.md | 2026-08-12 |
| IMP-005 | IMP | SQL analytics | implementation-plan.md | 2026-08-12 |
| IMP-006 | IMP | Feature engineering (shared train/serve) | implementation-plan.md | 2026-08-12 |
| IMP-007 | IMP | ML train, baselines, select, test-once, publish | implementation-plan.md | 2026-08-12 |
| IMP-008 | IMP | FastAPI prediction service | implementation-plan.md | 2026-08-12 |
| IMP-009 | IMP | Pipeline orchestration | implementation-plan.md | 2026-08-12 |
| IMP-010 | IMP | Docker Compose local deployment | implementation-plan.md | 2026-08-12 |
| IMP-011 | IMP | GitHub Actions CI | implementation-plan.md | 2026-08-12 |
| IMP-012 | IMP | Methodology and limitations disclosure | implementation-plan.md | 2026-08-12 |
| TEST-001 | TEST | Bootstrap/config/secrets unit suite | implementation-plan.md | 2026-08-12 |
| TEST-002 | TEST | Schema/migration integration suite | implementation-plan.md | 2026-08-12 |
| TEST-003 | TEST | Provider adapter/ingest suite (fixtures) | implementation-plan.md | 2026-08-12 |
| TEST-004 | TEST | Validate/load/report integration suite | implementation-plan.md | 2026-08-12 |
| TEST-005 | TEST | SQL analytics suite | implementation-plan.md | 2026-08-12 |
| TEST-006 | TEST | Feature leakage/consistency unit suite | implementation-plan.md | 2026-08-12 |
| TEST-007 | TEST | ML split/select/eval suite | implementation-plan.md | 2026-08-12 |
| TEST-008 | TEST | API contract integration suite | implementation-plan.md | 2026-08-12 |
| TEST-009 | TEST | Pipeline orchestration suite | implementation-plan.md | 2026-08-12 |
| TEST-010 | TEST | Compose static topology (not smoke/bring-up) | implementation-plan.md | 2026-08-12 |
| TEST-011 | TEST | CI path verification suite | implementation-plan.md | 2026-08-12 |
| TEST-012 | TEST | Methodology/model disclosure suite | implementation-plan.md | 2026-08-12 |
| TEST-013 | TEST | Training-repeatability (not clean-clone Compose) | test-plan.md | 2026-08-13 |
| TEST-014 | TEST | Published artifact ↔ API compatibility | test-plan.md | 2026-08-13 |

| ADR-010 | ADR | BIGINT / BIGSERIAL surrogate keys | ADR-010-bigint-surrogate-keys.md | 2026-08-13 |
| CR-001 | CR | MVP persist/ingest team-level entities; player tables reserved | CR-001-mvp-team-stats-not-players.md | 2026-08-13 |

## Prefixes

| Prefix | Meaning |
|---|---|
| FR- | Functional requirement |
| NFR- | Non-functional requirement |
| DR- | Data requirement |
| SEC- | Security requirement |
| ML- | Machine learning requirement |
| OPS- | Operational requirement |
| CON- | Constraint |
| ARCH- | Architecture element (optional cross-ref) |
| ADR- | Architecture decision record (`ADR-001`, …) |
| DESIGN- | Design element (optional) |
| TEST- | Test case / suite id |
| IMP- | Implementation plan task |
| CR- | Change request |
