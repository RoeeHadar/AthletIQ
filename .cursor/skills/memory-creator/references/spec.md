# Layer 1 — Memory behavior

Portable contract. Host, file format, VCS, and product domain are **not** part of this layer.

## Three objectives

These pull in different directions. The contract is explicit.

| Objective | Optimizes for |
|-----------|----------------|
| **Hygiene** | Auditability, low interference, no duplicate source of truth, no stale local state as policy |
| **Behavior** | Encode experiences, retrieve from partial cues, generalize with evidence, reduce accessibility |
| **Epistemics** | Trust: source, authority, confidence, temporal validity, usefulness |

**Conflict rule:** hygiene + epistemics win for **standing policy** (rules, skills, published facts). Behavior may be richer for episodes, candidate generation, and ranking. Nothing associative auto-writes policy.

**Target:** human-inspired memory, subject to engineering reliability.

**Borrow:** episodic encoding, semantic abstraction, pattern separation, pattern completion (as a *behavioral* property), pattern integration, cue-driven recall, accessibility decay, provenance-preserving reconsolidation, context-bounded generalization.

**Reject:** confabulation-as-fact; unverified generalization into policy; silent rule flips; salience as emotional valence (here salience = impact / prediction-error / explicit mark); biological attractor simulation; fitted neuroscience equations without a measured target.

**Invariant:** store **what changes future behavior**, not what merely contains information. Authoritative external knowledge stays in the project's source-of-truth store. Memory **points** or **gists**; it does not fork that store.

## Four independent dimensions

Do not collapse these.

**D1 — Representation:** working (transient) · episodic (one event) · semantic (generalized knowledge) · procedural (how to act)

**D2 — Persistence:** volatile · persistent · external (owned outside the memory store)

**D3 — Write classification:** `status` | `episode` | `lesson` | `rule` | `pointer`

`episode` **is** a persisted write type. `pointer` is a **reference mechanism** to external knowledge, not a fourth representation.

Semantic memory is **not** “pointer + gist.” It is internally learned gist, optionally anchored via `pointer`.

**D4 — Relationships** (typed links by id; need not be a graph DB):

`derived_from` | `supports` | `contradicts` | `exception_to` | `generalizes` | `similar_to` | `same_cause` | `same_situation` | `same_entity` | `same_strategy` | `same_outcome` | `supersedes` | `caused_by`

Recurrence is one relationship (`same_cause` / `similar_to`), not the whole association model.

## Interference (three kinds)

| Kind | Failure | Hygiene response |
|------|---------|------------------|
| **Retrieval** | Too many items share one cue (fan / cue overload) | Split cues; don't dump everything into one “never miss” bucket |
| **Representation** | Distinct events collapsed onto one label | Keep episodes distinct; don't equate tag with cause |
| **Source / authority** | User assertion, agent inference, hallucination, and external docs treated as equal | Provenance + authority; never let association erase source |

Retrieval interference is *not* catastrophic interference in trained weights.

## Lifecycle

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

## Encode when future behavior may change

Not only failure and decision. Encode an **episode** when the event is expected to influence future behavior, including: failure, success, decision, correction, discovery, preference, constraint, commitment, unexpected observation, plan outcome, environmental change, resolved ambiguity.

**Event vs fact:** “User asked for concise answers on date T” is an episode. “User prefers concise answers” is semantic, promoted only with repeated evidence and context bounds. One day's request must not become a standing preference.

**Context specificity:** “Strategy X worked in context A and failed in context B” must not collapse to “strategy X works” unless evidence supports erasing the bound.

## Episode vs lesson

| | Episode | Lesson |
|---|---|---|
| What | Experiential record of **one** event | Durable **cross-session gist** from one or more episodes |
| Immediate action | `episode.next` = one-off for **this** event | Lesson body = what the **next** agent should generally remember |
| When to write | At encode time, when the encode gate fires | When a human confirms it is worth generalizing, **or** a relationship flags a candidate and an operator accepts a gist — **not** automatically on first episode |
| Policy? | Never | Still not a `rule`. Promotion to `rule` requires approval |

If you only store `episode.next`, you have a to-do. If you only store a lesson, you have lost the event.

## Pattern trio

| Operation | Property | Honest v1 mechanism |
|-----------|----------|---------------------|
| **Separation** | Similar events stay distinct | Separate episode records; timestamps; tags ≠ cause |
| **Completion** | Partial cues surface related priors | **Approximated** by multi-cue exact/ID/keyword match. That is **not** paraphrase-complete |
| **Integration** | Several episodes become one abstraction | Lesson / semantic gist with `derived_from` + evidence; not a merge that deletes episodes |

## Recurrence, promotion, exceptions

**Exact id/tag match is a deliberate departure from human-like generalization** for **policy**. It is the strongest recurrence *signal*, not the definition of “I've seen this kind of problem.”

| Signal | May write a `rule`? |
|--------|---------------------|
| Exact tag / id (`same_cause` strong) | No — candidate |
| Shared entity / task / context | No |
| Semantic / paraphrase overlap | No |
| Operator approval | **Yes** |

**Invariant:** similarity may retrieve; similarity does not establish causality or policy.

**Promotion:** prefer **conditional** knowledge (“when Y, do X”) over universals. Evidence strength should consider **context diversity** and **source quality**, not only count.

**Exception (operational):**

```text
general:      when Y, do X
exception_to: <id>
when:         Z
evidence:     episode_ids[]
```

## Retrieval: two stages

**Stage A — candidate generation** (“could this possibly be relevant?”): exact ids, entities, tags, cause, task, temporal neighborhood, typed relationships.

**Stage B — candidate evaluation** (“how useful for *this* situation?”): relevance, confidence, source reliability, recency/accessibility, salience (impact, not affect), context fit. **Importance ≠ relevance.**

Context **budgeting** happens **after** A and B, only if the candidate set overflows. Any `recency × importance × rel` product is a **placeholder**, not a fitted model.

## Provenance-preserving reconsolidation

retrieve → use → if evidence conflicts, write a **new** episode (and `supersedes`), **do not silently mutate** the old episode's factual fields. Keep a recoverable supersession chain. Normal retrieval exposes the current interpretation; audit can walk the chain.

## Epistemics

| Field | Meaning |
|-------|---------|
| `source_type` | `user` \| `observation` \| `inference` \| `external` \| `derived` |
| `source_reliability` | Trust in that class of source in this project |
| `confidence` | How strongly this record claims the proposition (**not** raised by rewrite count) |
| `valid_at` / `last_verified` | Temporal validity |
| `authority` | e.g. user instruction > approved external spec > agent inference > unconfirmed observation |

A high-confidence **false observation** is still an observation.

## Forgetting

- **Working / situation:** TTL (adapter-tunable; any numeric default is arbitrary) removes from **automatic inject**. Optional archive. Not “never existed.”
- **Long-term:** reduced **accessibility** (rank), not deletion, unless security/retention requires purge.

## Deferred (not rejected)

| Mechanism | Build when |
|-----------|------------|
| Embedding / dense `rel` | Logged paraphrase miss, logged association failure, scale heuristic (“low hundreds” of episodes — not a law), **or** sunset N days after install (default **90**) — then decide to stay lexical **explicitly** |
| Accessibility curves | Recency ranking visibly fails |
| Learned ranker | **Memory usefulness** labels exist (retrieve → action → outcome) |
| Graph / PPR | Multi-hop queries actually occur |

Do **not** build IB / biological attractors / fitted αβγ because a paper has an equation.

Cloud vs local embeddings is an **adapter cost policy**, not a property of the model.

## Risks

Hygiene: type drift, cue fan, duplicate source of truth, local state promoted to policy.  
Behavior: false generalization, false association, retrieval-induced bias, over-personalization, context-bound erasure.  
Epistemics: confidence inflation, reconsolidation corruption, contamination, poisoning, authority collapse.  
Security: see `security.md`.  
Catalog fan: when the catalog makes selection ambiguous or measurably worse, partition it. A numeric default (e.g. ~20) is a heuristic, not a principle.
