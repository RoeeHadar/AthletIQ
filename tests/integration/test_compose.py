# TEST-010
"""TEST-010 — Compose deployment topology (not GHA)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "docker-compose.yml"


def test_compose_file_declares_architecture_topology() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    assert "profiles: [\"stub\"]" not in text
    assert "profiles: ['stub']" not in text

    for service in ("database:", "etl:", "api:"):
        assert service in text

    # Volumes: Postgres data + raw JSON (ADR-006) + artifacts (ADR-004)
    assert "raw_data:" in text or "raw_data" in text
    assert "artifacts:" in text
    assert "pgdata:" in text or "pgdata" in text

    # Postgres 16 (ADR-001)
    assert "postgres:16" in text

    # Localhost publish for demo API (ADR-009 / NFR-002)
    assert "127.0.0.1:8000:8000" in text

    assert (ROOT / "Dockerfile.etl").is_file()
    assert (ROOT / "api" / "Dockerfile").is_file()


def test_compose_config_validates() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker CLI not available")
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "config"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and (
        "Cannot connect" in (result.stderr or "")
        or "error during connect" in (result.stderr or "").lower()
        or "docker daemon" in (result.stderr or "").lower()
    ):
        pytest.skip(f"docker daemon unavailable: {result.stderr.strip()[:200]}")
    assert result.returncode == 0, result.stderr
    rendered = result.stdout
    assert "database" in rendered
    assert "etl" in rendered
    assert "api" in rendered
