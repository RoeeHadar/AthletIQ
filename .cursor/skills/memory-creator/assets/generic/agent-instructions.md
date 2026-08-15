# Merge into AGENTS.md, a project rule, or the system prompt when the host has no IDE hooks.

## Memory (portable)

Load the memory catalog first (`memory/INDEX.md` or equivalent). Open only the subject files the current task needs. Never read the whole memory tree by default.

Save only what will change **future** behavior. Classify writes as `status` | `episode` | `lesson` | `rule` | `pointer`. Durable policy is `rule` + thin `pointer` only. Status belongs in the working backend and is not standing policy.

Episodes are structured records with `id`, `time`, `what`, `source_type`, `confidence`. `tags[]` is not `cause`. `episode.next` is a one-off for this event. Do not auto-write a lesson or rule.

Facts wait for user confirmation. Pointers gist+cite external truth; do not copy it. Do not persist secrets.

At end of turn, sweep unread experience into the store (or leave a pending flag if the host is about to compact). Periodic consolidate merges dupes and drops copies of external docs; it does not promote lessons to rules.
