"""Base dataset generator contract."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster, Employee


class DatasetGenerator(ABC):
    name: str  # dataset short code
    headers: Sequence[str]

    def __init__(self, roster: Roster, rnd: RandomProvider):
        self.roster = roster
        self.rnd = rnd

    @abstractmethod
    def row_count(self, requested: int | None = None) -> int:  # number of rows this interval
        raise NotImplementedError

    @abstractmethod
    def generate_rows(self, count: int) -> list[dict[str, str]]:
        raise NotImplementedError

    def pick_employee(self, role: str | None = None) -> Employee:
        if role:
            pool = self.roster.by_role(role)
        else:
            pool = self.roster.employees
        return self.rnd.choice(pool)  # type: ignore[return-value]

    def build(self, requested: int | None = None) -> list[dict[str, str]]:
        count = self.row_count(requested)
        rows = self.generate_rows(count)
        assert len(rows) == count
        return rows
