# Engineering lifecycle

## Must never miss

- Non-trivial implementation requires upstream docs **`Approved`** per permanent gates. **Before Gate 6 code:** Approved Design, **Implementation Plan**, and **Test Strategy** (prefer Test Plan) — Gate 7 *number* is verification closeout; Test Strategy must not stay Draft while coding (`docs/00-meta/gates.md` §22). Trivial fixes exempt. Enforced by `.cursor/rules/engineering-lifecycle.mdc`.
- **Gates 0–5 + Gate 7 Approved; Gate 6 — IMP-001…018 Done (CR-004; code review APPROVE 2026-08-16).** Never claim CI green from local pytest — remote attestation only (SHAs/run IDs live in `docs/00-meta/reviews/`, not here).
- **2026-08-16** · `SOURCE: agent` · **WHY:** CR-005 working-tree code reviewed. **HOW:** Gate 6 IMP-019–025 **code-review APPROVE** (`docs/00-meta/reviews/2026-08-16-cr005-lead-dev-code-review.md`). Do not mark IMPs Done / traceability Implemented until remote CI is attested. Do not mix fixture vs live NBA pins. Demo UI only `http://127.0.0.1:8000/`.
- **2026-08-16** · `SOURCE: agent` · **WHY:** Lead-dev CR-005 docs re-review closed CR5-001–009. **HOW:** Gate 6 IMP-019–025 **unblocked** (superseded for “may start” by the code-review bullet above). Artifact: `docs/00-meta/reviews/2026-08-16-cr005-lead-dev-docs-rereview.md` (**APPROVE**).
- **2026-08-16** · `SOURCE: user` · **WHY:** Owner confirmed CR-005; docs then lead review then code. **HOW:** Docs path completed via rereview APPROVE (see newer bullet). Same-model code review remains IMP DoD after implementation, not an owner stop. Do not mix fixture vs live NBA pins. Demo UI only `http://127.0.0.1:8000/`.
- Never invent product facts, requirements, users, metrics, or architectural decisions. Invoke **Grill-Me** (`.cursor/skills/grill-me/`) before `[OPEN QUESTION]` / `[ASSUMPTION]` / guessing — placeholders only after Grill-Me cannot resolve.
- **PRD vs Charter boundary:** PRD = product capabilities/users only; portfolio technical must-demonstrate constraints live in **Charter** and ADRs — do not re-lock them as PRD product features.
- ADR files owned exclusively by `architecture-decisions`; other skills flag `[DECISION PENDING: see ADR-XXX]` and never author ADRs. `engineering-review` flags drift only — never authors primary content, never calls Grill-Me.
- Approved Charter/PRD product intent ≠ Accepted architecture. Pipeline sketches remain **intent only** until ADRs exist. If jump-to-architecture before SRS: draft **Proposed** ADRs only — Accept only after SRS exists and user approves.
- **No separate pending-approval folder** — all docs under `docs/`; approval = each file's **`Status` header**. Index: `docs/README.md`; gates: `docs/00-meta/gates.md`.
- **Traceability columns are independent:** never set Implementation=`Implemented` solely because a test is Passing; update each column only from direct evidence for that column.
- **Docs honesty:** dual review **9/10** (2026-08-13). Approved docs **≠** MVP-complete or publish-bar satisfied. Reports under `docs/00-meta/reviews/`.
- **2026-08-16** · `SOURCE: consolidate` · **WHY:** Dropped provider/signup/WNBA-demand copies (owned by `athletiq-product`); kept process publish-bar. **Publish-bar:** no re-approve Gates 0–7; per step QA (`scripts/crews/qa/`) → lead engineer → **lead manager (GPT 5.6 Sol; owner may authorize Cursor Grok Extra High)**. **Stop** for owner input, contradiction, unknown next, or MVP ready for manual test. Do not reopen CR-001. Do not add Compose e2e pytest to close NFR-001. Do not retune live LR against test log loss 0.623 (disposition: `athletiq-product` CRIT-001). **MVP closeout:** owner ticked PRD MVP acceptance (`docs/02-product/PRD.md` v1.0.5, 2026-08-15). **CR-004** IMP-001–018 Done. **CR-005** Accepted (docs); Gate 6 unblocked by lead-developer docs rereview **APPROVE** 2026-08-16.

## Notes

- **2026-08-13** · `SOURCE: consolidate` · Process: 8 skills; bidirectional traceability; drift triple; CRs re-enter Requirements. Gate 6 unblocked by Approved test strategy/plan; ADR-010 Accepted; `traceability.md` canonical req↔test; NFR-004 = no hard SLO via TEST-008; TEST-001…014.
- **2026-08-14** · `SOURCE: user` · Owner authorized MVP critique on Cursor **Grok Extra High** (`cursor-grok-4.6-xhigh`) after GPT 5.6 Sol API limit. Same lead-manager bar. Artifact: `docs/00-meta/reviews/2026-08-14-lead-mvp-critique.md`.
- **2026-08-14** · `SOURCE: sweep` · Owner may say "Grok 5.6 Extra High"; launcher has **`cursor-grok-4.6-xhigh` only** — do not hunt for a separate Grok 5.6 slug.
