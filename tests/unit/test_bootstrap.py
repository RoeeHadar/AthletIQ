# TEST-001
"""TEST-001 — bootstrap, config, logging, secrets."""

from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path

import pytest

from athletiq.config import Settings, load_settings
from athletiq.logging import configure_logging, redact_text

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / ".env.example"


def test_load_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/db")
    monkeypatch.setenv("API_SPORTS_KEY", "test-key-not-real")
    monkeypatch.setenv("ATHLETIQ_SEED", "7")
    monkeypatch.setenv("ATHLETIQ_RAW_PATH", "tmp/raw")
    monkeypatch.setenv("ATHLETIQ_ARTIFACTS_PATH", "tmp/artifacts")
    monkeypatch.setenv("ATHLETIQ_LOG_LEVEL", "DEBUG")

    settings = load_settings()
    assert settings.database_url.startswith("postgresql://")
    assert settings.api_sports_key == "test-key-not-real"
    assert settings.seed == 7
    assert settings.raw_path == Path("tmp/raw")
    assert settings.artifacts_path == Path("tmp/artifacts")
    assert settings.log_level == "DEBUG"


def test_settings_expose_nfr001_knobs() -> None:
    settings = Settings(
        database_url="postgresql://localhost/db",
        api_sports_key=None,
        seed=42,
        raw_path=Path("data/raw"),
        artifacts_path=Path("artifacts"),
        log_level="INFO",
    )
    assert isinstance(settings.seed, int)
    assert settings.raw_path.name == "raw"
    assert settings.artifacts_path.name == "artifacts"


def test_env_example_placeholders_only() -> None:
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert "API_SPORTS_KEY=" in text
    assert "DATABASE_URL=" in text
    assert "ATHLETIQ_SEED=" in text
    assert "ATHLETIQ_RAW_PATH=" in text
    assert "ATHLETIQ_ARTIFACTS_PATH=" in text
    # No live-looking secrets
    assert "SUPER_SECRET_TEST_VALUE" not in text
    for line in text.splitlines():
        if line.startswith("API_SPORTS_KEY="):
            assert "CHANGE_ME" in line or line.endswith("=")
        if line.startswith("DATABASE_URL="):
            assert "CHANGE_ME" in line or "localhost" in line


def test_sentinel_secret_redacted_from_logs() -> None:
    sentinel = "SUPER_SECRET_TEST_VALUE"
    stream = StringIO()
    logger = configure_logging(level="INFO", secrets=[sentinel], logger_name="athletiq.test.redact")
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(logger.handlers[0].filters[0])
    logger.handlers.clear()
    logger.addHandler(handler)

    logger.info("connecting with key=%s", sentinel)
    logger.error("failed: %s", sentinel)

    try:
        raise RuntimeError(f"provider error key={sentinel}")
    except RuntimeError:
        logger.exception("retry exhausted")

    out = stream.getvalue()
    assert sentinel not in out
    assert "REDACTED" in out


def test_redact_text_helper() -> None:
    sentinel = "SUPER_SECRET_TEST_VALUE"
    assert sentinel not in redact_text(f"oops {sentinel}", [sentinel])
