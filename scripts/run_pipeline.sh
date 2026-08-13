#!/usr/bin/env bash
# Implements: FR-011, CON-006, OPS-002, ADR-005
# Thin entry → Python orchestrator (ADR-005). No stage logic in bash.
# Compose/demo e2e: explicitly select Postgres store (DATABASE_URL = connection only).
# Developer CLI default remains memory: `python -m athletiq.pipeline` (no --store).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "warn: DATABASE_URL unset; --store postgres will fail until set" >&2
fi

# Pass through user args after explicit demo store selection.
exec python -m athletiq.pipeline --store postgres "$@"
