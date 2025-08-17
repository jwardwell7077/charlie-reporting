"""Productivity dataset generator."""
from __future__ import annotations

from datetime import UTC, datetime

from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import PRODUCTIVITY_HEADERS, ROLE_RULES


class ProductivityGenerator(DatasetGenerator):
    """Generator for the Productivity dataset."""
    name = "Productivity"
    headers = PRODUCTIVITY_HEADERS

    def row_count(self, requested: int | None = None) -> int:
        """Return the number of rows to generate for this interval."""
        if requested is not None:
            return max(10, min(1000, requested))
        return 50

    def generate_rows(self, count: int) -> list[dict[str, str]]:
        """Generate a list of Productivity dataset rows as dictionaries."""
        rows: list[dict[str, str]] = []
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        for _ in range(count):
            while True:
                emp = self.pick_employee()
                if emp.role in ROLE_RULES[self.name]:
                    break
            rows.append({
                "Interval Start": now.isoformat(timespec="seconds"),
                "Interval End": now.isoformat(timespec="seconds"),
                "Interval Complete": "true",
                "Filters": "",
                "Agent Id": emp.uuid,
                "Agent Name": emp.name,
                "Logged In": str(self.rnd.rand_int(200, 480)),
                "On Queue": str(self.rnd.rand_int(50, 300)),
                "Idle": str(self.rnd.rand_int(0, 120)),
                "Off Queue": str(self.rnd.rand_int(0, 60)),
                "Interacting": str(self.rnd.rand_int(20, 200)),
            })
        return rows

__all__ = ["ProductivityGenerator"]
