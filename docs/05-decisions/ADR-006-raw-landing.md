# ADR-006: Immutable raw JSON filesystem landing

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 1.1.0

Decision status: Accepted

## Context

Need replayability without ambiguous “filesystem or Postgres raw schema”. Owner review preferred filesystem raw for MVP.

## Decision

- Persist provider payloads as **immutable JSON files** under a raw landing directory/volume.  
- After a successful write, raw objects are **not updated in place** (new fetch = new batch path).  
- Transform reads raw → loads **curated PostgreSQL** only. No PostgreSQL `raw_*` schema in MVP.

## Alternatives considered

- Raw tables in PostgreSQL — valid but heavier for opaque payloads  
- Transform-only (no raw) — weaker replay/debug  
- Both FS + DB raw — unnecessary duplication for MVP

## Consequences

- Compose mounts a raw volume into the etl service.  
- Reprocessing can run without re-calling API-Sports.  
- **Prune policy (design):** delete obsolete season batches / dedupe / drop noisy — do not mutate JSON in place. Active window = 2–3 completed seasons (“too old” outside that window).

## References

- Related requirements: FR-001, FR-013, DR-001, DR-002  
- Related architecture docs: `data-architecture.md`  
- Owner architecture review; design Grill-Me Q4 (2026-08-12)
