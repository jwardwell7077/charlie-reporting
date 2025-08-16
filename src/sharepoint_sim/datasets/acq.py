"""ACQ dataset generator.

Headers inferred from real samples (spec section).
"""
from __future__ import annotations

from datetime import datetime, timezone
from sharepoint_sim.datasets.base import DatasetGenerator

ACQ_HEADERS = [
    "AccountId",
    "UserId",
    "EmployeeName",
    "Value",
    "Created",
]


class ACQGenerator(DatasetGenerator):
    name = "ACQ"
    headers = ACQ_HEADERS

    def row_count(self, requested: int | None = None) -> int:  # min 10, max 1000, default 50
        if requested is not None:
            requested = max(10, min(1000, requested))
            return requested
        return 50

    def generate_rows(self, count: int):  # type: ignore[override]
        rows: list[dict[str, str]] = []
        for _ in range(count):
            emp = self.pick_employee()
            rows.append({
                "AccountId": str(self.rnd.rand_int(1000, 9999)),
                "UserId": emp.uuid,
                "EmployeeName": emp.name,
                "Value": str(self.rnd.rand_int(1, 5000)),
                "Created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
        return rows

__all__ = ["ACQGenerator", "ACQ_HEADERS"]
