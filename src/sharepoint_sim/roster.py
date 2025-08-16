"""Employee roster loading and selection.

The roster is stored in a static CSV file under `sharepoint_sim/sharepoint_employees.csv`.
Each row: uuid,name,role
Roles: inbound, outbound, hybrid (distribution 40/40/20 in 100 rows)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv

PACKAGE_ROOT = Path(__file__).resolve().parent
ROSTER_CSV = PACKAGE_ROOT / "sharepoint_employees.csv"


@dataclass(frozen=True, slots=True)
class Employee:
    """Immutable employee record."""
    uuid: str
    name: str
    role: str  # inbound | outbound | hybrid


class Roster:
    """In-memory roster built from CSV."""

    def __init__(self, employees: list[Employee]):
        if len(employees) != 100:
            raise ValueError("Roster must contain exactly 100 employees per spec")
        self._employees = employees
        self._by_role: dict[str, list[Employee]] = {"inbound": [], "outbound": [], "hybrid": []}
        for e in employees:
            if e.role not in self._by_role:  # pragma: no cover - defensive
                raise ValueError(f"Unexpected role: {e.role}")
            self._by_role[e.role].append(e)

    @property
    def employees(self) -> list[Employee]:
        return list(self._employees)

    def by_role(self, role: str) -> list[Employee]:
        return list(self._by_role[role])

    def roles(self) -> list[str]:  # pragma: no cover - trivial
        return list(self._by_role.keys())


def load_roster(path: Path | None = None) -> Roster:
    """Load the roster CSV (path override for tests)."""
    p = path or ROSTER_CSV
    rows: list[Employee] = []
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = ["uuid", "name", "role"]
        if reader.fieldnames != expected:
            raise ValueError(f"Roster header mismatch: {reader.fieldnames} != {expected}")
        for r in reader:
            rows.append(Employee(uuid=r["uuid"], name=r["name"], role=r["role"]))
    return Roster(rows)


__all__ = ["Employee", "Roster", "load_roster", "ROSTER_CSV"]
