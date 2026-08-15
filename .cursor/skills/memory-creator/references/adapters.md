# Choosing an adapter

Read this, then **exactly one** adapter file.

| Host | Persistent backend | Read next |
|------|-------------------|-----------|
| Cursor (or Claude Code with project rules + hooks) + files | markdown INDEX + subjects | `cursor-markdown.md` |
| Any coding agent without IDE hooks | markdown INDEX + subjects | `generic-runtime.md` (files section) |
| LangGraph / CrewAI / custom runtime | SQLite, JSONL, or files | `generic-runtime.md` |
| User named a different store (Postgres, Redis, …) | that store | `generic-runtime.md` + implement `MemoryStore` against it |

If the user has not chosen a host, ask. Do not assume Cursor because this skill was authored in a Cursor repo.

## Portability invariant

The **model** (`spec.md`) stays identical across rows. Only paths, lifecycle wiring, and encoding change.

## What every adapter must map

| Portable | Adapter fills in |
|----------|------------------|
| Catalog | How agents discover subjects/collections without loading everything |
| Durable policy collection | Where `rule` / `pointer` live |
| Episode encoding | YAML blocks, JSONL rows, or table rows |
| Working backend | File, Redis, in-process — with TTL inject cutoff |
| `on_session_start` | Inject catalog (+ accessible situation if Phase 1) |
| `on_context_compact` | Mark unread; do not block compact |
| `on_turn_idle` | Sweep unread into the store |
| `on_consolidate` | Periodic hygiene; no auto-promote to rules |
| `validate` | Script, schema, or DB constraints |
| External truth | Path/URI scheme for pointers |
| Cost policy | Whether extra APIs are allowed |

## Do not

- Ship two adapters at once “just in case”
- Copy a worked instance from another product into the target
- Share this store with a framework's built-in agent memory unless the user explicitly asks (different epistemics)
