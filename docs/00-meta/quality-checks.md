# Documentation quality checks

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 0.1.0

Run at setup checkpoints, before Approving a gate package, and via the **engineering-review** skill on an ongoing basis.

## Checklist

- [ ] No broken internal references (paths, ADR ids, requirement ids)
- [ ] No missing requirement IDs in prose that claims to cite them
- [ ] Every requirement has acceptance criteria **or** an explicit `[OPEN QUESTION]`
- [ ] Every architecture component lists responsibilities
- [ ] Requirements in scope are covered by architecture (or gap flagged)
- [ ] Decisions have rationale; **Accepted** ADRs have consequences documented
- [ ] Design elements have upstream justification (PRD/SRS/architecture)
- [ ] Tests map to requirements where applicable (and vice versa for Must items)
- [ ] No contradictions between documents
- [ ] `Last Updated` / `Version` metadata present and not stale relative to known edits
- [ ] No duplicate definitions of the same concept across Charter/PRD/SRS
- [ ] Terminology defined in `glossary.md` when used in multiple docs
- [ ] Charter vs PRD boundary respected (no feature/user content in Charter; no sponsorship essay in PRD)
- [ ] Code listed in Implementation Plan “Files/modules affected” has `# Implements: FR-XXX` (when code exists)
- [ ] Design / contract / implementation triple agrees (else drift defect)
- [ ] No invented metrics, users, or constraints presented as Known
- [ ] Placeholders only appear after Grill-Me could not resolve (or user deferred)

## Anti-over-engineering (§23)

Do not: create unnecessary documents, duplicate information, invent requirements or ADRs, invent fake metrics/users/scalability targets, or fill unknowns with assumptions presented as fact.

Always distinguish: Known / Assumption / Decision / Open Question / Future Consideration.

## Ownership

`engineering-review` reports failures against this list; owning skills apply fixes.
