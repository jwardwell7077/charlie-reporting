"""Dials dataset generator.

Addendum: timestamps sourced from shared ``RandomProvider`` for deterministic tests.
"""
from __future__ import annotations

from datetime import UTC

from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import DIALS_HEADERS, ROLE_RULES


class DialsGenerator(DatasetGenerator):
    """Generator for the Dials dataset."""
    name = "Dials"
    headers = DIALS_HEADERS

    def row_count(self, requested: int | None = None) -> int:
        """Return the number of rows to generate for this interval."""
        if requested is not None:
            return max(10, min(1000, requested))
        return 50

    def generate_rows(self, count: int) -> list[dict[str, str]]:
        """Generate a list of Dials dataset rows as dictionaries."""
        rows: list[dict[str, str]] = []
        now = self.rnd.now().astimezone(UTC).replace(second=0, microsecond=0)
        for _ in range(count):
            while True:
                emp = self.pick_employee()
                if emp.role in ROLE_RULES[self.name]:
                    break
            handle = self.rnd.rand_int(0, 25)
            talk = self.rnd.rand_int(0, handle)
            hold = self.rnd.rand_int(0, max(0, handle - talk))
            acw = self.rnd.rand_int(0, 10)
            rows.append(
                {
                    "Interval Start": now.isoformat(timespec="seconds"),
                    "Interval End": now.isoformat(timespec="seconds"),
                    "Interval Complete": "true",
                    "Filters": "",
                    "Media Type": "voice",
                    "Agent Id": emp.uuid,
                    "Agent Name": emp.name,
                    "Handle": str(handle),
                    "Avg Handle": str(handle),
                    "Avg Talk": str(talk),
                    "Avg Hold": str(hold),
                    "Avg ACW": str(acw),
                    "Total Handle": str(handle * 5),
                    "Total Talk": str(talk * 5),
                    "Total Hold": str(hold * 5),
                    "Total ACW": str(acw * 5),
                }
            )
        return rows

__all__ = ["DialsGenerator"]
