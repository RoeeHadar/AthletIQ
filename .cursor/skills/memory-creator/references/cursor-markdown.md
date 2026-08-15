# Adapter — Cursor (or similar) + markdown + Git

Illustration of Layer 2, not the spec. Strip product names. Do not copy another repo's subjects.

## File map

Copy from this skill's `assets/` into the **target** project. Merge, don't blindly overwrite existing hooks.

| Template | Destination |
|----------|-------------|
| `assets/markdown/INDEX.md` | `memory/INDEX.md` |
| `assets/markdown/situation.md` | `memory/situation.md` (create empty; gitignore) |
| `assets/markdown/subject.md` | use when minting the first subject; do not seed fake topics |
| `assets/cursor/memory-loop.mdc` | `.cursor/rules/memory-loop.mdc` (`alwaysApply: true`) |
| `assets/cursor/sweep.md` | `.cursor/hooks/memory-prompts/sweep.md` |
| `assets/cursor/consolidate.md` | `.cursor/hooks/memory-prompts/consolidate.md` |
| `assets/cursor/memory-lib.mjs` | `.cursor/hooks/memory-lib.mjs` |
| `assets/cursor/memory-session-start.mjs` | `.cursor/hooks/memory-session-start.mjs` |
| `assets/cursor/memory-precompact.mjs` | `.cursor/hooks/memory-precompact.mjs` |
| `assets/cursor/memory-stop.mjs` | `.cursor/hooks/memory-stop.mjs` |
| `assets/gitignore.snippet` | merge into `.gitignore` |
| `scripts/validate_memory.py` | `scripts/validate_memory.py` (or keep calling the skill copy) |

## Merge `hooks.json`

If `.cursor/hooks.json` already exists, **add** these commands; do not delete unrelated hooks.

Map portable events:

| Event | Cursor hook |
|-------|-------------|
| `on_session_start` | `sessionStart` → `node .cursor/hooks/memory-session-start.mjs` |
| `on_context_compact` | `preCompact` → `node .cursor/hooks/memory-precompact.mjs` |
| `on_turn_idle` | `stop` → `node .cursor/hooks/memory-stop.mjs` with `loop_limit: 2` |
| `on_consolidate` | every K sweeps from the stop hook (default K=5) |

See `assets/cursor/hooks.snippet.json`.

## Adapter-tunable defaults (Cursor)

These are **this adapter's** starting values, not Layer 1:

- Sweep model: `composer-2.5-fast`
- Consolidate model: `cursor-grok-4.5-high`
- Consolidate every 5 sweeps
- Situation TTL: 48h (arbitrary)
- Extra embedding APIs: **off** unless the cost-policy slot says otherwise
- `sessionStart` injects **INDEX only** at Phase 0; add accessible situation inject at Phase 1

Change model IDs in `memory-lib.mjs` if the user picks different ones. Keep sweep cheap; keep consolidate stronger.

## Always-on rule

`.cursor/rules/memory-loop.mdc` is procedural memory: load INDEX first, write-gate, episode fields, no embeddings until triggers.

Do not put project-domain locks in that rule. Domain locks belong in subject files as `rule` / `pointer` after the user confirms them.

## Git

Commit: `memory/INDEX.md`, `memory/*.md` subjects, hook scripts, prompts, always-on rule, validator.

Do not commit: `memory/.state.json`, `memory/situation.md`, secrets.

## Sweep / consolidate behavior

Sweep: unread transcript slice + INDEX + only subjects it will update. Classify writes. Discard chatter. Do not edit `.state.json` (the stop hook owns the cursor).

Consolidate: merge dupes, drop copies of external truth, keep episodes distinct, do not auto-promote rules.

## Upgrade of a messy `memory/` folder

1. Build or fix INDEX from existing files.
2. Split each file into Must never miss (rules/pointers) vs Notes (episodes/lessons).
3. Move status-like lines into `situation.md`.
4. Wrap encode-worthy events as episode YAML with required fields.
5. Replace pasted spec/docs with pointers.
6. Run the validator. Do not delete unmatched notes — park them under Notes with `SOURCE: agent` until the user confirms.
