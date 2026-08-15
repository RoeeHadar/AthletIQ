# Test strategy

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

> How we verify AthletIQ. Tests are requirement-driven (`test-plan.md`), not invented solely because code exists.  
> **Gate 7 test strategy Approved.** Prefer Test Plan Approved before first Gate 6 slice (`gates.md` §22).

## Upstream

| Artifact | Status |
|---|---|
| SRS v1.4.1, traceability 1.5.1 | Approved (CR-001) |
| Architecture + binding ADRs (incl. ADR-010) | Accepted / Approved docs |
| Design + contracts | Approved |
| Implementation plan v1.0.x | Approved |

## Levels

Canonical names only (see `glossary.md`). **One primary `Level` per TEST suite.** A suite may *also* contain nested cases at another level — list those under **Also** in the plan; do not invent compound labels like `unit + integration`.

| Level | Intent | Typical runners |
|---|---|---|
| **unit** | Pure functions / in-process helpers (retry policy, split math, baselines, redaction) | `pytest` |
| **integration** | Cross-component: Postgres, filesystem ingest, API ↔ DB ↔ pin, Compose topology | `pytest` + ephemeral DB / Compose |
| **pipeline** | Operator script/CLI end-to-end with fixtures | Local / optional CI job |
| **ci** | GHA path + static asserts on workflow YAML (NFR-003, OPS-001) | GitHub Actions + meta-tests |

## Three verification kinds (do not conflate)

| Kind | What it proves | Example |
|---|---|---|
| **Automated correctness** | Software invariants; must be green in default CI | Leakage guard, validation-only selection, error codes |
| **Quality gate / attestation** | Empirical ML outcome on a **frozen** dataset/config; required for MVP *complete*, not a flaky PR unit assert | **ML-005** beats domain-informed baseline on test log loss |
| **CI topology** | Pipeline/workflow structure and policy | No live provider; job `needs` DAG |

**ML-005** is a **release-quality gate / attestation**, not a deterministic unit-test invariant. CI may smoke the *comparison machinery*; MVP-complete requires the attested eval report on the agreed fixture (or local full run).

**Freeze rule (test isolation):** Before ML-005 attestation runs, baseline definition, `dataset_version`, split boundaries, `feature_version`, and primary metric (log loss) are **frozen**. Changing any of these after peeking at test metrics voids the attestation (architecture: test set never used to redefine baselines/features/selection).

## Principles

1. **Requirement-driven** — every Must SRS id maps to ≥1 TEST via `traceability.md` (**canonical**).  
2. **No live API-Sports in CI** (NFR-003) — recorded fixtures only.  
3. **NFR-004 falsifiable** — docs/OpenAPI cite “no hard SLO” (TEST-008); no load suite.  
4. **Training-repeatability is verified, not merely configured** — **TEST-013** runs identical inputs twice (features/splits/selection/metrics). That is **not** the NFR-001 clean-machine / Compose demo (documented in root README; attested 2026-08-14 on a clean clone of `4a2f713`). TEST-001 only proves seed/path knobs exist.  
5. **Train/serve consistency (ML-008)** — API preprocessing **conforms to the same `feature_version` / feature contract** as training. Do **not** require “same Python import” unless design later mandates a shared module (current design prefers shared module, but the *requirement* is contract equivalence).  
6. **Artifact/API consistency** — published metadata, on-disk artifact, and API-loaded model agree (**TEST-014**); pin/`feature_version` mismatch fails clearly.  
7. **Secrets** — falsifiable redaction (sentinel value), not “by convention.”  
8. **Contract/docs static checks** — where practical, `ci` validates machine-readable contracts (OpenAPI ↔ design claims, workflow credentials, ID registry presence). Not a separate doc-test framework.  
9. **Annotation** — tests do not replace `# Implements:` on IMP-listed modules.

## Tooling stance

| Choice | Stance |
|---|---|
| Runner | `pytest` (+ FastAPI `TestClient`) |
| Lint | ruff (or chosen) in CI |
| DB | ephemeral Postgres |
| Fixtures | `tests/fixtures/` |
| Load/perf | **Out of MVP** (NFR-004) |

## Mapping to IMP tasks

| IMP | Primary TEST |
|---|---|
| IMP-001…012 | TEST-001…012 |
| IMP-001 + IMP-007 (repro) | **TEST-013** |
| IMP-007 + IMP-008 (pin↔serve) | **TEST-014** |

## ID minting

- **TEST-001…012:** Gate 5 planning-hook exception (documented); `testing` owns content.  
- **TEST-013…:** minted by `testing` skill (this revision).

## Deliberate non-coverage (MVP)

| Item | Why |
|---|---|
| Load / soak / SLA tests | NFR-004 |
| Live provider in CI | NFR-003 |
| Auth / multi-tenant beyond ADR-009 | ADR-009 / NFR-002 |
| Post-MVP models, UI, GCP | Out of scope |
| ML-005 as mandatory flaky PR unit fail | Quality gate / attestation instead |

## Boundary: TEST-010 vs TEST-011

| Suite | Owns |
|---|---|
| **TEST-010** | `docker-compose.yml` — app **deployment topology** (services, volumes; static file / `compose config` — not bring-up or `/v1/health`) |
| **TEST-011** | `.github/workflows/*.yml` — **CI pipeline topology** (jobs, `needs` DAG, no live provider, secrets, image build) |

## Related

- Cases: `test-plan.md`  
- Traceability: `../03-requirements/traceability.md`  
- CI wiring: IMP-011 + devops docs
