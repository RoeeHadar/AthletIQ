# Infra architecture reference

## Owns

High-level topology in architecture docs: Compose services (etl, database, api), CI as quality gate, local-first deploy.

## Hand off

Detailed CI jobs, secrets wiring, observability stacks → **devops-operations** (`docs/09-devops/*`, `docs/10-operations/*`).

## Open hosting

Cloud deploy targets often need Grill-Me + ADR; do not invent a host.
