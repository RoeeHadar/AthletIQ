# Memory system

## Must never miss

- Save only if it will change **future** behavior. If not — do not save.
- Scope: Cursor agents in this workspace first; CrewAI integration deferred.
- **Canonical spec (Approved):** `docs/00-meta/agent-memory-system.md` v1.2.0 (portable Layers 1–2). This workspace is Appendix A only.
- **Portable installer skill:** `.cursor/skills/memory-creator/` — general AI-project memory install; not AthletIQ-specific; copy that directory to seed other repos.
- **Write types:** `status` | `episode` | `lesson` | `rule` | `pointer`. Episode is first-class persisted. `episode.next` = one-off; `lesson` = durable gist when generalizing. Pointer = gist + provenance to `docs/`, not a copy. Cause ≠ tags.
- **Goal:** human-inspired memory under reliability constraints. Hygiene + epistemics win for standing policy. Exact tag = strong **candidate**; overlap = weak; neither auto-compiles a rule.
- **Status:** `memory/situation.md` (gitignored). TTL (48h here, arbitrary) drops inject, not history.
- **Rule changes:** current rule in Must never miss; supersession **chain** in Notes.
- **Retrieval:** INDEX + ids + tags + keywords (**approximates** completion). Embeddings per spec §1.13. Extra API billing is this workspace’s cost policy, not the model.
- **Validation:** non-LLM `scripts/validate_memory.py` (status-like lines in Must never miss, episode required fields, secret heuristics). Must never miss must not look like status.
- Never load all of `memory/`. Load `INDEX.md` first; open only the subject file(s) the task needs. If unclear, keyword-search — still do not read everything. `sessionStart` injects `INDEX.md` plus TTL-filtered `memory/situation.md` (Phase 1; default 48h, arbitrary).
- Before saving: check INDEX. Update an existing subject in place (newest wins, no duplicate bullets). Else create `memory/<kebab-topic>.md` and add one INDEX line.
- Keep subject files small. Must-never-miss at top; `## Notes` below with `DATE` + `SOURCE`. Every entry: DATE and SOURCE (`user` | `agent` | `sweep` | `consolidate` | `failure` | `correction`); WHY required on correction and failure.
- Facts wait for inline user confirm. Decisions / preferences / rules that pass the future-behavior filter may be written mid-flight.
- Corrections: patch existing subject or skill **after user approval**, with DATE + WHY + HOW — no `corrections.md`. Failures: write an **episode** (required fields; `tags[]` ≠ `cause`; `next` one-off) into the matching subject; skill patches only after approval.
- Instant durable writes + sweep catch-up merge (not staging-only). Sweep reads unread transcript slice + INDEX + only subjects it will update. Sweep/consolidate must not promote `status` or recap into Must never miss.
- Always-on rule: `.cursor/rules/memory-loop.mdc`. Automation (Cursor models only — no extra embedding API billing): `preCompact` sets pending flag (cannot block compact); completed `stop` spawns Composer 2.5 Task sweep (`composer-2.5-fast`); every 5 sweeps Grok consolidate (`cursor-grok-4.5-high`); `loop_limit: 2` + gitignored `memory/.state.json` state machine prevents loops.
- **Phase:** 0+1 in this adapter (2026-08-14). Phase 4 embedding sunset clock starts 2026-08-14 (default 90 days) — stay lexical unless a §1.13 trigger fires **and** owner opts in.
- Commit INDEX + subject files to git; gitignore `memory/.state.json` and `memory/situation.md`; never commit secrets into memory.

## Notes

- **2026-08-12** · `SOURCE: consolidate` · **WHY:** Squeezed load/save and correction/failure bullets; no conflicts. User-confirmed design (grilling Q1–Q22): hooks sessionStart/preCompact/stop; K=5 consolidate cadence.
- **2026-08-14** · `SOURCE: sweep` · User Approved spec v1.2.0; portable `memory-creator` skill shipped (`.cursor/skills/memory-creator/`).

```yaml
id: ep_2026-08-14_001
time: 2026-08-14T16:00:00Z
what: "Owner Approved docs/00-meta/agent-memory-system.md v1.2.0 and a portable memory-creator skill"
source_type: user
confidence: high
tags: [memory-spec, memory-creator]
cause: none
entities: [agent-memory-system, memory-creator]
task: memory-install
next: "none — skill exists; this adapter is Phase 0+1"
```
