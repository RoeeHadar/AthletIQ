# Requirements traceability

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.7.0

## Direction

```text
Forward:  Requirement → Architecture → Design → Implementation → Test
Reverse:  Implementation → Design → Architecture → Requirement
```

## Status columns (independent evidence)

Do **not** set Implementation from a passing test, or Verification from an IMP Done checkbox.

| Column | Source of truth | Allowed values |
|---|---|---|
| Requirement | SRS / CR | `Active` · `Amended (CR-00X)` |
| Implementation | IMP task Status + code (not pytest) | `Implemented` · `Partial` · `Not started` |
| Verification | TEST plan Status; OPS-001/CON-005 remote is GitHub Actions | `Passing (local)` · `Passing (synthetic)` · `Passing (in-memory)` · `Passing (remote)` · `Deferred (remote CI)` · `Planned` |

IMP-001…012 **Done** is Gate 6 code complete for listed MVP modules. IMP-013–018 (CR-004) are **Done**: CI `491c5c0` ([31913410157](https://github.com/RoeeHadar/AthletIQ/actions/runs/31913410157)); code review APPROVE 2026-08-16 (`docs/00-meta/reviews/2026-08-16-cr004-code-review.md`). IMP-019–025 (CR-005) are **Done**: CI `657e5a1` ([31956566628](https://github.com/RoeeHadar/AthletIQ/actions/runs/31956566628)); code review APPROVE 2026-08-16 (`docs/00-meta/reviews/2026-08-16-cr005-lead-dev-code-review.md`). Live NBA/WNBA pin **publish** is operator (IMP-024 protocol + CI 48-game pin unchurned on `657e5a1`).

**Partial** means the mapped IMP exists but the requirement’s product bar is not attested. DR-001 / ML-005 local live bars were owner-reported **2026-08-14** (not PRD-ticked; TEST-007 remains synthetic). CR-005 amends live NBA depth and retrains; old live test log loss **0.623 does not bind** the new pin (ML-012).

CR-001 (Accepted): MVP persist/ingest was teams/games/team statistics. **CR-004** loads players, WNBA fixtures, synthetic odds, per-league pins. **CR-005** (Accepted): e-coin ledger, `/slate`, `/board`, uncapped live NBA, live player boxes, retrain — labeled simulation, not a real-money book.

## Matrix

| Requirement | Architecture | Design | Implementation | Test | Requirement | Implementation | Verification |
|---|---|---|---|---|---|---|---|
| FR-001 | system/data | error + ADR-006 | IMP-003, IMP-020 | TEST-003, TEST-020, TEST-025 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| FR-002 | data | database | IMP-002, IMP-004, IMP-019 | TEST-002, TEST-004 | Amended (CR-005) | Implemented | Passing (local) / Passing (in-memory); Passing (remote) |
| FR-003 | data | database | IMP-005 | TEST-005 | Amended (CR-001) | Implemented | Passing (in-memory) |
| FR-004 | system/data | ml | IMP-006 | TEST-006 | Amended (CR-001) | Implemented | Passing (local) |
| FR-005 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| FR-006 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| FR-007 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| FR-008 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| FR-009 | api | api + error | IMP-008 | TEST-008 | Active | Implemented | Passing (local) |
| FR-010 | system | ml + api + model-card | IMP-012 | TEST-012 | Active | Implemented | Passing (local) |
| FR-011 | system | error | IMP-009 | TEST-009 | Active | Implemented | Passing (local) |
| FR-012 | system | infrastructure | IMP-010 | TEST-010 | Active | Implemented | Passing (static topology) |
| FR-013 | data | error | IMP-004 | TEST-004 | Active | Implemented | Passing (in-memory) |
| FR-014 | api | api | IMP-008 | TEST-008, TEST-014 | Active | Implemented | Passing (local) |
| FR-015 | api | PRODUCT.md + gamecast Comp A | IMP-018, IMP-023 | TEST-008, TEST-019, TEST-028 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| FR-016 | data | database | IMP-014, IMP-021 | TEST-015, TEST-026 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| FR-017 | data | database | IMP-014, IMP-020 | TEST-016, TEST-025 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| FR-018 | api/data | api + ADR-012 | IMP-014, IMP-017 | TEST-017 | Active | Implemented | Passing (local) |
| FR-019 | api | api + ADR-013 | IMP-016, IMP-017 | TEST-018 | Active | Implemented | Passing (local) |
| FR-020 | api | api-design | IMP-017 | TEST-008 | Active | Implemented | Passing (local) |
| FR-021 | data | database + ADR-015 | IMP-019, IMP-020, IMP-021 | TEST-020, TEST-025 | Active | Implemented | Passing (local); Passing (remote) |
| FR-022 | data/api | database + ADR-014 | IMP-019, IMP-023 | TEST-022, TEST-023 | Active | Implemented | Passing (local); Passing (remote) |
| FR-023 | system/data | database + api + ADR-015 | IMP-019, IMP-022, IMP-023 | TEST-021, TEST-022 | Active | Implemented | Passing (local); Passing (remote) |
| FR-024 | api | api + ADR-016 | IMP-023 | TEST-023, TEST-028 | Active | Implemented | Passing (local); Passing (remote) |
| FR-025 | api | api + ADR-016 | IMP-023 | TEST-024, TEST-028 | Active | Implemented | Passing (local); Passing (remote) |
| FR-026 | system | infrastructure + ADR-015 | IMP-022 | TEST-024, TEST-025 | Active | Implemented | Passing (local); Passing (remote) |
| FR-027 | data | database + ADR-017 | IMP-020 | TEST-025, TEST-016 | Active | Implemented | Passing (local); Passing (remote) |
| FR-028 | system | ml + model-card | IMP-024 | TEST-007, TEST-027 | Active | Implemented | Passing (local); Passing (remote) |
| DR-001 | data | ml | IMP-003, IMP-004, IMP-014, IMP-020, IMP-021 | TEST-003, TEST-004, TEST-015, TEST-025, TEST-026 | Amended (CR-005) | Partial | Passing (local); Passing (remote) |
| DR-002 | data | database | IMP-002, IMP-004, IMP-013, IMP-019 | TEST-002, TEST-004, TEST-015, TEST-022 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| DR-003 | data | database | IMP-004, IMP-014, IMP-022 | TEST-004, TEST-016, TEST-017, TEST-021 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| DR-004 | data | database | IMP-013, IMP-014 | TEST-017 | Active | Implemented | Passing (local) |
| DR-005 | data | database + ADR-014 | IMP-019 | TEST-002, TEST-021, TEST-022 | Active | Implemented | Passing (local); Passing (remote) |
| DR-006 | data | database + ADR-015 | IMP-019, IMP-020 | TEST-020, TEST-021, TEST-024 | Active | Implemented | Passing (local); Passing (remote) |
| ML-001 | system | ml | IMP-006 | TEST-006 | Active | Implemented | Passing (local) |
| ML-002 | system | ml | IMP-006, IMP-007 | TEST-006, TEST-007 | Active | Implemented | Passing (local) / Passing (synthetic) |
| ML-003 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| ML-004 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| ML-005 | system | ml | IMP-007, IMP-024 | TEST-007 (quality gate), TEST-027 | Amended (CR-005) | Partial | Passing (synthetic); Passing (remote) |
| ML-006 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| ML-007 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| ML-008 | system | ml | IMP-006 | TEST-006 | Active | Implemented | Passing (local) |
| ML-010 | system | ml + ADR-013 | IMP-016 | TEST-007, TEST-018 | Active | Implemented | Passing (local) |
| ML-011 | system/data | ml | IMP-015 | TEST-006, TEST-016 | Active | Implemented | Passing (local) |
| ML-012 | system | ml + model-card | IMP-024 | TEST-027 | Active | Implemented | Passing (local); Passing (remote) |
| SEC-001 | system | error | IMP-001, IMP-003 | TEST-001, TEST-003 | Active | Implemented | Passing (local) |
| SEC-002 | system | — | IMP-001, IMP-011 | TEST-001, TEST-011 | Active | Implemented | Passing (local) |
| NFR-001 | system | ml | IMP-001, IMP-007 | TEST-001, TEST-013 | Active | Implemented | Passing (local) |
| NFR-002 | api | api | IMP-008 | TEST-008 | Active | Implemented | Passing (local) |
| NFR-003 | system | ci-cd | IMP-011, IMP-025 | TEST-011, TEST-025 | Active | Implemented | Passing (local); Passing (remote) |
| NFR-004 | api | api | IMP-008 | TEST-008 | Active | Implemented | Passing (local) |
| NFR-005 | data | database | IMP-002, IMP-019 | TEST-002, TEST-022 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| OPS-001 | system | ci-cd | IMP-011 | TEST-011 | Active | Implemented | Passing (local); Passing (remote) |
| OPS-002 | system | error + logging | IMP-001, IMP-009 | TEST-001, TEST-009 | Active | Implemented | Passing (local) |
| CON-001 | system | — | IMP-001, IMP-009 | TEST-001, TEST-009 | Active | Implemented | Passing (local) |
| CON-002 | data | database | IMP-002 | TEST-002 | Active | Implemented | Passing (local) |
| CON-003 | system | infrastructure | IMP-010 | TEST-010 | Active | Implemented | Passing (local) |
| CON-004 | api | api | IMP-008 | TEST-008 | Active | Implemented | Passing (local) |
| CON-005 | system | ci-cd | IMP-011 | TEST-011 | Active | Implemented | Passing (local); Passing (remote) |
| CON-006 | system | — | IMP-009 | TEST-009 | Active | Implemented | Passing (local) |
| CON-007 | data | — | IMP-003 | TEST-003 | Active | Implemented | Passing (local) |
| CON-008 | system | ml | IMP-007 | TEST-007 | Active | Implemented | Passing (synthetic) |
| ADR-008 | system/api/data | ADR-008 + api/ml | IMP-006, IMP-008 | TEST-006, TEST-008, TEST-014 | Accepted | Implemented | Passing (local) |
| ADR-009 | api | ADR-009 + api | IMP-008 | TEST-008 | Accepted | Implemented | Passing (local) |
| CON-009 | api | api + ADR-012 + ADR-014 | IMP-017, IMP-018, IMP-023 | TEST-017, TEST-019, TEST-021, TEST-024, TEST-028 | Amended (CR-005) | Implemented | Passing (local); Passing (remote) |
| ADR-012 | data/api | ADR-012 | IMP-013, IMP-014, IMP-017 | TEST-017 | Accepted | Implemented | Passing (local) |
| ADR-013 | system/api | ADR-013 | IMP-016, IMP-017 | TEST-018 | Accepted | Implemented | Passing (local) |
| ADR-014 | data/api | ADR-014 | IMP-019, IMP-023 | TEST-021, TEST-022 | Accepted | Implemented | Passing (local); Passing (remote) |
| ADR-015 | system/data | ADR-015 | IMP-019, IMP-020, IMP-022 | TEST-020, TEST-021, TEST-024 | Accepted | Implemented | Passing (local); Passing (remote) |
| ADR-016 | api | ADR-016 | IMP-023 | TEST-023, TEST-024, TEST-028 | Accepted | Implemented | Passing (local); Passing (remote) |
| ADR-017 | data | ADR-017 | IMP-020, IMP-024 | TEST-025, TEST-027 | Accepted | Implemented | Passing (local); Passing (remote) |

## Code annotation rule

A file or module gets an inline reverse pointer if and only if it appears under **Files/modules affected** for an `IMP-XXX` task in `docs/07-implementation/implementation-plan.md`:

```python
# Implements: FR-XXX
```

Test files use TEST ids in `docs/08-testing/test-plan.md`. They must **not** carry `# Implements`.

## Notes

- Gate 7 test strategy/plan **Approved** (v1.2.0). CR-005 Gate 6 IMP-019–025 **Done** (`657e5a1` / [31956566628](https://github.com/RoeeHadar/AthletIQ/actions/runs/31956566628)).  
- TEST-013 = training-repeatability on a controlled synthetic fixture — **not** clean-clone Compose.  
- ML-005 verification **TEST-007** remains **synthetic**. Owner-reported **local live** holdout **2026-08-14** (working-tree Compose, not the NFR-001 clean clone): `ml005=True`, pin `logistic_regression-v1`, test log loss **0.623**. Not a PRD tick. **Does not bind** the CR-005 retrained pin (ML-012 / TEST-027). Fixture clean-clone pin is `xgboost-v1` (48 games) — different dataset; CR-005 does not replace that CI pin. Live NBA/WNBA pin **publish** is operator — not SHA `657e5a1`.  
- NFR-001 Implementation **Implemented**; Verification **Passing (local)**. Clean-clone attestation **2026-08-14**: `git clone` of `https://github.com/RoeeHadar/AthletIQ` `main` at `4a2f713ed4cf58966358c6dd12b3ea77813d905a` into a directory outside the developer working tree; `cp .env.example .env`; `docker compose up -d --build`; `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture` (48 games, pin `xgboost-v1`); `GET /v1/health` `{"status":"ok"}`; `GET /v1/model` `xgboost-v1`. TEST-001/013 still do not close the clean-machine AC by themselves. No Compose e2e pytest added. **Not** re-attested on `657e5a1`.  
- FR-012 Verification = TEST-010 **Passing (static topology)** only. E2E demo is NFR-001.  
- CON-003 remains Passing (local): Compose file defines the three services.  
- DR-001 Implementation **Partial**: code has uncapped live NBA paging + WNBA 2021–2025/2026 scheduled fixtures; **live uncapped ingest is not attested** on `657e5a1`. TEST-003/004 remain fixture/in-memory except when `TEST_DATABASE_URL` integration is recorded. Owner-reported **local live** ingest **2026-08-14** (`--provider nba-stats --seasons 2023 2024`, **2640** games) is a CR-004-era two-season run — **not** CR-005 DR-001 done and not a PRD tick.  
- FR-028 / ML-012 Implementation **Implemented** for protocol, disclosure, and CI pin identity (TEST-027). Live NBA+WNBA pin publish remains operator.  
- OPS-001 / CON-005 remote verification: GitHub Actions run [31956566628](https://github.com/RoeeHadar/AthletIQ/actions/runs/31956566628) succeeded for a push to main at head SHA `657e5a1` (lint, unit, integration, image). Prior CR-004 attest: [31913410157](https://github.com/RoeeHadar/AthletIQ/actions/runs/31913410157) on `491c5c0`. TEST-011 remains Passing (local) for static DAG/policy verification; NFR-003 remains fixture/offline-only.  
- Postgres load path exists (`--store postgres`); TEST-004 status remains in-memory unless `TEST_DATABASE_URL` integration is recorded as Passing.
