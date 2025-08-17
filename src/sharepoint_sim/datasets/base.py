"""Base dataset generator contract."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Employee, Roster


class DatasetGenerator(ABC):
    """Abstract base for dataset generators.

    Subclasses must define ``name`` (dataset code) and ``headers`` (ordered
    column names) and implement ``row_count`` and ``generate_rows``.

    Attributes:
        name (str): Dataset code identifier.
        headers (Sequence[str]): Ordered list of column names each generated row must supply.
        roster (Roster): Shared roster used for employee selection.
        rnd (RandomProvider): Deterministic randomness / clock provider.
    """

    name: str
    headers: Sequence[str]

    def __init__(self, roster: Roster, rnd: RandomProvider) -> None:
        """Initialize generator with shared roster and deterministic random provider.

        Args:
            roster (Roster): Pre-loaded employee roster.
            rnd (RandomProvider): Random provider (seeded for determinism across runs/tests).
        """
        self.roster = roster
        self.rnd = rnd

    @abstractmethod
    def row_count(self, requested: int | None = None) -> int:
        """Return number of rows to generate for this build cycle.

        Implementations may use a requested override, internal stochastic logic, or business rules.

        Args:
            requested (int | None): Caller-supplied desired row count override. ``None`` lets the
                implementation choose its default / rule-based count.

        Returns:
            int: Non-negative row count to produce.

        Raises:
            ValueError: If an implementation computes a negative count (should be prevented in concrete classes).
        """
        raise NotImplementedError

    @abstractmethod
    def generate_rows(self, count: int) -> list[dict[str, str]]:
        """Generate exactly ``count`` row dictionaries.

        Args:
            count (int): Exact number of rows to create (already validated by caller logic).

        Returns:
            list[dict[str, str]]: Generated rows. Each dict contains an entry for every header name.

        Raises:
            ValueError: If a concrete implementation produces malformed rows (header misalignment).
        """
        raise NotImplementedError

    def pick_employee(self, role: str | None = None) -> Employee:
        """Return a deterministic random employee, optionally filtered by role.

        Args:
            role (str | None): Role key (e.g. ``"inbound"``) to constrain selection. ``None`` uses full roster.

        Returns:
            Employee: Selected employee.

        Raises:
            ValueError: If an invalid role is supplied (propagated from roster lookup).
        """
        pool: list[Employee] = self.roster.by_role(role) if role else self.roster.employees
        return self.rnd.choice(pool)

    def build(self, requested: int | None = None) -> list[dict[str, str]]:
        """Compute row count then generate that many rows (asserting size).

        Args:
            requested (int | None): Optional row count override passed to ``row_count``.

        Returns:
            list[dict[str, str]]: Generated rows (length equals resolved row count).

        Raises:
            AssertionError: If generator output length mismatches the computed count (logic error).
        """
        count = self.row_count(requested)
        rows = self.generate_rows(count)
        assert len(rows) == count
        return rows
