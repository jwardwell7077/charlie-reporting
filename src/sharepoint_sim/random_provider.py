"""Random utilities with deterministic seeding and injectable clock."""
from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TypeVar

ClockFn = Callable[[], datetime]


def default_clock() -> datetime:
    """Return current UTC time (separate for easier test injection)."""
    return datetime.now(UTC)


T = TypeVar("T")


@dataclass
class RandomProvider:
    """Deterministic random + time provider wrapper.

    Not cryptographically secure (uses ``random.Random``); acceptable for
    simulation. A seed of ``None`` delegates to system randomness.
    """

    seed: int | None
    clock: ClockFn = default_clock

    def __post_init__(self) -> None:
        """Initialize underlying PRNG (non-cryptographic)."""
        self._rng = random.Random(self.seed)  # noqa: S311 - simulation only

    def rand_int(self, a: int, b: int) -> int:
        """Return random integer in [a, b] inclusive."""
        return self._rng.randint(a, b)

    def choice(self, seq: Sequence[T]) -> T:  # type: ignore[type-var]
        """Return random element from sequence with preserved element type."""
        return self._rng.choice(list(seq))

    def random(self) -> float:
        """Return random float in [0, 1)."""
        return self._rng.random()

    def now(self) -> datetime:
        """Return current (possibly injected) time."""
        return self.clock()
