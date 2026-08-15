---
name: memory-creator
description: >-
  Install or upgrade a portable human-inspired agent memory system (episodes,
  lessons, rules, pointers, situation TTL, sweep/consolidate, non-LLM validation)
  in an AI development project. Use whenever the user wants agent memory,
  persistent memory across sessions, a memory loop, memory-creator, INDEX/catalog
  memory, remember-across-chats, or to add memory to Cursor, Claude Code,
  LangGraph, CrewAI, or custom agents — even if they do not name this skill.
  Do not use for application caches, product analytics stores, or a framework's
  built-in agent memory unless the user is explicitly installing this spec.
---

# Memory creator

Install (or upgrade) a **human-inspired agent memory system under reliability constraints** in the current project. After install, agents **use** memory via the generated always-on instructions — they do not need this skill for ordinary recall/write.

The memory **model** does not depend on Cursor, markdown, Git, or any product domain. Host, files, VCS, and models are adapters. Do not copy another project's requirement IDs, service names, or product locks into the new install.

## Progressive disclosure

Read this file first. Then open **only** what the current pass needs:

| Need | File |
|------|------|
| Behavior contract (Layer 1) | `references/spec.md` |
| Store, schemas, validation (Layer 2) | `references/store.md` |
| What to ship now (phases 0–4) | `references/phases.md` |
| Which host/backend | `references/adapters.md`, then **one** of `cursor-markdown.md` or `generic-runtime.md` |
| Secrets / PII / untrusted writes | `references/security.md` |

Copy from `assets/`. Run `scripts/validate_memory.py` when the persistent backend is markdown subjects + INDEX.

## Why this exists

Agents already have context windows. That is working memory: it dies at compact and does not survive sessions. A durable store that **dumps recap into a “never miss” bucket** causes cue overload (too many items share one cue) and forks the project's real source of truth.

This skill installs a store that:

- writes only what will change **future** behavior
- keeps episodes distinct from lessons and rules
- points at external truth instead of copying it
- lets hygiene + epistemics win for standing policy (association may retrieve; it must not auto-write rules)

## Adapter slots (ask — do not invent)

If a grilling skill is available, use it for these. Otherwise ask before creating files. Parentheses are **starting defaults**, not locks.

1. **Host:** Cursor / Claude Code / other coding agent / LangGraph / CrewAI / custom
2. **Persistent backend:** markdown INDEX + subjects / JSONL / SQLite / other
3. **Working backend:** gitignored situation file / other TTL store / skip until Phase 1
4. **External truth:** path to docs/wiki/tickets, or none
5. **Lifecycle:** IDE hooks + sweep/consolidate / framework callbacks / manual only
6. **Cost:** extra paid embedding or memory APIs allowed? (default **no**)
7. **Phase now:** 0 / 0+1 / 0–2 (do not jump to embeddings or fitted rankers)
8. **Redaction:** PII classes beyond secrets/credentials

If the user says “portable defaults for a Cursor coding repo,” take: Cursor host, markdown INDEX + subjects, `situation.md` gitignored, Git, Phase 0+1, no extra embedding APIs, sweep/consolidate on Cursor models. Still do not import another repo's product memory.

## Detect an existing install

Search for a catalog (`INDEX.md` or equivalent), a working/situation store, an always-on memory rule, sweep/consolidate prompts, or a `MemoryStore`-like module.

- **None:** greenfield install for the chosen adapter.
- **Present:** upgrade in place. Retag write types, add missing episode fields, move status out of durable policy. Do not delete user content. Do not overwrite customized model IDs or paths without asking.

## Procedure

1. Read `references/spec.md` and `references/store.md`.
2. Resolve adapter slots (section above). Read `references/adapters.md`, then **only** the matching adapter file.
3. Read `references/phases.md` and `references/security.md`. Install the requested phase, not the whole roadmap.
4. Copy templates from `assets/` into the **target project** (this skill may be running in that project or used to seed another tree). Substitute adapter slots (models, paths, TTL).
5. Wire lifecycle events to the host (`on_session_start`, `on_context_compact`, `on_turn_idle`, `on_consolidate`). Event names are portable; hook files are not.
6. Add gitignore (or equivalent) for working state and hook cursor files. Never gitignore the catalog or durable subjects unless the user wants a private-only store.
7. Run validation (`scripts/validate_memory.py` for markdown). Fix errors before claiming done.
8. Stop. Report paths created or changed. Do not start a memory dump of the current chat into the new store unless the user asks.

## What “done” means (Phase 0)

- Catalog exists and is the only always-loaded memory file
- Write types are `status` | `episode` | `lesson` | `rule` | `pointer`
- Durable policy collection holds **rules and thin pointers only**
- Episode records can be stored with required fields `id`, `time`, `what`, `source_type`, `confidence`
- `status` cannot land in durable policy (convention + validator)
- Pointers gist+cite external truth; they do not paste it
- Secrets policy is in the always-on instructions
- A non-LLM validator exists for the chosen backend (script, schema, or DB constraints)

Phase 1 adds a working backend with TTL that drops **inject**, not history. Later phases are in `references/phases.md`.

## Must not

- Fork the project's docs/wiki into memory
- Auto-promote a lesson to a rule
- Equate `tags[]` with `cause`
- Collapse episode into lesson (or store only `episode.next` and call it memory)
- Treat embeddings, decay formulas, or graph algorithms as required for install
- Merge this store silently with a framework's built-in memory
- Write product-domain examples from this skill's origin repo into the target

## Outputs (typical)

Depend on the adapter. Markdown + Cursor is spelled out in `references/cursor-markdown.md`. Generic runtimes are in `references/generic-runtime.md`.

Always tell the user the **skill path** (this directory) and the **install paths** in the target project.

## Validation

Markdown backend:

```text
python <this-skill>/scripts/validate_memory.py --root <project-root>
```

Other backends: implement `MemoryStore.validate` as schema/constraints; do not use an LLM as the only categorizer.

Checklist:

- [ ] Adapter slots confirmed or explicitly defaulted
- [ ] Only one adapter reference was followed
- [ ] No product-domain copy from another project
- [ ] Phase matches what the user asked
- [ ] Validator runs (or equivalent constraints exist)
- [ ] Working store is not committed (if Git + Phase 1)
- [ ] User has paths to review
