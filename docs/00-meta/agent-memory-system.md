# Agent memory — portable specification

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-14  
Version: 1.2.0

**What this is:** A general specification for **human-inspired agent memory under reliability constraints**. It is the intended anchor for a reusable skill that can be installed in coding, research, planning, support, analysis, robotics, and multi-agent systems.

**Installer skill:** [`.cursor/skills/memory-creator/`](../../.cursor/skills/memory-creator/SKILL.md) — portable; copy that directory. Appendix A is not the skill.

**How to read it:** three layers. Layers 1–2 are portable. Layer 3 is **not** the spec.

| Layer | Content | Depends on Cursor / markdown / Git / a product domain? |
|---|---|---|
| **1. Behavior** | What memory must do | **No** |
| **2. Skill** | Procedures, schemas, store interface, lifecycle events | **No** (abstract adapters) |
| **3. Reference implementation** | One worked instance | Yes — Appendix A only |

**Portability invariant:** The memory **model** MUST NOT depend on a particular IDE, agent framework, file format, VCS, or product domain. Those are adapters. Examples from one project, if used, are boxed as *illustration*, never as load-bearing rules.

**Revision 1.2.0** folds two reviews of v1.1.0: split instance from spec; formalize four dimensions; make episode first-class with a day-one store format; split cause vs tags; operationalize exceptions, relationships, epistemics, and memory usefulness.

---

## Layer 1 — Memory behavior

### 1.1 Three objectives

These pull in different directions. The contract is explicit.

| Objective | Optimizes for | Human memory *exhibits* (not: “is identical to”) |
|---|---|---|
| **Hygiene** | Auditability, low interference, no duplicate source of truth, no stale local state as policy | Weakly — humans confabulate and overwrite |
| **Behavior** | Encode experiences, retrieve from partial cues, generalize with evidence, reduce accessibility | Associative, lossy, self-reorganizing |
| **Epistemics** | Trust: source, authority, confidence, temporal validity, usefulness | Weak and biased — **do not copy that** |

**Conflict rule:** hygiene + epistemics win for anything that becomes **standing policy** (rules, skills, published facts). Behavior may be richer for episodes, candidate generation, and ranking. Nothing associative auto-writes policy.

**Target:** human-inspired memory behavior, subject to engineering reliability constraints.

**Borrow:** episodic encoding, semantic abstraction, pattern separation, pattern completion (as a *behavioral* property), pattern integration, cue-driven recall, accessibility decay, provenance-preserving reconsolidation, context-bounded generalization.

**Reject:** treating confabulation as fact; unverified generalization into policy; silent rule flips; **salience as emotional valence** (for agent memory, salience = impact / prediction-error / explicit mark — not affect); biological attractor simulation; fitted neuroscience equations without a measured target.

**Invariant:** store **what changes future behavior**, not what merely contains information. Authoritative external knowledge stays in the project’s source-of-truth store (docs, wiki, tickets, code comments — adapter-defined). Memory **points** or **gists**; it does not fork that store.

### 1.2 Four independent dimensions

Do not collapse these.

**D1 — Representation**

| Kind | Meaning |
|---|---|
| Working | Transient, currently accessible state |
| Episodic | A specific event in time |
| Semantic | Generalized knowledge (facts, preferences, constraints, strategies, beliefs) |
| Procedural | How to act (skills, productions, approved rules) |

**D2 — Persistence**

| Kind | Meaning |
|---|---|
| Volatile | Working / situation; TTL reduces *accessibility* |
| Persistent | Episodes, lessons, semantic, procedural |
| External | Authoritative knowledge owned outside the memory store |

**D3 — Write classification** (what the writer emits)

`status` | `episode` | `lesson` | `rule` | `pointer`

`episode` **is** a persisted write type. `pointer` is a **reference mechanism** to external knowledge, not a fourth representation alongside episode/semantic/procedural.

**D4 — Relationships** (typed links by id; need not be a graph DB)

`derived_from` | `supports` | `contradicts` | `exception_to` | `generalizes` | `similar_to` | `same_cause` | `same_situation` | `same_entity` | `same_strategy` | `same_outcome` | `supersedes` | `caused_by`

**Recurrence** is one relationship (`same_cause` / `similar_to`), not the whole association model.

Semantic memory is **not** “pointer + gist.” It is internally learned gist, **optionally** anchored to an external source via `pointer`.

### 1.3 Interference (three kinds)

| Kind | Failure | Hygiene response |
|---|---|---|
| **Retrieval** | Too many items share one cue (fan / cue overload) | Split cues; don’t dump everything into one “never miss” bucket |
| **Representation** | Distinct events collapsed onto one label | Keep episodes distinct; don’t equate tag with cause |
| **Source / authority** | User assertion, agent inference, hallucination, and external docs treated as equal | Provenance + authority; never let association erase source |

Retrieval interference is *not* catastrophic interference in trained weights. Fan-effect / cue-overload is the retrieval-time account.

### 1.4 Lifecycle

```text
EXPERIENCE  →  ENCODE EPISODE  →  ASSOCIATIONS
                    ↓
              CONSOLIDATION (integration)
                    ↓
         SEMANTIC / LESSON  →  (evidence + approval)  →  PROCEDURAL / RULE
```

```text
CURRENT CONTEXT → CUES → CANDIDATE GENERATION (broad)
                      → CANDIDATE EVALUATION (rank)
                      → WORKING MEMORY → ACTION → OUTCOME
                      → usefulness signal + provenance-preserving reconsolidation
```

### 1.5 Encode when future behavior may change

Not only failure and decision. Encode an **episode** when the event is expected to influence future behavior, including:

failure, success, decision, correction, discovery, preference, constraint, commitment, unexpected observation, plan outcome, environmental change, resolved ambiguity.

**Event vs fact:** “User asked for concise answers on date T” is an episode. “User prefers concise answers” is semantic, promoted only with repeated evidence and context bounds. One day’s request must not become a standing preference (over-personalization).

**Context specificity:** preserve the boundaries in which an observation was valid. “Strategy X worked in context A and failed in context B” must not collapse to “strategy X works” unless evidence supports erasing the bound.

### 1.6 Episode vs lesson (disambiguation)

| | Episode | Lesson |
|---|---|---|
| What it is | The experiential record of **one** event | A **durable cross-session gist** derived from one or more episodes |
| `next` / immediate action | `episode.next` = one-off action for **this** event | Lesson body = what the **next** agent should generally remember |
| When to write | At encode time, whenever §1.5 fires | When a human confirms it is worth generalizing, **or** when a relationship flags a candidate and an operator accepts a gist — **not** automatically on first episode |
| Policy? | Never | Still not a `rule`. Promotion to `rule` requires approval |

If you only store `episode.next`, you have a to-do, not semantic memory. If you only store a lesson, you have lost the event (no pattern separation, no context bounds).

### 1.7 Pattern trio

| Operation | Property | Honest v1 mechanism |
|---|---|---|
| **Separation** | Similar events stay distinct | Separate episode records; timestamps; tags ≠ cause |
| **Completion** | Partial cues surface related priors | **Approximated** by multi-cue exact/ID/keyword match. That is **not** paraphrase-complete. Embeddings (or equivalent) are the later implementation of this *property* |
| **Integration** | Several episodes become one abstraction | Lesson / semantic gist with `derived_from` + evidence; not a merge that deletes episodes |

### 1.8 Recurrence, promotion, exceptions

**Exact id/tag match is a deliberate departure from human-like generalization** for **policy**. It is the strongest recurrence *signal*, not the definition of “I’ve seen this kind of problem.”

| Signal | Relationship | May write a `rule`? |
|---|---|---|
| Exact tag / id | `same_cause` strong | No — candidate |
| Shared entity / task / context | candidate | No |
| Semantic / paraphrase overlap | candidate (keywords now; embeddings if triggered) | No |
| Operator approval | compilation | **Yes** |

**Invariant:** similarity may retrieve; similarity does not establish causality or policy.

**Promotion:** prefer **conditional** knowledge (“when Y, do X”) over universals. Evidence strength should consider **context diversity** and **source quality**, not only count (10 repeats in one environment can be weaker than 3 consistent outcomes across contexts). Specify the principle now; do not fit a formula yet.

**Exception (operational):**

```text
general:     when Y, do X                    (semantic or rule)
exception_to: <id>
when:        Z
evidence:    episode_ids[]
```

Exceptions are first-class relationships, not a hoped-for behavior.

### 1.9 Retrieval: two stages

**Stage A — candidate generation** (“could this possibly be relevant?”): exact ids, entities, tags, cause, task, temporal neighborhood, typed relationships (`similar_to`, `contradicts`, `exception_to`, …). Interface must allow later causal / outcome / semantic channels without redesign.

**Stage B — candidate evaluation** (“how useful for *this* situation?”): `retrieval_score(memory, context)` using relevance, confidence, source reliability, recency/accessibility, salience (impact, not affect), context fit. **Importance ≠ relevance.**

Context **budgeting** (knapsack) happens **after** A and B, only if the candidate set overflows. Any `recency × importance × rel` product is a **placeholder heuristic**, not a fitted model.

### 1.10 Provenance-preserving reconsolidation

Human reconsolidation is not claimed. The engineering approximation:

retrieve → use → if evidence conflicts, write a **new** episode (and a `supersedes` / relationship), **do not silently mutate** the old episode’s factual fields.

Keep a **recoverable supersession chain**. Normal retrieval exposes the current interpretation; audit can walk the chain.

### 1.11 Epistemics

Distinguish, do not collapse:

| Field | Meaning |
|---|---|
| `source_type` | `user` \| `observation` \| `inference` \| `external` \| `derived` |
| `source_reliability` | Trust in that class of source in this project |
| `confidence` | How strongly this record claims the proposition (set at encode; **not** raised by rewrite count) |
| `valid_at` / `last_verified` | Temporal validity |
| `authority` | e.g. user instruction > approved external spec > agent inference > unconfirmed observation |

A high-confidence **false observation** is still an observation. Authority prevents treating it as a user lock.

### 1.12 Forgetting

- **Working / situation:** TTL (default heuristic, adapter-tunable) removes from **automatic inject**. Optional archive in persistent store. Not “never existed.”
- **Long-term:** reduced **accessibility** (rank), not deletion, unless a security/retention policy requires purge.
- **Salience:** high-impact failures may outrank age (later). Not emotional weighting.

### 1.13 Deferred mechanisms (not “not human-inspired”)

| Mechanism | Role in the *model* | Build when |
|---|---|---|
| Embedding / dense `rel` | Closer approximation of pattern completion | Retrieval difficulty: paraphrase/association **misses**, or scale heuristic, or sunset |
| Accessibility curves (e.g. ACT-R-like) | Forgetting as accessibility | Recency ranking visibly fails |
| Learned ranker | Fit `retrieval_score` | **Memory usefulness** labels exist (retrieve → action → outcome) |
| Graph / PPR | Multi-hop over D4 | Multi-hop queries actually occur |
| IB / biological attractors / fitted αβγ | — | **Do not build because a paper has an equation** |

“Not needed in the first adapter” ≠ “not part of human-inspired memory.”

**Embedding / dense retrieval trigger (any):** (1) logged paraphrase miss, (2) logged association failure (even at small N), (3) scale heuristic — **starting default** “low hundreds” of episodes, not a universal law (20 hard memories can be harder than 10k trivial ones), (4) **sunset:** N time units after skill install (default **90 days**) — decide to stay lexical **explicitly**, don’t default-forever.

Cloud vs local embeddings is an **adapter cost policy**, not a property of the memory model.

### 1.14 Risks (portable)

Hygiene: type drift, cue fan, duplicate source of truth, local state promoted to policy.  
Behavior: false generalization, false association, retrieval-induced bias, over-personalization, context-bound erasure.  
Epistemics: confidence inflation, reconsolidation corruption, **contamination** (untrusted write), **poisoning** (repetition of falsehoods), **authority collapse**.  
**Security:** secrets, PII, credentials — memory needs a **retention/redaction policy** (never commit secrets; purge or refuse).  
**INDEX/catalog fan:** when the catalog of subjects/collections makes selection ambiguous or measurably worse, partition it. A numeric default (e.g. ~20) is a **heuristic**, not a principle.

---

## Layer 2 — Memory skill (generic)

This layer is what a reusable skill should implement. Names in `<angle-brackets>` are adapter slots.

### 2.1 Lifecycle events (abstract)

| Event | Meaning | Typical adapter |
|---|---|---|
| `on_session_start` | New working context | inject catalog + accessible working state |
| `on_context_compact` | Working memory about to drop | mark unread experience for sweep; do not block compact |
| `on_turn_idle` | Agent finished a turn | sweep unread experience into the store |
| `on_consolidate` | Periodic integration | merge dupes, drop copies of external truth, do not auto-promote rules |

Loop limits and which model runs sweep vs consolidate are **adapter** choices.

### 2.2 Store interface

```text
MemoryStore
  write_episode(ep) -> id
  write_lesson(lesson) -> id
  write_status(status)          # volatile
  write_rule(rule) / write_pointer(ptr)
  link(from_id, rel, to_id)     # D4
  supersede(old_id, new_id, why)
  get_working()                 # accessible situation only
  get_candidates(cues)          # Stage A
  rank(candidates, context)     # Stage B
  retrieve(context, budget)     # A + B + optional budget
  validate(write) -> ok | errors  # deterministic, not LLM
```

Backends (files, SQLite, Postgres, Redis, objects, vectors) are adapters behind this interface.

### 2.3 Deterministic validation

**Requirement:** every write is checked by a **non-LLM** layer (schema, types, DB constraints, middleware — adapter choice). LLMs must not be the only categorizer.

Minimum checks: write type present; episode required fields; `status` not in the durable-policy collection; `pointer` does not contain a pasted external body; secrets redacted.

### 2.4 Episode schema (day-one format)

Persist **from day one** as structured records (YAML/JSON/table — adapter). Do **not** use freeform recap as the store.

**Required (small set — compliance risk if larger):**

- `id`, `time`, `what`, `source_type`, `confidence`

**Recommended:**

- `tags[]` (index labels, 0..N), `cause` (**hypothesis, separate from tags**), `entities[]`, `task`, `goal`
- `state_before`, `state_after` (or `context` + `outcome`)
- `next` (immediate one-off), `source_reliability`, `valid_at`
- `derived_lesson_id` (optional)

**Lesson record:** `id`, `gist`, `derived_from[]`, `tags[]`, `when` (condition), `exception_to?`, `confidence`. Created only per §1.6.

Canonical YAML shape (any equivalent encoding is fine):

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

### 2.5 Provenance on pointers and rules

```text
source_type, source_id, source_location, observed_at, validated_at, validated_by
gist: why this reference matters
```

Not all fields required. `user said` ≠ `agent inferred` ≠ `external spec`.

### 2.6 Working vs persistent backends

| Backend | Holds |
|---|---|
| Working | `status` / situation; TTL = inject cutoff |
| Persistent | episodes, lessons, rules, pointers, relationship edges, supersession chain |
| External | project source of truth |

### 2.7 Skill phases (generic)

| Phase | Name | Content |
|---|---|---|
| 0 | Model + hygiene | Types, episode format, validation, no copies of external truth, no status-as-policy |
| 1 | Persistence + working | Dual backends; TTL accessibility |
| 2 | Retrieval | Stage A/B; relationships; context-bounded rank |
| 3 | Learning | Lessons, conditional generalization, exceptions, approval to procedural |
| 4 | Adaptive | Dense `rel` if triggered; usefulness-trained ranker; accessibility curves |

Adapter mapping (Cursor, LangGraph, CrewAI, custom) belongs in that project’s Appendix, not here.

### 2.8 Memory usefulness (future measurement)

Log: `retrieved_ids` → `action` → `outcome` → `useful: yes/no/unknown`.  
This is the preferred target for a later ranker — more important than fitting αβγ.

### 2.9 Security policy (skill-required)

- Never persist secrets, credentials, or raw PII in durable memory.
- Untrusted sources cannot write `rule` or raise `authority`.
- Redact or refuse rather than “remember the password.”

---

## Layer 3 — Reference implementation

**This section is not portable.** It instantiates Layers 1–2 for one Cursor + markdown + Git workspace (AthletIQ). Other projects replace this appendix.

See **Appendix A**.

---

## Reviewer checklists

### Model (Layer 1) — Approve / Reject / Changes

1. Three objectives + conflict rule.  
2. Four dimensions; `episode` is a persisted write; `pointer` is external reference.  
3. Semantic ≠ pointer; internal gist allowed.  
4. Episode vs lesson boundary (§1.6).  
5. Cause ≠ tags.  
6. Three interference kinds including source/authority.  
7. Relationships including `exception_to`.  
8. Two-stage retrieval; multi-cue **approximates** completion.  
9. Provenance-preserving reconsolidation + supersession **chain**.  
10. Epistemic fields; context bounds; event vs fact.  
11. Usefulness as future metric; security policy.  
12. Exact-id recurrence named as policy departure.

### Skill (Layer 2)

1. Abstract lifecycle events.  
2. `MemoryStore` interface.  
3. Deterministic validation (non-LLM).  
4. Day-one structured episode format; **required field set is small**.  
5. Generic phases 0–4.  
6. Embedding trigger uses misses + heuristic scale + **N-day sunset after install**.  
7. Cloud/local embeddings left to adapter cost policy.

### Implementation (Layer 3 / Appendix A)

Approve only for **this** workspace’s adapter (hooks, markdown layout, Git ignore, local cost policy). Do not treat Appendix A as the skill.

**Out of scope:** product MVP, CI, model quality of any one app.

---

## Appendix A — Worked instance (Cursor / AthletIQ)

*Illustration only. Strip this when packaging the skill.*

| Portable concept | This workspace |
|---|---|
| Catalog | `memory/INDEX.md` |
| Persistent subjects | `memory/*.md`; durable policy in `## Must never miss` |
| Working backend | `memory/situation.md` (gitignored); TTL default 48h **arbitrary** |
| Sweep / consolidate | `on_turn_idle` → Composer 2.5; every 5 → Grok; `loop_limit: 2` |
| Lifecycle | Cursor `sessionStart` / `preCompact` / `stop` |
| Procedural | `.cursor/rules/*.mdc`, skills |
| External truth | `docs/` Approved |
| Validation | `scripts/validate_memory.py` (non-LLM; status-like lines in Must never miss, episode required fields, secret heuristics) |
| Cost policy **here** | Cursor models only; no extra embedding API unless owner changes it |

**Domain names** (CR-001, ADR-011, nba-stats, Sol, Compose, attest paths) are **examples of pointers/status**, not part of the memory model.

**Catalog heuristic here:** if INDEX exceeds ~20 lines *and* selection is ambiguous, group it. The principle is degradation, not the number 20.

**File mapping after Approve (this repo only):** standing gates stay thin rules + pointers into `docs/00-meta/gates.md`; clone gossip stays in situation; product locks are gist+pointer into PRD/SRS/ADR; TEST-010 vs NFR-001 vs TEST-013 stay as pointers to test docs.

**P0 in this adapter:** retag historical Must never miss; structured episode blocks in Notes; `scripts/validate_memory.py`; YAML blocks **are** the day-one store. Phase 1: `sessionStart` injects INDEX + TTL-filtered `memory/situation.md` (default 48h, arbitrary).

---

## References

**Human memory / cognitive science**  
Anderson (1974) fan effect; Watkins & Watkins (1975) cue-overload; McClelland, McNaughton & O’Reilly (1995) CLS; Marr (1971); O’Reilly & McClelland (1994); Yassa & Stark (2011) pattern separation; Taatgen & Anderson (2002) production compilation.

**Associative / retrieval theory**  
Amit, Gutfreund & Sompolinsky (1985) Hopfield capacity; Ramsauer et al. (2020) attention as one Hopfield step; McCloskey & Cohen (1989) catastrophic interference *(rejected as the mechanism here)*.

**AI agent memory systems**  
Park et al. (2023) Generative Agents; Gutiérrez et al. (2024) HippoRAG; MemGPT/Letta-style paging (archival vs core).

**Reliability**  
Write-gate, provenance, authority, and usefulness logging are engineering requirements of this spec, not citations of a single paper.

Working-tree canvases are not normative.
