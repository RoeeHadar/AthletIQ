---
name: testing
description: >-
  Draft or update test strategy and requirement-driven test plans. Use when defining
  unit, integration, pipeline, or CI test approach, writing TEST-XXX cases from the
  SRS, mapping tests to requirements, or clarifying ML evaluation versus baseline.
---

# Testing

## Purpose

Requirement-driven verification docs: `test-strategy.md` + `test-plan.md`. Tests derive from SRS, not merely from existing code.

## Grill-Me

Invoke **Grill-Me** when test scope is ambiguous (performance load, how much API mocking, acceptance thresholds not in SRS).

## Inputs (may read)

- SRS, traceability, architecture, design, implementation plan
- glossary, id-registry

## Outputs (may modify)

- `docs/08-testing/test-strategy.md`
- `docs/08-testing/test-plan.md`
- `docs/00-meta/id-registry.md` (`TEST-`)
- Traceability **Test** column updates

## Must not touch

- Production application feature code (test code may be planned; writing tests is OK only when implementation gate allows — this skill prefers documenting plan first)
- ADR authorship
- Inventing requirements to “have something to test”

## Procedure

1. Read SRS + implementation plan testing requirements.
2. Strategy: levels, principles, tooling stance (or Open Question).
3. Plan: one TEST-XXX per acceptance criterion cluster; link requirement ids.
4. Grill-Me ambiguous scope.
5. Update traceability.

## Validation

- [ ] No orphan tests without requirement links where applicable
- [ ] Must requirements in scope have planned coverage or explicit risk acceptance
- [ ] TEST ids registered
- [ ] ML baseline comparison called out if ML requirements exist

## Downstream

**devops-operations** wires CI to run the planned suites.
