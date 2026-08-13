# ADR-010: BIGINT / BIGSERIAL surrogate keys

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.0

Decision status: Accepted

## Context

Gate 4 database design and `database/schema.sql` already used **BIGINT / BIGSERIAL** for curated surrogate keys (`game_id`, `team_id`, `player_id`), with the API exposing `game_id` as a decimal string (ADR-008). Downstream IMP-002 / TEST-002 asserted BIGINT, but no ADR recorded the identity-type choice — risking apparent drift vs older UUID/serial sketches. This ADR locks the decision formally.

## Decision

- Curated surrogate primary keys (`game_id`, `team_id`, `player_id`, and FKs to them) are **BIGINT**, typically allocated as **BIGSERIAL**.  
- **Not UUID** for MVP internal ids.  
- HTTP/OpenAPI continue to pass `game_id` as a **decimal string** of that BIGINT (ADR-008).  
- Provider natural keys remain separate `provider_*` TEXT (or equivalent) columns.

## Alternatives considered

- UUID PKs — larger indexes; awkward decimal-string API; no MVP need for distributed id generation  
- Plain INTEGER/SERIAL — sufficient today but tighter headroom for provider-scale ids and future merges  
- Provider id as sole PK — couples curated grain to vendor; harder idempotent remapping

## Consequences

- `database/schema.sql`, migrations, IMP-002, and TEST-002 must assert BIGINT-compatible types.  
- API clients must not assume UUID format.  
- Changing to UUID later requires a CR + schema migration + OpenAPI change.

## References

- Related requirements: FR-002, FR-009, DR-002, ADR-001, ADR-008  
- Related design: `docs/06-design/database-design.md`, `docs/06-design/api-design.md`  
- Contract: `database/schema.sql`  
- Gate 4 design approval (2026-08-12); formalized 2026-08-13 after test-plan drift review
