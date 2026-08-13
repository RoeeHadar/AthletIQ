# TEST-011
"""TEST-011 — CI workflow topology (jobs + needs DAG; no live provider)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def _load_ci() -> dict:
    path = WORKFLOWS / "ci.yml"
    assert path.is_file(), "expected .github/workflows/ci.yml (ci-stub replaced)"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ci_stub_removed() -> None:
    assert not (WORKFLOWS / "ci-stub.yml").exists()


def test_ci_jobs_and_needs_dag() -> None:
    doc = _load_ci()
    jobs = doc["jobs"]
    required = {"lint", "unit", "integration", "image"}
    assert required <= set(jobs)

    # Parallel lint∥unit allowed; integration after both; image after integration.
    assert set(jobs["integration"].get("needs") or []) == {"lint", "unit"}
    assert set(jobs["image"].get("needs") or []) == {"integration"}


def test_ci_no_live_provider_requirement() -> None:
    text = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert "NFR-003" in text
    # Must not require a live API key secret for green builds.
    assert "secrets.API_SPORTS_KEY" not in text
    assert "api-sports.io" not in text.lower()
    # Fixture/offline intent for unit path.
    assert "fixture" in text.lower() or "no live" in text.lower()


def test_ci_secret_hygiene_checklist() -> None:
    text = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    # No hard-coded cloud API keys in workflow.
    for needle in ("sk-", "apikey=", "API_SPORTS_KEY: "):
        # Allow comments / empty env documentation, not literal secret values.
        if needle == "API_SPORTS_KEY: ":
            assert "API_SPORTS_KEY: ${{" not in text
            continue
        assert needle not in text
    assert "SEC-002" in text or "no API keys" in text.lower() or "secrets" in text.lower()


def test_ci_image_build_present() -> None:
    doc = _load_ci()
    steps = doc["jobs"]["image"]["steps"]
    joined = "\n".join(str(s.get("run", "")) for s in steps)
    assert "docker build" in joined
    assert "Dockerfile.etl" in joined
    assert "api/Dockerfile" in joined
