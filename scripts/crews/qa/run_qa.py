"""Deterministic QA runner for Approved TEST-001…019.

CrewAI YAML under config/ describes the workforce. This script is the
executor (no live LLM, no live API-Sports). NFR-003.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAP_PATH = Path(__file__).resolve().parent / "test_map.json"

# SRS Musts from docs/03-requirements/traceability.md (CR-004-amended).
MUST_TO_TESTS: dict[str, list[str]] = {
    "FR-001": ["TEST-003"],
    "FR-002": ["TEST-002", "TEST-004"],
    "FR-003": ["TEST-005"],
    "FR-004": ["TEST-006"],
    "FR-005": ["TEST-007"],
    "FR-006": ["TEST-007"],
    "FR-007": ["TEST-007"],
    "FR-008": ["TEST-007"],
    "FR-009": ["TEST-008"],
    "FR-010": ["TEST-012"],
    "FR-011": ["TEST-009"],
    "FR-012": ["TEST-010"],
    "FR-013": ["TEST-004"],
    "FR-014": ["TEST-008", "TEST-014"],
    "FR-015": ["TEST-008", "TEST-019"],
    "FR-016": ["TEST-015"],
    "FR-017": ["TEST-016"],
    "FR-018": ["TEST-017"],
    "FR-019": ["TEST-018"],
    "FR-020": ["TEST-008"],
    "DR-001": ["TEST-003", "TEST-004", "TEST-015"],
    "DR-002": ["TEST-002", "TEST-004", "TEST-015"],
    "DR-003": ["TEST-004", "TEST-016", "TEST-017"],
    "DR-004": ["TEST-017"],
    "ML-001": ["TEST-006"],
    "ML-002": ["TEST-006", "TEST-007"],
    "ML-003": ["TEST-007"],
    "ML-004": ["TEST-007"],
    "ML-005": ["TEST-007"],
    "ML-006": ["TEST-007"],
    "ML-007": ["TEST-007"],
    "ML-008": ["TEST-006"],
    "ML-010": ["TEST-007", "TEST-018"],
    "ML-011": ["TEST-006", "TEST-016"],
    "ML-009": ["TEST-007", "TEST-013", "TEST-014"],
    "SEC-001": ["TEST-001", "TEST-003"],
    "SEC-002": ["TEST-001", "TEST-011"],
    "NFR-001": ["TEST-001", "TEST-013"],
    "NFR-002": ["TEST-008"],
    "NFR-003": ["TEST-011"],
    "NFR-004": ["TEST-008"],
    "NFR-005": ["TEST-002"],
    "OPS-001": ["TEST-011"],
    "OPS-002": ["TEST-001", "TEST-009"],
    "CON-001": ["TEST-001", "TEST-009"],
    "CON-002": ["TEST-002"],
    "CON-003": ["TEST-010"],
    "CON-004": ["TEST-008"],
    "CON-005": ["TEST-011"],
    "CON-006": ["TEST-009"],
    "CON-007": ["TEST-003"],
    "CON-008": ["TEST-007"],
    "CON-009": ["TEST-017", "TEST-019"],
}

ATTESTATION_NOT_CLOSED_BY_PYTEST = {
    "NFR-001": "clean-machine Compose path — attested 2026-08-14 (not pytest)",
    "DR-001": "two completed live NBA seasons — owner-reported local 2026-08-14 (not pytest; not PRD-ticked)",
    "ML-005": "frozen real holdout — owner-reported local 2026-08-14 (TEST-007 remains synthetic; not PRD-ticked)",
    "OPS-001": "remote GitHub Actions green — attested 491c5c0 run 31913410157 (not pytest)",
    "CON-005": "remote GitHub Actions green — same as OPS-001 (not pytest)",
}


def audit_coverage() -> list[str]:
    holes = [rid for rid, tests in MUST_TO_TESTS.items() if not tests]
    print("=== coverage_auditor ===")
    print(f"Must requirements mapped: {len(MUST_TO_TESTS)}")
    print(f"Holes (Must with no TEST id): {holes or 'none'}")
    print("Attestation gaps (not pytest closeouts):")
    for rid, why in ATTESTATION_NOT_CLOSED_BY_PYTEST.items():
        print(f"  {rid}: {why}")
    return holes


def run_suite(test_id: str, paths: list[str]) -> tuple[int, str]:
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=line", *paths]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={k: v for k, v in __import__("os").environ.items() if k != "API_SPORTS_KEY"},
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def main() -> int:
    mapping = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    holes = audit_coverage()
    print("\n=== qa_runner ===")
    failed: list[str] = []
    for entry in mapping["tests"]:
        tid = entry["id"]
        code, out = run_suite(tid, entry["paths"])
        last = out.splitlines()[-1] if out else "(no output)"
        status = "PASS" if code == 0 else "FAIL"
        if code != 0:
            failed.append(tid)
        print(f"{tid}: {status} — {last}")
        if code != 0:
            print(out[-2000:])
    print("\n=== verdict ===")
    if holes:
        print("REJECT: SRS Must without TEST id")
        return 2
    if failed:
        print("REJECT: " + ", ".join(failed))
        return 1
    print("ACCEPT: TEST-001…019 pytest green (skips inside suites still honest)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
