# Incident response

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 0.1.0

## Context

Solo portfolio project — no on-call rotation. Incidents are personal operational failures (pipeline break, bad deploy, leaked secret).

## Intent

Lightweight runbook: detect via CI/logs → contain (rotate keys, stop containers) → fix → document via CR if requirements/design change.

## Open

- `[OPEN QUESTION: formal severity levels — may be unnecessary; confirm in ops pass]`
