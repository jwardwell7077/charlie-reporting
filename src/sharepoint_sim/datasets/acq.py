"""ACQ dataset generator matching spec headers.

Spec headers (section 3.1):
Interval Start,Interval End,Interval Complete,Filters,Media Type,Agent Id,Agent Name,Handle
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Final  # noqa: F401
from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import ACQ_HEADERS, ROLE_RULES


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
        now = self.rnd.now().astimezone(timezone.utc)
        # Use same interval start/end truncated to minute for simplicity
        interval_start = now.replace(second=0, microsecond=0)
        interval_end = interval_start
        for _ in range(count):
            # pick employee restricted to allowed roles
            while True:
                emp = self.pick_employee()
                if emp.role in ROLE_RULES[self.name]:
                    break
            rows.append({
                "Interval Start": interval_start.isoformat(timespec="seconds"),
                "Interval End": interval_end.isoformat(timespec="seconds"),
                "Interval Complete": "true",
                "Filters": "",
                "Media Type": "voice",
                "Agent Id": emp.uuid,
                "Agent Name": emp.name,
                "Handle": str(self.rnd.rand_int(0, 25)),
            })
        return rows

__all__ = ["ACQGenerator", "ACQ_HEADERS"]
