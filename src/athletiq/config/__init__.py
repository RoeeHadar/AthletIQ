# Implements: SEC-001, SEC-002, NFR-001, CON-001
"""Environment-backed settings (secrets never hard-coded)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables only."""

    database_url: str
    api_sports_key: str | None
    seed: int
    raw_path: Path
    artifacts_path: Path
    log_level: str

    def secret_values(self) -> tuple[str, ...]:
        """Values that must never appear in logs or error text."""
        secrets: list[str] = []
        if self.api_sports_key:
            secrets.append(self.api_sports_key)
        # Avoid logging full DB URLs that embed passwords.
        if self.database_url and "://" in self.database_url:
            secrets.append(self.database_url)
            # Also redact password segment if present: scheme://user:pass@host
            try:
                after_scheme = self.database_url.split("://", 1)[1]
                if "@" in after_scheme and ":" in after_scheme.split("@", 1)[0]:
                    userinfo = after_scheme.split("@", 1)[0]
                    password = userinfo.split(":", 1)[1]
                    if password:
                        secrets.append(password)
            except (IndexError, ValueError):
                pass
        return tuple(s for s in secrets if s)


def load_settings() -> Settings:
    """Load settings from the process environment.

    Required for a full pipeline later: DATABASE_URL.
    API_SPORTS_KEY is optional until live ingest (fixtures need none).
    """
    database_url = _env("DATABASE_URL", "postgresql://athletiq:athletiq@localhost:5432/athletiq")
    assert database_url is not None
    seed_raw = _env("ATHLETIQ_SEED", "42")
    assert seed_raw is not None
    raw = _env("ATHLETIQ_RAW_PATH", "data/raw")
    artifacts = _env("ATHLETIQ_ARTIFACTS_PATH", "artifacts")
    log_level = _env("ATHLETIQ_LOG_LEVEL", "INFO")
    assert raw is not None and artifacts is not None and log_level is not None

    return Settings(
        database_url=database_url,
        api_sports_key=_env("API_SPORTS_KEY"),
        seed=int(seed_raw),
        raw_path=Path(raw),
        artifacts_path=Path(artifacts),
        log_level=log_level.upper(),
    )
