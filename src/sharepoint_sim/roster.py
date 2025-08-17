"""Employee roster loading and selection.

The roster is stored in a static CSV file under
``sharepoint_sim/sharepoint_employees.csv`` with columns::

    uuid,name,role

Role distribution: ``inbound`` 40, ``outbound`` 40, ``hybrid`` 20 (total 100).
The module provides lightweight immutable ``Employee`` records, an in-memory
``Roster`` container with convenience selectors.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
ROSTER_CSV = PACKAGE_ROOT / "sharepoint_employees.csv"


@dataclass(frozen=True, slots=True)
class Employee:
    """Immutable employee record.

    Attributes:
        uuid (str): Stable unique identifier.
        name (str): Display name.
        role (str): One of ``inbound``, ``outbound``, or ``hybrid``.
    """

    uuid: str
    name: str
    role: str  # inbound | outbound | hybrid


ROSTER_SIZE = 100


class Roster:
    """In-memory roster container with optional self-loading.

    By default, constructing ``Roster()`` (with no arguments) reads the
    packaged CSV file. A custom list of employees or alternate path can be
    supplied for tests or alternative datasets.
    """

    def __init__(self, employees: list[Employee] | None = None, path: Path | None = None) -> None:
        """Create a roster, loading from CSV if employees not provided.

        Args:
            employees (list[Employee] | None): Pre-built employee list. If
                ``None``, the CSV at ``path`` (or default path) is loaded.
            path (Path | None): Optional override CSV path when auto-loading.

        Raises:
            ValueError: If roster size != spec or unknown role is found.
        """
        if employees is None:
            employees = self._load_csv(path or ROSTER_CSV)
        if len(employees) != ROSTER_SIZE:
            raise ValueError("Roster must contain exactly 100 employees per spec")
        self._employees: list[Employee] = employees
        self._by_role: dict[str, list[Employee]] = {"inbound": [], "outbound": [], "hybrid": []}
        for e in employees:
            if e.role not in self._by_role:  # pragma: no cover - defensive
                raise ValueError(f"Unexpected role: {e.role}")
            self._by_role[e.role].append(e)

    # ---------------------------------------------------------------------
    # Construction helpers
    # ---------------------------------------------------------------------
    @classmethod
    def from_csv(cls, path: Path | None = None) -> Roster:
        """Alternate constructor loading directly from CSV.

        Args:
            path (Path | None): Optional path override.

        Returns:
            Roster: Loaded roster instance.
        """
        return cls(employees=None, path=path)

    @staticmethod
    def _load_csv(path: Path) -> list[Employee]:
        """Load employees from a CSV file.

        Args:
            path (Path): CSV file path.

        Returns:
            list[Employee]: Loaded employee records.

        Raises:
            ValueError: If header mismatch occurs.
        """
        rows: list[Employee] = []
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected = ["uuid", "name", "role"]
            if reader.fieldnames != expected:
                raise ValueError(
                    f"Roster header mismatch: {reader.fieldnames} != {expected}"
                )
            for r in reader:
                rows.append(Employee(uuid=r["uuid"], name=r["name"], role=r["role"]))
        return rows

    @property
    def employees(self) -> list[Employee]:
        """Return a shallow copy of all employees.

        Returns:
            list[Employee]: Copy preserving original ordering.
        """
        return list(self._employees)

    def by_role(self, role: str) -> list[Employee]:
        """Return employees filtered by role.

        Args:
            role (str): Role key (``inbound``, ``outbound``, or ``hybrid``).

        Returns:
            list[Employee]: Employees whose ``role`` matches.
        """
        return list(self._by_role[role])

    def roles(self) -> list[str]:  # pragma: no cover - trivial
        """Return role keys present in the roster."""
        return list(self._by_role.keys())


__all__ = ["Employee", "Roster", "ROSTER_CSV", "ROSTER_SIZE"]
