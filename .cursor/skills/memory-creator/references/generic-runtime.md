# Adapter — generic runtime (files, LangGraph, CrewAI, custom)

Use when the host is **not** Cursor hooks, or when the store is not markdown files. Layer 1 does not change.

## Files-only coding agent (no IDE hooks)

Still use markdown INDEX + subjects from `assets/markdown/` if the user wants a file store.

Map lifecycle onto whatever the host provides:

| Event | If the host has no hooks |
|-------|---------------------------|
| `on_session_start` | Put catalog-load instructions in `AGENTS.md`, a project rule, or the system prompt |
| `on_context_compact` | If the host signals compaction, set a pending-sweep flag in working state; never block |
| `on_turn_idle` | End-of-turn reminder in the rule: sweep unread experience, or run a scheduled job |
| `on_consolidate` | Periodic task (every K sweeps, nightly cron, or human `/consolidate`) |

Copy `assets/generic/agent-instructions.md` into the project's agent-instruction file (merge; do not overwrite the whole file).

Working backend: `memory/situation.md` or an equivalent TTL document, ignored by VCS.

## SQLite / JSONL store

Implement `MemoryStore` (`references/store.md`) against the DB or log. Suggested tables/collections:

- `episodes` (required columns = required episode fields)
- `lessons`
- `rules`
- `pointers`
- `status` (volatile; TTL column)
- `links` (`from_id`, `rel`, `to_id`)
- `supersessions` (`old_id`, `new_id`, `why`, `at`)

`validate` = CHECK constraints + a small insert trigger or application middleware. Do not accept freeform recap as the row body without the required columns.

JSONL: one episode per line; lessons/rules in separate files or typed lines. Still keep a catalog so agents do not scan every file by default.

## LangGraph

- Working: graph state (or a short-TTL store) for `status`
- Persistent: SQLite/Postgres node or a memory service behind `MemoryStore`
- `on_session_start`: first node loads catalog + accessible situation
- `on_turn_idle`: after `END` or a `memory_sweep` node
- Do not stuff the full store into every node's state (cue overload + token cost)

## CrewAI / other multi-agent frameworks

Install this spec as a **shared project memory** with provenance, or do not install it.

Do **not** silently dual-write into the framework's built-in memory: those stores often skip write types, authority, and approval-to-rule. If the user wants both, keep them separate and pointer across.

Crew / agent YAML should not receive the whole catalog. Inject INDEX (or ranked candidates) the same way a coding agent would.

## Custom runtime

Fill the mapping table in `adapters.md`. Minimum viable: catalog, episode schema, write gate, `validate`, security policy. Hooks are optional; a documented manual sweep is an adapter, not a failure of the model.

## Embeddings

Same triggers as `spec.md`. Cost policy is the user's. Local vs cloud is not a Layer 1 decision.
