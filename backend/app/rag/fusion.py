"""Reciprocal Rank Fusion."""

from __future__ import annotations

from collections.abc import Hashable, Sequence
from typing import TypeVar

K = TypeVar("K", bound=Hashable)

RRF_K = 60


def rrf_score(rank: int, k: int = RRF_K) -> float:
    """Вклад одного списка; rank начинается с 1."""
    return 1.0 / (k + rank)


def rrf(rank_lists: Sequence[Sequence[K]], k: int = RRF_K) -> dict[K, float]:
    """Слияние ранжированных списков: score(d) = Σ 1/(k + rank_i(d))."""
    scores: dict[K, float] = {}
    for items in rank_lists:
        seen: set[K] = set()
        rank = 0
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            rank += 1
            scores[item] = scores.get(item, 0.0) + rrf_score(rank, k)
    return scores
