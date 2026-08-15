# Engineering lifecycle

## Must never miss

- Non-trivial implementation requires upstream docs **`Approved`** per permanent gates. **Before Gate 6 code:** Approved Design, **Implementation Plan**, and **Test Strategy** (prefer Test Plan) — Gate 7 *number* is verification closeout; Test Strategy must not stay Draft while coding (`docs/00-meta/gates.md` §22). Trivial fixes exempt. Enforced by `.cursor/rules/engineering-lifecycle.mdc`.
- **Gates 0–5 + Gate 7 Approved; Gate 6 — IMP-001…012 Done.** Never claim CI green from local pytest — remote attestation only.
- Never invent product facts, requirements, users, metrics, or architectural decisions. Invoke **Grill-Me** (`.cursor/skills/grill-me/`) before `[OPEN QUESTION]` / `[ASSUMPTION]` / guessing — placeholders only after Grill-Me cannot resolve.
- **PRD vs Charter boundary:** PRD = product capabilities/users only; portfolio technical must-demonstrate constraints live in **Charter** and ADRs — do not re-lock them as PRD product features.
- ADR files owned exclusively by `architecture-decisions`; other skills flag `[DECISION PENDING: see ADR-XXX]` and never author ADRs. `engineering-review` flags drift only — never authors primary content, never calls Grill-Me.
- Approved Charter/PRD product intent ≠ Accepted architecture. Pipeline sketches remain **intent only** until ADRs exist. If jump-to-architecture before SRS: draft **Proposed** ADRs only — Accept only after SRS exists and user approves.
- **No separate pending-approval folder** — all docs under `docs/`; approval = each file's **`Status` header**. Index: `docs/README.md`; gates: `docs/00-meta/gates.md`.
- **Traceability columns are independent:** never set Implementation=`Implemented` solely because a test is Passing; update each column only from direct evidence for that column.
- **Docs honesty:** dual review **9/10** (2026-08-13). Approved docs **≠** MVP-complete or publish-bar satisfied. Reports under `docs/00-meta/reviews/`.
- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Stripped status/clone/commit gossip from Must never miss; kept standing publish-bar rules + thin review pointers. **Publish-bar:** no re-approve Gates 0–7; per step QA (`scripts/crews/qa/`) → lead engineer → **lead manager (GPT 5.6 Sol; owner may authorize Cursor Grok Extra High)**. **Stop** for owner input, contradiction, unknown next, or MVP ready for manual test. Do not reopen CR-001. Live path `--provider nba-stats` (CR-002 / ADR-011). Do not invent `API_SPORTS_KEY`/signup URLs. Do not add Compose e2e pytest to close NFR-001. **2026-08-15** · `SOURCE: user` · Owner ticked PRD MVP acceptance (`docs/02-product/PRD.md` v1.0.5). Publish-bar owner closeout is done. Do **not** demand player ingest (CR-001), GCP, or application auth unless a later CR. **Closed steps (pointers):** Step 1, GHA `4a2f713`, NFR-001, honesty+QA, MVP critique APPROVE + note-1 closeout — `docs/00-meta/reviews/2026-08-13-lead-step1-qa.md`, `2026-08-14-lead-gha-4a2f713.md`, `2026-08-14-lead-nfr001-attest.md`, `2026-08-14-lead-honesty-qa.md`, `2026-08-14-lead-mvp-critique.md`, `2026-08-14-lead-mvp-critique-2.md`. Do not retune live LR against test log loss 0.623. Post-MVP work re-enters Gate 2 via CR — do not start betting, multi-sport, or player ingest from chat direction alone.

## Notes

- **2026-08-13** · `SOURCE: consolidate` · Process: 8 skills; bidirectional traceability; drift triple; CRs re-enter Requirements. Gate 6 unblocked by Approved test strategy/plan; ADR-010 Accepted; `traceability.md` canonical req↔test; NFR-004 = no hard SLO via TEST-008; TEST-001…014.
- **2026-08-14** · `SOURCE: user` · Owner authorized MVP critique on Cursor **Grok Extra High** (`cursor-grok-4.6-xhigh`) after GPT 5.6 Sol API limit. Same lead-manager bar. Artifact: `docs/00-meta/reviews/2026-08-14-lead-mvp-critique.md`.
- **2026-08-14** · `SOURCE: sweep` · Owner may say "Grok 5.6 Extra High"; launcher has **`cursor-grok-4.6-xhigh` only** — do not hunt for a separate Grok 5.6 slug.
