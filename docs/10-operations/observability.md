# Observability

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 0.2.0

## Intent

Health signals for ETL, API, and training jobs appropriate to a demo portfolio system. **NFR-004:** no hard latency or availability SLOs in MVP. Do not invent load-test targets.

## MVP

| Signal | Approach |
|---|---|
| API | `GET /v1/health` (503 when model or DB unavailable) |
| Pipeline / eval | Validation report + eval report artifacts; quality-gate vs execution-failure |
| Logs | Structured stderr via IMP-001 formatter (`docs/10-operations/logging.md`) |

No metrics backend (Prometheus, etc.) is required for MVP.

## Closed

- Metrics backend and SLOs — **not required** (NFR-004 / NFR-002). Health checks + logs are sufficient.

## Future (Gate 9 / post-MVP)

Optional metrics backend if a later CR introduces operational SLOs. Cloud deploy remains non-binding (ADR-007 Proposed).
