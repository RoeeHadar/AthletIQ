# Implements: ML-003
"""Temporal train / validation / test split (no shuffle)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SplitIndices:
    train: list[int]
    validation: list[int]
    test: list[int]


def temporal_split(
    n: int,
    *,
    train_frac: float = 0.70,
    val_frac: float = 0.15,
    test_frac: float = 0.15,
) -> SplitIndices:
    """Split [0, n) into contiguous oldest→newest partitions.

    Fractions are approximate; remainders go to train then validation.
    """
    if n < 3:
        raise ValueError("need at least 3 samples for temporal split")
    if abs((train_frac + val_frac + test_frac) - 1.0) > 1e-6:
        raise ValueError("fractions must sum to 1")
    n_test = max(1, int(round(n * test_frac)))
    n_val = max(1, int(round(n * val_frac)))
    n_train = n - n_val - n_test
    if n_train < 1:
        n_train = 1
        n_val = max(1, (n - n_train) // 2)
        n_test = n - n_train - n_val
    train = list(range(0, n_train))
    validation = list(range(n_train, n_train + n_val))
    test = list(range(n_train + n_val, n))
    return SplitIndices(train=train, validation=validation, test=test)


def take(items: Sequence[T], indices: Sequence[int]) -> list[T]:
    return [items[i] for i in indices]
