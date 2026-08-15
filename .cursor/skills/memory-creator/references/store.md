# Layer 2 — Store, schemas, validation

Names in `<angle-brackets>` are adapter slots. Backends (files, SQLite, Postgres, Redis, objects, vectors) hide behind this interface.

## Lifecycle events (abstract)

| Event | Meaning | Typical adapter |
|-------|---------|-----------------|
| `on_session_start` | New working context | inject catalog + accessible working state |
| `on_context_compact` | Working memory about to drop | mark unread experience for sweep; do not block compact |
| `on_turn_idle` | Agent finished a turn | sweep unread experience into the store |
| `on_consolidate` | Periodic integration | merge dupes, drop copies of external truth, do not auto-promote rules |

Loop limits and which model runs sweep vs consolidate are **adapter** choices.

## MemoryStore

```text
MemoryStore
  write_episode(ep) -> id
  write_lesson(lesson) -> id
  write_status(status)            # volatile
  write_rule(rule) / write_pointer(ptr)
  link(from_id, rel, to_id)       # D4
  supersede(old_id, new_id, why)
  get_working()                   # accessible situation only
  get_candidates(cues)            # Stage A
  rank(candidates, context)       # Stage B
  retrieve(context, budget)       # A + B + optional budget
  validate(write) -> ok | errors  # deterministic, not LLM
```

A markdown install approximates this with files + instructions. A database install should expose the same verbs.

## Deterministic validation

Every write is checked by a **non-LLM** layer (schema, types, DB constraints, middleware). LLMs must not be the only categorizer.

Minimum checks:

- write type present
- episode required fields present
- `status` not in the durable-policy collection
- `pointer` does not contain a pasted external body
- secrets redacted (see `security.md`)

For markdown subjects + INDEX, run `scripts/validate_memory.py`.

## Episode schema (day one)

Persist **from day one** as structured records (YAML/JSON/table — adapter). Do **not** use freeform recap as the store.

**Required** (keep this set small):

- `id`, `time`, `what`, `source_type`, `confidence`

**Recommended:**

- `tags[]` (index labels, 0..N)
- `cause` (**hypothesis, separate from tags**)
- `entities[]`, `task`, `goal`
- `state_before`, `state_after` (or `context` + `outcome`)
- `next` (immediate one-off)
- `source_reliability`, `valid_at`
- `derived_lesson_id` (optional)

Canonical YAML (any equivalent encoding is fine):

```yaml
id: ep_2026-08-14_001
time: 2026-08-14T16:00:00Z
what: "External API returned 429 after sustained volume"
source_type: observation
confidence: med
tags: [http-429, provider-x]
cause: "quota exhausted"          # hypothesis, not the tag list
entities: [provider-x, ingest]
task: ingest
state_before: "requests succeeding"
state_after: "ingest halted"
next: "back off and honor Retry-After"   # this event only
```

`source_type` on episodes may be recorded as `user` | `observation` | `inference` | `external` | `derived`. Some adapters also stamp a write pipeline (`sweep` | `consolidate` | `correction` | `failure`) as `SOURCE` on the surrounding note — that is provenance of *how it was written*, not a substitute for `source_type`.

## Lesson record

Created only per spec § episode vs lesson (not automatically on first episode).

Required: `id`, `gist`, `derived_from[]`, `confidence`  
Recommended: `tags[]`, `when` (condition), `exception_to`

## Pointers and rules — provenance

```text
source_type, source_id, source_location, observed_at, validated_at, validated_by
gist: why this reference matters
```

Not all fields required. `user said` ≠ `agent inferred` ≠ `external spec`.

**Pointer:** gist + provenance + id. No copy of the external body.

**Rule:** standing policy, operator-approved. Prefer `when Y, do X`. Current rule in the durable-policy collection; superseded text stays in an audit chain, not as a second current rule.

## Working vs persistent vs external

| Backend | Holds |
|---------|--------|
| Working | `status` / situation; TTL = inject cutoff |
| Persistent | episodes, lessons, rules, pointers, relationship edges, supersession chain |
| External | project source of truth |

## Markdown layout (one common adapter, not the model)

```text
<memory-root>/
  INDEX.md              # catalog — only file always loaded
  <kebab-topic>.md      # one subject per concern
  situation.md          # working; typically VCS-ignored
  .state.json           # hook cursor; typically VCS-ignored
```

Subject shape:

```markdown
# <Title>

## Must never miss

- rules and thin pointers only

## Notes

- episodes, lessons, supersession chain, dated provenance
```

INDEX format (one line per subject):

```text
memory/<kebab-topic>.md — <one-line description>
```

Load INDEX first. Open only the subject files the task needs. Never read the whole tree by default.

## Write gate (operational)

Ask: will this change **future** behavior? If no — do not save.

| Kind | Action |
|------|--------|
| Decision / preference / rule | Write as `rule` or `pointer` on the matching subject |
| Fact | Ask the user; write only after they confirm |
| Status | Working backend only. Never durable policy |
| Correction | After approval: patch subject or skill with DATE + WHY; supersede via chain |
| Encode-worthy event | `write_episode` with required fields. Do not auto-write a lesson or rule |

Update an existing subject in place (newest wins, no duplicate bullets). Else create a subject and one catalog line.

## Memory usefulness (later)

Log: `retrieved_ids` → `action` → `outcome` → `useful: yes/no/unknown`.  
Preferred future ranker target — more important than fitting accessibility equations.
