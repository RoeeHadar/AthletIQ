# Lead review — MVP critique notes closeout (follow-up)

Status: Complete  
Date: 2026-08-14  
Reviewer role: Lead manager / independent engineering reviewer  
Model: Cursor Grok Extra High (`cursor-grok-4.6-xhigh`), owner-authorized substitute for GPT 5.6 Sol (API limit)  
Scope: Verify closeout of notes from `docs/00-meta/reviews/2026-08-14-lead-mvp-critique.md` (**APPROVE with notes**). Independent read of model card, `LIMITATIONS_TEXT`, `train.py` `max_iter`, IMP DoD boxes, PRD checkboxes.  
Baseline (not reopened): first MVP critique; docs 9/10; Step 1 QA; GHA `4a2f713`; NFR-001 attest; honesty+QA

## Decision

**APPROVE.**

Note 1 / CRIT-001 (live LR `ConvergenceWarning` disclosure) is **closed**. No remaining **blocking** edits. This follow-up does not tick PRD, does not reopen CR-001, does not retune LR, and does not add Compose e2e pytest.

Owner manual test may still proceed (already allowed by critique 1).

## Criterion 12

**Unblocked.** The owner **may** tick PRD criterion 12 (`Predictions are accompanied by documented methodology and known limitations`). This review does **not** tick it.

Criteria **1–11 and 13–17** remain as previously recommended in critique 1 (see closeout table below). Criterion 1 is still **Yes after notes 2** (README honesty still uncommitted). That is a carry-forward documentation commit, **not** a product defect and **not** a hold on criterion 12.

## Independent verification (do not trust the engineer’s list)

### Note 1 / CRIT-001 — **Closed** (required for criterion 12)

| Check | Claim | Independent result |
|---|---|---|
| Model card v1.0.1 Known limitations **item 7** | Required live-LR wording | **Exact match** to critique 1 required text (`logistic_regression-v1`, sklearn `LogisticRegression(solver="lbfgs", max_iter=500)`, unscaled L5/L10, `ConvergenceWarning`, test log loss 0.623 is that fit not full convergence, config not changed after inspecting test metrics) |
| Item **8** | Optional CRIT-004 0/1 log-loss grain | **Present** (optional; not required to unblock 12) |
| `api/app/methodology.py` `LIMITATIONS_TEXT` | Mentions live LR `ConvergenceWarning` | **Present.** Short clause: live pin `logistic_regression-v1`, lbfgs `max_iter=500`, `ConvergenceWarning`, reported test log loss is that fit not full optimizer convergence, config not changed after inspecting test metrics. Does not repeat `0.623` / “unscaled” — allowed: critique 1 required the long wording on the **card** and only **optionally** a short `/v1/model` mirror |
| `src/athletiq/ml/train.py` `max_iter` | Still 500; no retune | **Confirmed.** `cfg = {"C": 1.0, "max_iter": 500, "random_state": seed, "solver": "lbfgs"}`. `git diff 4a2f713 -- src/` is empty. No `StandardScaler`. Application source vs `4a2f713` is **only** `+3` lines on `LIMITATIONS_TEXT` |
| TEST-012 pytest | “5 passed” | **Not reproduced.** Canonical TEST-012 path is `tests/unit/test_methodology.py` only (`scripts/crews/qa/test_map.json`). This review: **2 passed, 1 warning** (`test_model_card_documents_methodology_and_limitations`, `test_v1_model_aligns_with_fr010_and_card`). Same count as honesty+QA. Suite does **not** assert the new `ConvergenceWarning` sentence; original FR-010 alignment still passes. Engineer’s “5 passed” is a miscount, **not** a product defect |

FR-010 acceptance criteria remain met: methodology (split, metrics, baselines, temporal boundary) is documented; known limitations are on the card and returned by `/v1/model` (`limitations` + `model_card_ref`). Live-pin non-convergence is no longer missing.

### IMP DoD — **Closed** (process, not PRD)

| Check | Result |
|---|---|
| IMP-001…012 **Code review passed** | All **12** ticked with the recommended wording pointing at critique 1 + application source `4a2f713` |
| Remaining **CI passed** boxes | Ticked. IMP-011 already recorded remote green (`4a2f713` / [31753742525](https://github.com/RoeeHadar/AthletIQ/actions/runs/31753742525)); others cite IMP-011 + local TEST green |
| Layout comment `provider/` | No longer “API-Sports adapter” only. Now: `Fixture + NBA Stats (ADR-011); unused ApiSports fallback` (CRIT-003) |
| Open `[ ]` in the IMP plan | **None** |

Code-review attestation remains the critique-1 review of `4a2f713`. The post-review `LIMITATIONS_TEXT` addition is the allowed IMP-012 disclosure mirror, not a model-selection change.

### PRD.md — **Unchanged (honest)**

All **17** MVP acceptance checkboxes remain `[ ]`. Engineer did not tick them. This review does not tick them.

### Note 2 — **Still uncommitted** (carry-forward)

Working-tree `README.md` still differs from `4a2f713` (records NFR-001 attest + remote CI green run `31753742525` vs committed “Remote CI green deferred”). **Not** a product defect. This follow-up **does not demand** a commit. It **does not** upgrade criterion 1 to an unconditional Yes.

## Closeout table (owner ticks only)

Do **not** apply these ticks from this review. After the owner accepts this APPROVE:

| # | Criterion | Critique 1 Tick? | This follow-up |
|---|---|---|---|
| 1 | Clean environment / documented setup | Yes after notes 2 | **Unchanged** — README honesty still uncommitted |
| 2–7 | Ingest, ETL, persist, SQL, features, baseline | Yes | **Unchanged** |
| 8 | Logistic regression on same holdout | Yes, with note 1 | **Yes** — note 1 disclosed; config not retuned |
| 9–11 | XGBoost, reproducible eval grain, prediction API | Yes | **Unchanged** |
| **12** | Methodology + known limitations | **Hold until note 1** | **Yes — unblocked** |
| 13–17 | Tests, image, GHA, docs gates, no secrets | Yes | **Unchanged** |

## Findings

| ID | Severity | Finding | Owning skill |
|---|---|---|---|
| CRIT-001 | **Closed** | Required model-card item 7 present verbatim; optional API mirror present; no peek-tune | — |
| CRIT-003 | **Closed** | IMP layout `provider/` comment aligned with ADR-011 | — |
| CRIT-004 | Closed as optional | Model-card item 8 records 0/1 baseline log-loss grain; baselines unchanged | — |
| CRIT-002 | Observation (still) | `code_commit` still `null` — not required for PRD | optional later IMP |
| CRIT-005 | Observation (still) | `PAGE_SIZE = 100` vs “effective 50” comment/docs — not required for PRD | `architecture` / IMP-003 note |
| FOLLOW-001 | Nit (claim only) | Engineer reported TEST-012 “5 passed”; independent run is **2 passed, 1 warning**. Do not treat 5 as the TEST-012 bar | — |

No blocking design↔contract↔code drift introduced by this closeout. Binding ADRs **001, 003–006, 008–011** were checked in critique 1; this slice does not change their consequences. ADR-002 remains Superseded; ADR-007 remains Proposed / out of MVP.

Static `LIMITATIONS_TEXT` mentions the **live** LR pin even when a fixture/attest stack serves `xgboost-v1`. That is readable as a live-pin limitation, not a claim that the served model is LR. Non-blocking.

## Required fixes (ordered)

**None.**

Non-required (same as critique 1): Compose e2e pytest; player ingest; scaler/iter retune; GCP; auth; reopening CR-001; demanding a README commit in this follow-up.

## Gate snapshot (MVP slice)

| Gate | Status |
|---|---|
| 0 Charter | Approved v1.0.2 |
| 1 PRD | Approved v1.0.4; acceptance **unchecked**; criterion **12 now eligible** for owner tick |
| 2 SRS + traceability | Approved v1.4.3 / v1.5.4 |
| 3 Architecture + binding ADRs | Approved / Accepted |
| 4 Design + contracts | Approved; model card **v1.0.1** (limitation 7–8) |
| 5 Implementation plan | Approved v1.0.2; IMP-001…012 Done; **code-review and CI boxes ticked** |
| 6 Code | Product train/select/serve still `4a2f713`; working tree adds FR-010 limitations clause only |
| 7 Test strategy/plan + execution | Approved docs; TEST-012 **2 passed** this review; remote CI green unchanged |
| 8–9 Release/ops | Not required to start owner manual test |

## Scope and lock validation

- [x] Only this review artifact authored
- [x] No primary product document or application-code edits by this review
- [x] No Grill-Me invocation
- [x] PRD acceptance remains unchecked by this review
- [x] CR-001 not reopened; no player ingest demanded
- [x] No Compose e2e pytest added or recommended
- [x] No LR `max_iter` / scaling / regularization retune demanded or observed
- [x] No `API_SPORTS_KEY` / signup URLs invented
- [x] Note 2 not reclassified as a product defect; criterion 1 recommendation unchanged
- [x] Attest `xgboost-v1` and live `logistic_regression-v1` not treated as contradictory
- [x] Binding ADR consequences not re-litigated; no new drift on this slice
