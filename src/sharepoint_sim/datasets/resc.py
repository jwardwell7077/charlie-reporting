"""RESC dataset generator.

Addendum: timestamps sourced from shared ``RandomProvider`` for deterministic tests.
"""
from __future__ import annotations

from datetime import UTC

from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import RESC_HEADERS, ROLE_RULES


class RESCGenerator(DatasetGenerator):
    """Generator for the RESC dataset."""
    name = "RESC"
    headers = RESC_HEADERS

    def row_count(self, requested: int | None = None) -> int:
        """Return the number of rows to generate for this interval."""
        if requested is not None:
            return max(10, min(1000, requested))
        return 50

    def generate_rows(self, count: int) -> list[dict[str, str]]:
        """Generate a list of RESC dataset rows as dictionaries."""
        rows: list[dict[str, str]] = []
        now = self.rnd.now().astimezone(UTC).replace(second=0, microsecond=0)
        for _ in range(count):
            while True:
                emp = self.pick_employee()
                if emp.role in ROLE_RULES[self.name]:
                    break
            rows.append(
                {
                    "Interval Start": now.isoformat(timespec="seconds"),
                    "Interval End": now.isoformat(timespec="seconds"),
                    "Interval Complete": "true",
                    "Filters": "",
                    "Media Type": "voice",
                    "Agent Id": emp.uuid,
                    "Agent Name": emp.name,
                    "Handle": str(self.rnd.rand_int(0, 25)),
                }
            )
        return rows

__all__ = ["RESCGenerator"]
