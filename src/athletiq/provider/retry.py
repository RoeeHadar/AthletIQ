# Implements: FR-001 — provider HTTP retries (error-handling design Q6)
"""Exponential backoff + jitter; max 5 attempts; honor Retry-After."""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")

MAX_ATTEMPTS = 5


class RetryExhaustedError(RuntimeError):
    """Raised after max attempts."""


def parse_retry_after(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def compute_backoff_seconds(attempt: int, retry_after: float | None = None) -> float:
    """attempt is 0-based failure count before this sleep."""
    if retry_after is not None and retry_after >= 0:
        return retry_after
    base = 2**attempt
    jitter = random.uniform(0, 0.5 * base)
    return base + jitter


def retry_with_backoff(
    operation: Callable[[], T],
    *,
    is_retryable: Callable[[BaseException], bool],
    get_retry_after: Callable[[BaseException], float | None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    max_attempts: int = MAX_ATTEMPTS,
    rng: random.Random | None = None,
) -> T:
    """Call `operation` up to max_attempts with exponential backoff + jitter."""
    last_exc: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            return operation()
        except BaseException as exc:  # noqa: BLE001 — boundary for retry classification
            last_exc = exc
            if not is_retryable(exc) or attempt >= max_attempts - 1:
                raise
            retry_after = get_retry_after(exc) if get_retry_after else None
            if rng is not None and retry_after is None:
                base = 2**attempt
                delay = base + rng.uniform(0, 0.5 * base)
            else:
                delay = compute_backoff_seconds(attempt, retry_after)
            sleep(delay)
    assert last_exc is not None
    raise RetryExhaustedError(str(last_exc)) from last_exc
