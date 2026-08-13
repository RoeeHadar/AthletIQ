---
name: devops-operations
description: >-
  Draft or update CI/CD, infrastructure, deployment, observability, logging, and
  incident-response documentation. Use when defining GitHub Actions pipelines,
  Docker Compose topology, run_pipeline.sh behavior, deploy/rollback, metrics,
  health checks, structured logging, or operational runbooks.
---

# DevOps and operations

## Purpose

Own `docs/09-devops/*` and `docs/10-operations/*`, and keep machine stubs aligned at the **documentation** level (`docker-compose.yml`, `.github/workflows/*`) without implementing full application code.

## Progressive disclosure

Load only needed references:

- `references/ci-cd.md`
- `references/infrastructure.md`
- `references/deployment.md`
- `references/observability.md`
- `references/logging.md`
- `references/incidents.md`

## Grill-Me

Invoke **Grill-Me** for deploy/infra choices the SRS does not pin (hosting provider, registry, alert channels).

## Inputs (may read)

- SRS, architecture, design, test strategy
- glossary, id-registry

## Outputs (may modify)

- `docs/09-devops/ci-cd.md`
- `docs/09-devops/infrastructure.md`
- `docs/09-devops/deployment.md`
- `docs/10-operations/observability.md`
- `docs/10-operations/logging.md`
- `docs/10-operations/incident-response.md`
- Stub/config updates to `docker-compose.yml`, `.github/workflows/*` when documenting intent (no secret values)
- `docs/00-meta/glossary.md` as needed

## Must not touch

- ADR files (flag pending; use **architecture-decisions**)
- Charter/PRD/SRS primary authorship
- Application feature modules

## AthletIQ MVP CI path (from PRD)

```text
push → lint → unit → integration → Docker image build
```

Deploy after image build remains Open Question until decided.

## Validation

- [ ] Secrets guidance: env/repo secrets only
- [ ] CI path matches PRD or documents deviation via CR
- [ ] Grill-Me used for unresolved hosting/deploy choices
- [ ] Ops docs match solo-portfolio reality (no fake 24/7 NOC)

## Downstream

**engineering-review** checks docs vs actual workflows/compose for drift once implemented.
