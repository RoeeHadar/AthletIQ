# Install phases (generic)

Ship the phase the user asked for. Later mechanisms stay in the model even when they are not in the first adapter.

| Phase | Name | Content |
|-------|------|---------|
| 0 | Model + hygiene | Types, episode format, validation, no copies of external truth, no status-as-policy |
| 1 | Persistence + working | Dual backends; TTL accessibility |
| 2 | Retrieval | Stage A/B; relationships; context-bounded rank |
| 3 | Learning | Lessons, conditional generalization, exceptions, approval to procedural |
| 4 | Adaptive | Dense `rel` if triggered; usefulness-trained ranker; accessibility curves |

## Phase 0 — required for any install

- Catalog + subject (or table) layout, or equivalent collections
- Write classification documented in always-on instructions
- Durable policy = `rule` + thin `pointer` only
- Episode structured records with required fields
- Non-LLM validator for the backend
- Security/redaction line in always-on instructions
- Encode gate: future behavior only; facts wait for confirm

**Definition of done:** `scripts/validate_memory.py` (markdown) exits 0 on a fixture or empty-but-valid store, **or** DB/schema constraints cover the same checks.

## Phase 1 — working memory

- Volatile situation/status store
- TTL removes from **automatic inject** (default duration is adapter-tunable and arbitrary until measured)
- `on_session_start` injects catalog + *accessible* working state (not expired)
- Working store not treated as history-never-existed; optional archive is fine
- VCS-ignore working + hook cursor files if Git is in use

## Phase 2 — retrieval

- Candidate generation from ids, entities, tags, cause, task, relationships
- Rank with importance ≠ relevance
- Budget/knapsack only if candidates overflow
- Multi-cue lexical/ID match **approximates** completion; do not claim paraphrase-complete recall
- Typed links can be stored as fields or a small edge list — not a graph product until Phase 4 needs it

## Phase 3 — learning

- Lesson records with `derived_from[]`
- Exact tag = strong **candidate**; overlap = weak; neither auto-compiles a rule
- `exception_to` as a first-class relationship
- Promotion to `rule` only after operator approval; prefer conditional rules
- Evidence diversity over raw repeat count

## Phase 4 — adaptive (opt-in)

Install **only** if a trigger in `spec.md` deferred table fired **and** the user opts in:

1. logged paraphrase miss
2. logged association failure (even at small N)
3. scale heuristic (starting default: low hundreds of episodes)
4. sunset: N days after install (default 90) — then explicitly keep lexical or add dense retrieval

Do not add extra paid APIs unless the cost-policy slot allows it.

## Suggested default for a new coding-agent repo

Phase **0+1**. Leave 2–4 as documented future work in the always-on rule (“do not use embeddings or decay math until triggers fire”).
