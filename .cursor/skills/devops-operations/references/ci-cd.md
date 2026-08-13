# CI/CD reference

## Doc

`docs/09-devops/ci-cd.md` + `.github/workflows/*`

## MVP

lint → unit → integration → Docker build. No secrets in repo.

## Post-MVP

Deploy job only after host/registry decided (Grill-Me + ADR if material).
