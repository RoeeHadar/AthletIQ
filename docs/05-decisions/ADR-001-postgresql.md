# ADR-001: PostgreSQL as system of record

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 1.0.0

Decision status: Accepted

## Context

CON-002 requires a relational SQL system of record supporting analytics and window functions (FR-003). Engine was not named in the SRS.

## Decision

Use **PostgreSQL 16** (or current stable 16.x patch) as the MVP database engine inside Docker Compose.

## Alternatives considered

- SQLite — simpler, weaker concurrent story for API+ETL
- MySQL/MariaDB — adequate SQL, weaker fit for our window-function examples and Compose defaults in this project
- Managed cloud SQL from day one — out of MVP scope

## Consequences

- Schema/migrations target PostgreSQL dialect.
- Compose `database` service uses official Postgres image.
- Post-MVP GCP may move to Cloud SQL for PostgreSQL (ADR-007) without changing logical model.

## References

- Related requirements: CON-002, FR-002, FR-003, DR-002  
- Related architecture docs: `system-architecture.md`, `data-architecture.md`  
- Grill-Me architecture Q1 (2026-08-12)
