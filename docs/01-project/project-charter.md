# Project Charter — AthletIQ

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

> Organizational / sponsorship / portfolio view. Product capabilities and users: `docs/02-product/PRD.md`.  
> Deliberate **technical constraints** for the portfolio live here so the PRD can stay product-shaped.

## Purpose

**Project purpose:** Build a credible portfolio project demonstrating end-to-end data, ML, software, and DevOps engineering — with decisions derived from documentation **before** implementation.

**Product purpose** (owned by the PRD, summarized only): Provide a system that ingests NBA data, analyzes historical performance, and serves ML-based game-outcome predictions through an API.

## Vision

A reproducible, well-documented reference system that a technical reader can clone, run locally, and inspect from data intake through evaluated predictions — evidencing breadth (data → ML → API → DevOps) and depth (analytics, honest evaluation, from-scratch NN as stretch).

## Objectives

1. Establish living engineering documentation and gates so build work follows approved design.
2. Deliver a working local demo that trains/evaluates models and serves pre-game win/lose predictions.
3. Keep the repository GitHub-publishable: CI green, secrets via environment only, clear README and docs.
4. Demonstrate the constrained technology families listed under Constraints (educational / portfolio requirements).

## Stakeholders

| Role | Who | Accountability |
|---|---|---|
| Sponsor / owner | Project owner (sole) | All product, technical, and publish decisions |

No other organizational stakeholders. Known (Grill-Me). Product users and artifact audience are defined in the PRD (not duplicated here).

## High-level scope

**In scope (effort boundary):** documentation lifecycle; NBA data ingestion from an external provider; relational storage and SQL analytics; feature engineering; ML win/lose prediction (baseline + LR + XGBoost in MVP; NumPy NN documented as stretch); demo HTTP API; containerized local multi-service deployment; CI through image build; shell pipeline orchestration.

**Out of scope (effort boundary):** commercial productization, multi-tenant operations, betting products, mobile clients, production ML ops platforms. Detail in PRD non-goals.

## Constraints

Portfolio **must-demonstrate** technical constraints (intentional; to be minted as `CON-` in SRS and refined by ADRs where alternatives exist):

| Constraint | Intent |
|---|---|
| Python-based ETL | API requests, pagination, JSON parsing, validation, error handling, logging, env-based config |
| Relational store with SQL analytics | Including aggregations and window functions over team/game stats (player-grain tables may exist as reserved schema — CR-001) |
| Containerized local deployment | Multi-service local topology (ETL, database, API); **Docker Compose is the expected MVP realization** unless an ADR supersedes |
| HTTP prediction API | Demo-grade serving of predictions (**FastAPI** expected MVP realization unless ADR supersedes) |
| CI on GitHub Actions | Path: lint → unit → integration → image build |
| Linux orchestration script | `scripts/run_pipeline.sh`: env check, migrations, ETL, validation, logs, failure reporting |
| External NBA data provider | Discovery selection: **API-Sports NBA** (free tier class); record final choice + rationale in an ADR; keep an adapter boundary so the provider can be replaced |
| ML MVP model families | Baseline + **logistic regression** + **XGBoost** on the same holdout (see PRD); NumPy-from-scratch NN is post-MVP stretch |

Still open from discovery:

- Additional hard constraints (budget, compliance, deadlines): `[OPEN QUESTION: none confirmed beyond portfolio must-demonstrate list above]`
- Deploy/CD target after image build: `[OPEN QUESTION]`

## Known assumptions

- API-Sports NBA free-tier quotas are sufficient for MVP historical depth of 2–3 seasons with careful pagination/caching. `[ASSUMPTION — needs confirmation]`
- Solo maintenance indefinitely is acceptable for portfolio scope. Known (Grill-Me).

## Success criteria

Organizational / publish bar (product metrics detail in PRD):

- Documentation through implementation plan can be driven to Approved before non-trivial coding
- One-command / scripted local demo path works on a clean machine
- CI: lint → unit → integration → image build
- Model evaluation reported vs an approved baseline (methodology in ML design)
- No secrets committed
- Portfolio constraints above are demonstrably exercised in the shipped artifact

## Major milestones

| Milestone | Meaning |
|---|---|
| M0 | Engineering docs/skills/gates scaffolding complete |
| M1 | Charter + PRD Approved |
| M2 | SRS + architecture + ADRs + design + test strategy + implementation plan Approved |
| M3 | MVP slice meets PRD acceptance criteria |
| M4 | Post-MVP items per PRD roadmap (documented; built when chosen) |

Exact dates: `[OPEN QUESTION: schedule not set]`.

## Risks

| Risk | Notes |
|---|---|
| Provider throttling / season limits | May slow or shrink training data |
| Treating discovery stack as unexamined “architecture” | Mitigate via ADRs for provider, Compose vs alternatives, serving stack |
| Scope creep into productization or production ML ops | PRD non-goals + gates; CRs required |
| Docs drift from code | `engineering-review` + design/contract/implementation triple |

## Source

Grill-Me Rounds 1–4 (2026-08-12); aligned with PRD v0.2 revision (2026-08-12). Product detail: `docs/02-product/PRD.md`.
