# ADR-009: No authentication on MVP demo API

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.1.0

Decision status: Accepted

## Context

PRD/API non-goals exclude paid accounts and multi-tenant SaaS. Shipping `/v1/predict` with zero auth is an exposure decision, not merely “not built yet.”

## Decision

MVP FastAPI has **no application-level authentication/authorization**. Safety assumption: service is bound for **local demo** (Docker Compose / localhost), per NFR-002 and architecture trust boundaries — not a public internet multi-tenant deployment.

## Alternatives considered

- API keys / basic auth in MVP — extra scope without a paid-user product  
- Put behind a gateway now — no cloud CD in MVP  
- Leave auth as silent omission — rejected; must be an explicit decision

## Consequences

- Docs must not imply production-public exposure without a CR + auth ADR.  
- Post-MVP cloud deploy (Gate 8) must revisit auth before public bind.  
- Pick-a-demo-user (`?user=`) is **not** authentication (CR-005 / ADR-014).

## References

- NFR-002, FR-009, CON-004  
- `api-design.md`, `api-architecture.md`  
- Design review 2026-08-12
