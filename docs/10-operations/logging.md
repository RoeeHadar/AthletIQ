# Logging

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 0.2.0

## Intent

Structured logging across ETL and API; `scripts/run_pipeline.sh` writes logs and reports failures (OPS-002). Never log secrets (SEC-001).

## Current (IMP-001)

Module: `src/athletiq/logging/`.

- Stream handler, ISO-like timestamp: `%(asctime)s %(levelname)s [%(name)s] %(message)s` with `datefmt=%Y-%m-%dT%H:%M:%S`.
- Secret redaction filter replaces known secret substrings with `***REDACTED***`.
- Logger name default: `athletiq`; `propagate=False`.

This is the MVP format. Correlation IDs and log retention are **Gate 9 leftovers** — not open product questions blocking Gate 6.

## Open (Gate 9 / non-blocking)

- Correlation IDs across pipeline stages and API requests.
- Log file retention on the host / Compose volume.
