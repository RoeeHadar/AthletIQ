# Lead review — Honesty recording and QA rerun

Status: Complete  
Date: 2026-08-14  
Reviewer role: Lead manager / independent engineering reviewer  
Scope: Local DR-001/ML-005 honesty recording and TEST-001…014 QA rerun after approved NFR-001 and remote CI steps

## Decision

**APPROVE with notes.**

The working requirements documents accurately distinguish owner-reported local live evidence from automated verification. DR-001 and ML-005 are recorded as implemented, while ML-005 Verification remains `Passing (synthetic)` and TEST-007 remains a synthetic CI suite. The live and fixture stacks are not conflated, every PRD MVP acceptance checkbox remains unchecked, and the QA runner explicitly labels attestation evidence as “not pytest.”

The project **may proceed to the separate MVP-ready-for-manual-test full critique** in the same lead-manager role. That critique is required before any PRD acceptance closeout and must include the still-open code-review gate.

## Honesty checks

### Traceability v1.5.4

Pass.

- DR-001 Implementation is `Implemented`; its Notes record an owner-reported local NBA Stats run of 2,640 games across 2023 (1,319) and 2024 (1,321).
- ML-005 Implementation is `Implemented`, but Verification remains `Passing (synthetic)`.
- ML-005 Notes separately record the owner-reported local live result: `ml005=True`, `logistic_regression-v1`, test log loss `0.623`.
- The Notes state that TEST-007 remains synthetic and that neither local live item is a PRD tick.
- The clean-clone fixture pin `xgboost-v1` (48 games) is explicitly distinguished from the working-tree live pin `logistic_regression-v1`.

### SRS v1.4.3

Pass.

ML-005's Tests field says TEST-007 is the CI synthetic quality-gate suite and separately records the owner-reported local live holdout. It does not relabel TEST-007 as live verification or claim PRD completion.

### PRD and implementation plan

Pass with an open downstream gate.

- All PRD MVP acceptance checkboxes remain `[ ]`.
- IMP-011 records remote CI success on GitHub Actions run `31753742525` at `4a2f713`.
- IMP-011 `Code review passed` remains unchecked. This is honest and prevents the CI tick from being mistaken for completed review.

### QA attestation labels

Pass.

`scripts/crews/qa/run_qa.py` labels NFR-001, DR-001, ML-005, OPS-001, and CON-005 as attestation evidence not closed by pytest. It preserves fixture-only CI and does not claim that QA establishes the live or remote facts.

## Independent evidence

The live-run transcript corroborates:

- command exit code `0`;
- 2,640 games loaded and 2,640 feature rows produced;
- selected model `logistic_regression`;
- test log loss `0.6231052772493764`;
- `ml005=True`;
- published pin `logistic_regression-v1`.

The 2023/2024 split is correctly presented in living docs as **owner-reported** rather than as a pytest result. The live working-tree stack was no longer running during this review, so that per-season split was not independently re-queried.

The currently reachable `/v1/model` returned `xgboost-v1`, consistent with the separate 48-game clean-clone fixture stack. This does not contradict the earlier working-tree live pin.

## Independent QA rerun

Command rerun from the repository root:

`python scripts/crews/qa/run_qa.py`

Result: exit code **0**, verdict **ACCEPT**.

| Suite | Result |
|---|---:|
| TEST-001 | 5 passed |
| TEST-002 | 4 passed, 1 skipped |
| TEST-003 | 9 passed |
| TEST-004 | 7 passed |
| TEST-005 | 3 passed |
| TEST-006 | 5 passed |
| TEST-007 | 7 passed |
| TEST-008 | 7 passed, 1 warning |
| TEST-009 | 6 passed |
| TEST-010 | 2 passed |
| TEST-011 | 5 passed |
| TEST-012 | 2 passed, 1 warning |
| TEST-013 | 1 passed |
| TEST-014 | 10 passed, 1 warning |

Coverage reports no holes. The printed count of 43 remains the known non-blocking labeling defect: it is 42 Must requirements plus NFR-005, which is Should. This does not hide an uncovered Must.

## Required follow-up for the full critique

1. Perform and record the still-open code review before any final MVP/PRD acceptance decision.
2. Assess the live logistic-regression `ConvergenceWarning` (`lbfgs` reached `max_iter=500`) as part of ML credibility review. The reported metric is real output, but solver non-convergence must be either accepted and disclosed as a limitation or resolved through a newly frozen, test-isolated configuration. Do not tune against the already-observed test result.

Neither item blocks proceeding to the full critique; both block treating this approval as final MVP acceptance.

## Scope and lock validation

- [x] Only this review artifact authored
- [x] No primary product document or application-code edits
- [x] No Grill-Me invocation
- [x] PRD acceptance remains unchecked
- [x] TEST-007 remains synthetic
- [x] No player ingest, GCP, application auth, or Compose end-to-end pytest requested
- [x] CR-001 not reopened
- [x] Fixture-only CI preserved
