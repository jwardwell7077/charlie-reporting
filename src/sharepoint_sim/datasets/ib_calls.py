"""IB_Calls dataset generator."""
from __future__ import annotations

from datetime import datetime, timezone
from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import IB_CALLS_HEADERS, ROLE_RULES


class IBCallsGenerator(DatasetGenerator):
    name = "IB_Calls"
    headers = IB_CALLS_HEADERS

    def row_count(self, requested: int | None = None) -> int:
        if requested is not None:
            return max(10, min(1000, requested))
        return 50

    def generate_rows(self, count: int):  # type: ignore[override]
        rows: list[dict[str, str]] = []
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        for _ in range(count):
            while True:
                emp = self.pick_employee()
                if emp.role in ROLE_RULES[self.name]:
                    break
            handle = self.rnd.rand_int(0, 25)
            rows.append({
                "Interval Start": now.isoformat(timespec="seconds"),
                "Interval End": now.isoformat(timespec="seconds"),
                "Interval Complete": "true",
                "Filters": "",
                "Media Type": "voice",
                "Agent Id": emp.uuid,
                "Agent Name": emp.name,
                "Handle": str(handle),
                "Avg Handle": str(handle),
            })
        return rows

__all__ = ["IBCallsGenerator"]
