# Memory system

## Must never miss

- Save only if it will change **future** behavior. If not — do not save.
- Scope: Cursor agents in this workspace first; CrewAI integration deferred.
- Never load all of `memory/`. Load `INDEX.md` first; open only the subject file(s) the task needs. If unclear, keyword-search — still do not read everything. `sessionStart` injects `INDEX.md` only; subjects load on demand.
- Before saving: check INDEX. Update an existing subject in place (newest wins, no duplicate bullets). Else create `memory/<kebab-topic>.md` and add one INDEX line.
- Keep subject files small. Must-never-miss at top; `## Notes` below with `DATE` + `SOURCE`. Every entry: DATE and SOURCE (`user` | `agent` | `sweep` | `consolidate` | `failure` | `correction`); WHY required on correction and failure.
- Facts wait for inline user confirm. Decisions / preferences / rules that pass the future-behavior filter may be written mid-flight.
- Corrections: patch existing subject or skill **after user approval**, with DATE + WHY + HOW — no `corrections.md`. Failures: write lesson immediately into matching subject (`SOURCE: failure`, WHAT/WHY/NEXT); skill patches only after approval.
- Instant durable writes + sweep catch-up merge (not staging-only). Sweep reads unread transcript slice + INDEX + only subjects it will update.
- Always-on rule: `.cursor/rules/memory-loop.mdc`. Automation (Cursor models only — no external API billing): `preCompact` sets pending flag (cannot block compact); completed `stop` spawns Composer 2.5 Task sweep (`composer-2.5-fast`); every 5 sweeps Grok consolidate (`cursor-grok-4.5-high`); `loop_limit: 2` + gitignored `memory/.state.json` state machine prevents loops.
- Commit INDEX + subject files to git; gitignore `memory/.state.json`; never commit secrets into memory.

## Notes

- **2026-08-12** · `SOURCE: consolidate` · **WHY:** Squeezed load/save and correction/failure bullets; no conflicts. User-confirmed design (grilling Q1–Q22): hooks sessionStart/preCompact/stop; K=5 consolidate cadence.
