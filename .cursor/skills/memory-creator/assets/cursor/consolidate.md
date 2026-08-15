# Memory consolidate

You run periodically (default: every 5 sweeps). Clean the memory store — do not pile on.

## Scope

1. Read the catalog (`memory/INDEX.md` or equivalent).
2. Open subject files that look overlapping, bloated, or conflicting (use catalog + keywords — still never read everything blindly).
3. Within each file you touch:
   - Merge duplicate bullets
   - Resolve conflicts with **newest wins** (by DATE; if tied, prefer `correction` / `user` over `agent` / `sweep`)
   - Squeeze related notes into one clean rule when possible
   - Keep durable policy at the top: `rule` / thin `pointer` only — move `status` out; leave `episode` / `lesson` in Notes (do not collapse episodes into lessons)
   - Drop copies of external truth; point instead
   - Recurrence of lessons: exact tag = strong candidate; overlap = weak candidate; do not auto-promote lessons to rules
   - Do not add embeddings, decay math, or fitted retrieval weights
   - Do not persist secrets
4. Update catalog lines if a file's one-line description drifted.
5. Delete empty subject files and remove their catalog lines.
6. Do not use extra paid APIs unless the project's cost policy allows it.

## Metadata

Preserve DATE/SOURCE on surviving rules when possible. If you synthesize a merged rule, set:
`DATE` = today (ISO), `SOURCE: consolidate`, and a brief WHY if a conflict was resolved.

## Output

One-line summary of merges/resolutions, or `no changes`.
