"""Random utilities with deterministic seeding and injectable clock."""
from __future__ import annotations

from dataclasses import dataclass
import random
from datetime import datetime, timezone
from typing import Callable

ClockFn = Callable[[], datetime]


def default_clock() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class RandomProvider:
    seed: int | None
    clock: ClockFn = default_clock

    def __post_init__(self) -> None:  # noqa: D401 - simple init
        self._rng = random.Random(self.seed)

    def rand_int(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq: list[object]) -> object:
        return self._rng.choice(seq)

    def random(self) -> float:
        return self._rng.random()

    def now(self) -> datetime:
        return self.clock()
