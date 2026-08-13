# Implements: FR-001, SEC-001, ADR-002 — live HTTP adapter (not used in CI)
"""API-Sports NBA client with retries. Key from env only."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlencode

from athletiq.provider.retry import parse_retry_after, retry_with_backoff

DEFAULT_BASE = "https://v1.basketball.api-sports.io"


class HttpError(RuntimeError):
    def __init__(self, status: int, body: str, retry_after: str | None = None) -> None:
        super().__init__(f"HTTP {status}")
        self.status = status
        self.body = body
        self.retry_after = retry_after


class ApiSportsProvider:
    """Thin HTTP adapter. Prefer FixtureProvider in tests/CI (NFR-003)."""

    def __init__(self, api_key: str, *, base_url: str = DEFAULT_BASE) -> None:
        if not api_key:
            raise ValueError("API_SPORTS_KEY is required for live provider")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def fetch_teams(self) -> list[dict[str, Any]]:
        payload = self._get("/teams", {"league": "12"})  # NBA league id on API-Sports basketball
        return list(payload.get("response", []))

    def fetch_games(self, season: int) -> list[dict[str, Any]]:
        payload = self._get("/games", {"league": "12", "season": str(season)})
        return list(payload.get("response", []))

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        url = f"{self._base_url}{path}?{urlencode(params)}"

        def operation() -> dict[str, Any]:
            req = urllib.request.Request(
                url,
                headers={"x-apisports-key": self._api_key},
                method="GET",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                body = exc.read().decode("utf-8", errors="replace")
                raise HttpError(exc.code, body, retry_after) from exc

        def is_retryable(exc: BaseException) -> bool:
            if isinstance(exc, HttpError):
                return exc.status in {408, 425, 429, 500, 502, 503, 504}
            return isinstance(exc, (TimeoutError, urllib.error.URLError))

        def get_retry_after(exc: BaseException) -> float | None:
            if isinstance(exc, HttpError):
                return parse_retry_after(exc.retry_after)
            return None

        return retry_with_backoff(
            operation,
            is_retryable=is_retryable,
            get_retry_after=get_retry_after,
        )
