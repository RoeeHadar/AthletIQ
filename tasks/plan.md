# Implementation Plan: Publish-bar closeout (post-blocker)

## Overview

Blockers that paused publish-bar after Step 1 are cleared: remote CI green on `4a2f713`, NFR-001 clean-clone attested, local live NBA ingest + ML-005 reported. Remaining work is honesty recording, QA re-run, lead-manager step gate, then **MVP-ready-for-manual-test** critique. No new product features. Do not tick PRD until owner/lead-manager closeout. Do not add Compose e2e pytest.

## Architecture Decisions

- Unchanged. CR-001 Accepted (no player ingest). CR-002 / ADR-011 live path `--provider nba-stats`. CI fixture-only (NFR-003). Canonical Compose: `--store postgres --provider fixture`.

## Task List

### Phase 1: Honesty (not PRD ticks)

- [ ] Task 1: Record owner-reported local DR-001 / ML-005 in traceability (+ SRS ML-005 test note). Leave PRD checkboxes unchecked.
- [ ] Task 2: Align QA crew attestation printout with attested NFR-001 / remote CI; live DR-001/ML-005 still “not pytest.”

### Checkpoint: Honesty

- [ ] Traceability does not say live seasons “are not attested.”
- [ ] TEST-007 remains synthetic.
- [ ] PRD MVP acceptance all `[ ]`.

### Phase 2: QA

- [ ] Task 3: QA crew `python scripts/crews/qa/run_qa.py` (TEST-001…014). Coverage: every SRS Must still has a TEST id.

### Checkpoint: QA + lead engineer

- [ ] Verdict ACCEPT
- [ ] Lead engineer approves this step

### Phase 3: Lead manager + MVP critique

- [ ] Task 4: Lead manager (GPT 5.6 Sol) reviews Task 1–3 vs Approved docs + QA results.
- [ ] Task 5: If Task 4 APPROVE — full MVP scope + docs to lead manager for test/critique; fix until approved. Stop if owner input, contradiction, or unknown next.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Confusing fixture pin `xgboost-v1` with live pin `logistic_regression-v1` | High | Keep stacks distinct in notes |
| Ticking PRD early | High | Lead-manager closeout only |
| Ports 5432/8000 held by attest clone | Med | Do not restart this workspace Compose without owner |

## Open Questions

- None that block this plan. PRD ticks wait for lead-manager MVP closeout.
