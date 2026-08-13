# Lead engineering re-review 2 — AthletIQ documentation and drift

Status: Complete  
Date: 2026-08-13  
Reviewer role: Lead engineering reviewer (independent read-only pass)  
Baseline: `docs/00-meta/reviews/2026-08-13-lead-sol-docs-review.md` (8 / 10; LEAD-001 open)  
Scope: Claimed LEAD-001…003 closes, requirements/test honesty, Accepted ADR consequences, and DB/API/ML design-contract-implementation drift

## Executive verdict

The current repository closes **LEAD-001**. The canonical Compose invocation is unambiguous in all three copy-paste surfaces:

`docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture`

The root README now gives the required local workflow (`.env.example` → `.env`, `docker compose up -d --build`, canonical pipeline command, `/v1/health`, `/v1/model`). More importantly, the evidence labels no longer overstate what was verified: NFR-001 is **Implementation Partial** with the clean-machine slice explicitly **Partial**, FR-012 is **Passing (static topology)**, TEST-010 contains no bring-up step, and TEST-013 remains controlled synthetic training-repeatability.

LEAD-002 and LEAD-003 are also closed by narrowing documentation to implemented behavior. No checkpoint restoration or home/away/date resolver was added or is needed.

This remains intentionally short of MVP-complete: no clean-machine owner attestation, live two-season DR-001 attestation, real NBA ML-005 attestation, remote CI-green claim, Gate 8/9 completion, or checked PRD acceptance.

**Score: 9 / 10**  
**≥9 / 10: yes**  
**OPEN blockers: none**

## Claimed closes independently verified

| Claim | Current evidence | Verdict |
|---|---|---|
| Canonical Postgres command appears in all copy-paste surfaces | `README.md`; `docs/09-devops/infrastructure.md`; `docker-compose.yml` etl comment | **Held** |
| README documents a usable local path | `.env.example` copy, `docker compose up -d --build`, canonical pipeline command, `/v1/health`, `/v1/model` | **Held** |
| CLI default remains intentionally in-memory | `src/athletiq/pipeline/__main__.py`: `--store` defaults to `memory`; docs explicitly require Postgres for Compose | **Held** |
| NFR-001 is not overstated | `traceability.md`: Implementation **Partial**; Verification `Passing (local) / Partial (clean-machine)`; notes say owner attestation is not recorded | **Held** |
| FR-012 reflects only static evidence | SRS points end-to-end demo to NFR-001; traceability says **Passing (static topology)** | **Held** |
| TEST-010 has no hidden bring-up claim | Test plan and `tests/integration/test_compose.py` cover topology and optional `docker compose config`, not `up`, pipeline, or health | **Held** |
| TEST-013 remains training-repeatability | Test plan and `tests/unit/test_reproducibility.py` use a controlled synthetic fixture and repeat feature/train/select behavior | **Held** |
| No Compose e2e pytest was added | Current TEST-010 remains static; no bring-up → pipeline → API pytest is claimed | **Correct; not required** |
| LEAD-002 narrowed to actual restart limits | ADR-005, system architecture, error-handling, and IMP-009 say state is write-only; train can rediscover `feature_matrix.npz`; features needs in-process store | **Closed** |
| LEAD-003 narrowed to the shipped resolver | ADR-008, system/API architecture, and glossary say MVP resolver is `provider_game_id`; home/away/date is Future | **Closed** |

### LEAD-001 disposition

**Closed.** The two conditions that previously blocked 9/10 are both satisfied:

1. No ambiguous copy-paste Compose pipeline command remains outside historical review artifacts; current operational surfaces include `--store postgres`.
2. Approved SRS/traceability/test-plan content distinguishes static topology, synthetic training-repeatability, and unattested clean-machine execution.

Leaving clean-machine verification **Partial** is valid under NFR-001, which allows owner attestation or scripted smoke. A new Compose end-to-end pytest is not required.

## Gate snapshot

| Gate | Current judgment |
|---|---|
| 0–1 | Charter and PRD **Approved**; PRD MVP acceptance remains unchecked |
| 2 | SRS 1.4.1 and traceability 1.5.1 **Approved**; LEAD-001 evidence drift closed |
| 3 | Architecture **Approved**; ADR-001–006 and 008–010 Accepted; ADR-007 Proposed/non-binding |
| 4 | DB/API/ML/error designs and contracts **Approved** |
| 5 | Implementation plan **Approved** |
| 6 | IMP-001…012 marked Done; code-review and remote-CI DoD boxes remain open |
| 7 | Test strategy/plan **Approved**; local/static/synthetic qualifiers retained; remote CI not claimed |
| 8–9 | Release and operations remain Draft; no completion claim |

IMP Done is not treated as MVP-complete or as a release/operations approval.

## Design / contract / implementation drift

### Database

| Concern | Design / contract / implementation | Verdict |
|---|---|---|
| MVP persistence scope | CR-001, SRS, database design/schema, and load surface agree on teams, games, and `team_game_stats`; player tables are reserved | **Aligned** |
| PostgreSQL and identity | ADR-001/010, schema, migration, and API decimal-string handling agree on PostgreSQL 16 and BIGINT/BIGSERIAL | **Aligned** |
| Migration snapshot | `schema_migrations` exists in both consolidated schema and migration | **Aligned** |
| Feature payload | Database design and schema describe the JSONB envelope used by the feature store | **Aligned** |
| Demo persistence path | Compose database plus shared volumes; canonical command explicitly selects Postgres | **Aligned; prior drift closed** |

### API

| Concern | Design / contract / implementation | Verdict |
|---|---|---|
| Routes and errors | `/v1/health`, `/v1/predict`, `/v1/model` and distinct 400/404/503 codes agree | **Aligned** |
| Authentication | ADR-009, API design, OpenAPI `security: []`, no auth middleware, and localhost Compose bind agree | **Aligned** |
| Prediction lookup | Design, OpenAPI, and routes expose `game_id` plus optional `provider_game_id`; matchup input is Future | **Aligned; LEAD-003 closed** |
| Artifact/feature compatibility | Pinned model and `(game_id, feature_version)` lookup remain the serving contract | **Aligned** |

### ML

| Concern | Design / contract / implementation | Verdict |
|---|---|---|
| Features and splits | Team L5/L10 plus season-to-date; temporal train/validation/test; shared feature version | **Aligned** |
| Selection and serving | Validation log-loss selection, LR tie-break, test-after-selection, pin-only serving | **Aligned** |
| ML-005 | Traceability remains Partial / synthetic; no real NBA holdout claim | **Honest** |
| Reproducibility | TEST-013 proves controlled training-repeatability; clean-machine workflow is documented but unattested and Partial | **Honest; LEAD-001 closed** |

## Accepted ADR consequences

| ADR | Consequences present? | Follow-through | Verdict |
|---|---|---|---|
| ADR-001 PostgreSQL 16 | Yes | Compose, schema, migrations | **Held** |
| ADR-002 API-Sports adapter | Yes | Env secret, adapter boundary, fixture provider; team-level CR-001 scope | **Held** |
| ADR-003 validation selection / test reporting / pin | Yes | Temporal split, validation-only selection, test reporting, pin-only API | **Held**; ML-005 remains honestly Partial |
| ADR-004 shared local artifacts | Yes | Shared Compose artifacts volume and file pin/artifacts | **Held** |
| ADR-005 batch Python orchestrator | Yes | Thin host wrapper, Python stages, documented restart limits | **Held; LEAD-002 closed** |
| ADR-006 immutable raw filesystem | Yes | Raw volume, immutable batch landing, no raw DB schema | **Held** |
| ADR-008 inference feature contract | Yes | Composite feature key, shared preprocessing, `provider_game_id` resolver only | **Held; LEAD-003 closed** |
| ADR-009 no-auth local API | Yes | Localhost bind, no middleware, explicit empty OpenAPI security | **Held** |
| ADR-010 BIGINT keys | Yes | Design, schema/migration, tests, decimal-string API contract | **Held** |

ADR-007 is Proposed and non-binding; it does not create a GCP requirement.

## Remaining non-blocking nits

These are small documentation-maintenance issues and do not reopen LEAD-001:

1. `traceability.md` uses `Passing (static topology)` and `Partial (clean-machine)` but its allowed-values legend does not list those two qualified values.
2. `implementation-plan.md` upstream version references still name SRS 1.4.0, traceability 1.5.0, test strategy 1.0.0, and test plan 1.0.1 instead of the current 1.4.1 / 1.5.1 / 1.0.1 / 1.0.2.
3. The system-architecture deployment diagram visually routes the host script/CLI into the Compose `etl` container, while `scripts/run_pipeline.sh` actually executes host Python against Postgres. Nearby prose and the canonical Compose command make the supported paths clear, so this is diagram precision rather than an operational blocker.

These residuals are minimal and unimportant to the 9/10 bar. They explain why the score is not 10/10.

## Locked-scope checks

- CR-001 remains Accepted; no player ingest is demanded.
- No GCP, public auth, player ML, or automated retraining is required.
- No remote CI-green, real NBA ML-005, or live two-season claim is inferred.
- PRD acceptance remains unchecked.
- IMP-001…012 Done is not treated as MVP-complete.

## Validation

- [x] Only this review artifact was authored
- [x] No Grill-Me invocation
- [x] No primary documentation edits
- [x] Every Accepted ADR checked for consequences
- [x] DB/API/ML design-contract-implementation triples checked
- [x] LEAD-001…003 independently re-verified against current repo evidence
- [x] No new Compose e2e test demanded

**Final score: 9 / 10**  
**≥9 / 10: yes**  
**OPEN blockers: none**
