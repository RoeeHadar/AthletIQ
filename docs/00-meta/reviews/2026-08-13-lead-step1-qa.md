# Lead review — Step 1 documented-test coverage and QA

Status: Complete  
Date: 2026-08-13  
Reviewer role: Lead manager / independent engineering reviewer  
Scope: SRS Must coverage, traceability/test-plan alignment, `test_map.json`, and local execution of TEST-001…014

## Decision

**APPROVE Step 1.**

Every current SRS **Must** has at least one TEST id in the canonical traceability matrix, and the TEST ids agree with the SRS `Tests` fields. `scripts/crews/qa/test_map.json` maps every documented suite TEST-001…014 to an existing pytest module; TEST-014 intentionally reuses `tests/unit/test_api.py` alongside its dedicated artifact/API tests.

There are **42 Must requirements**, not 43: `NFR-005` is explicitly **Should** in `docs/03-requirements/SRS.md` but is included in `run_qa.py`'s `MUST_TO_TESTS`. Thus the runner's “Must requirements mapped: 43” line means **42 Must + one Should**. This is a non-blocking reporting defect because all 42 actual Musts are mapped and NFR-005 also has TEST-002 coverage.

**OPEN blockers for Step 1: none.**

## Independent QA execution

Command rerun from the repository root:

`python scripts/crews/qa/run_qa.py`

Result: exit code **0**, verdict **ACCEPT**.

| Suite | Independent result | Evidence qualifier |
|---|---:|---|
| TEST-001 | 5 passed | local bootstrap/config/secrets |
| TEST-002 | 4 passed, 1 skipped | static contract passed; live migrate skipped without DB URL |
| TEST-003 | 7 passed | fixture provider; no live API |
| TEST-004 | 7 passed | in-memory curated store |
| TEST-005 | 3 passed | in-memory analytics semantics |
| TEST-006 | 5 passed | local feature invariants |
| TEST-007 | 7 passed | synthetic ML lifecycle / ML-005 smoke |
| TEST-008 | 7 passed | TestClient + fixture pin/features |
| TEST-009 | 5 passed | offline pipeline paths |
| TEST-010 | 2 passed | static Compose topology/config only |
| TEST-011 | 5 passed | static GitHub Actions DAG/policy |
| TEST-012 | 2 passed | methodology/API alignment |
| TEST-013 | 1 passed | controlled-fixture training repeatability |
| TEST-014 | 10 passed | dedicated artifact tests plus overlapping TEST-008 API file |

The results match the qualifiers in the Approved test plan and traceability. They do **not** establish Compose bring-up, a clean clone, live-season ingestion, a frozen NBA ML-005 result, or remote GitHub Actions green.

## Coverage and attestation boundary

- `NFR-001`: TEST-001/013 cover configuration and training repeatability; clean-machine Compose remains **Partial** pending owner attestation. No Compose bring-up pytest is required.
- `DR-001`: TEST-003/004 cover season-window and load behavior; two completed **live** NBA seasons remain unattested.
- `ML-005`: TEST-007 proves the comparison machinery and a synthetic gate only; the frozen NBA holdout remains unattested.
- `OPS-001` / `CON-005`: TEST-011 proves local workflow topology and policy; remote GitHub Actions green remains deferred.
- CR-001 remains intact: no player ingest test is required, and reserved player tables are not an MVP load outcome.

## QA tooling boundary

`scripts/crews/qa/` is engineering tooling, not AthletIQ runtime:

- `run_qa.py` imports only Python standard-library modules and launches pytest.
- CrewAI appears only as descriptive YAML/comments for the QA workforce; the runner does not import or execute CrewAI or an LLM.
- `pyproject.toml` contains no `crewai` runtime or development dependency.
- The runner removes `API_SPORTS_KEY` from each pytest subprocess environment.

## Publish-bar blockers

The next publish-bar steps are correctly **blocked on owner-provided environment/access**:

- Compose demo: Docker CLI is present, but the Docker Desktop Linux daemon is unavailable.
- Remote CI: this workspace has no `.git`, so there is no local repository metadata or remote to push.
- Live seasons and real-data ML-005 evidence: no `.env` exists and `API_SPORTS_KEY` is unset.

These are not Step 1 failures. They prevent truthful completion claims for NFR-001 clean-machine execution, DR-001 live seasons, ML-005 frozen NBA holdout, and OPS-001/CON-005 remote CI.

## Non-blocking tooling note

The coverage auditor is a hard-coded dictionary rather than a parser/check against the current SRS and traceability. Its current contents were independently compared and are complete, but future requirement changes could drift without the runner detecting them. Correct the `NFR-005` priority label/count when engineering tooling is next maintained; no new TEST id is needed.

## Validation

- [x] Only this review artifact was authored
- [x] No Grill-Me invocation
- [x] No primary product documentation or application code edits
- [x] CR-001, no-player-ingest, no-GCP/auth, and no-PRD-tick locks preserved
- [x] No remote CI, two-live-season, clean-machine, or NBA ML-005 claim made

