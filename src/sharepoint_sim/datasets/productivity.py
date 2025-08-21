"""Productivity dataset generator.

Clarifications / Assumptions (spec addendum):
- Timestamps are deterministic per build cycle using the shared ``RandomProvider`` clock.
- Row count bounds: min 10, max 1000, default 50 when not overridden.
- Component time fields (On Queue, Idle, Off Queue, Interacting) MUST sum to
    a value less than or equal to Logged In. This file enforces that by
    drawing sequentially from remaining capacity after selecting Logged In.
"""
from __future__ import annotations

from datetime import UTC

from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import PRODUCTIVITY_HEADERS, ROLE_RULES


class ProductivityGenerator(DatasetGenerator):
    """Generator for the Productivity dataset."""
    name = "Productivity"
    headers = PRODUCTIVITY_HEADERS
    # Bucket bounds
    MIN_ON_QUEUE = 50
    MAX_ON_QUEUE = 300
    MIN_INTERACTING = 20
    MAX_INTERACTING = 200
    MAX_IDLE = 120
    MAX_OFF_QUEUE = 60

    def row_count(self, requested: int | None = None) -> int:
        """Return the number of rows to generate for this interval.

        Args:
            requested (int | None): Optional caller override.

        Returns:
            int: Bounded row count in [10, 1000].
        """
        if requested is not None:
            return max(10, min(1000, requested))
        return 50

    def generate_rows(self, count: int) -> list[dict[str, str]]:
        """Generate a list of Productivity dataset rows as dictionaries.

        Ensures component activity buckets do not exceed Logged In time.
        If remaining time is less than a bucket's minimum, that bucket is set to 0.

        Args:
            count (int): Number of rows to generate.

        Returns:
            list[dict[str, str]]: Generated row dictionaries.
        """
        rows: list[dict[str, str]] = []
        now = self.rnd.now().astimezone(UTC).replace(second=0, microsecond=0)
        for _ in range(count):
            while True:
                emp = self.pick_employee()
                if emp.role in ROLE_RULES[self.name]:
                    break
            logged_in = self.rnd.rand_int(200, 480)
            remaining = logged_in
            # On Queue
            on_queue = (
                self.rnd.rand_int(self.MIN_ON_QUEUE, min(self.MAX_ON_QUEUE, remaining))
                if remaining >= self.MIN_ON_QUEUE
                else 0
            )
            remaining -= on_queue
            # Interacting
            interacting = (
                self.rnd.rand_int(self.MIN_INTERACTING, min(self.MAX_INTERACTING, remaining))
                if remaining >= self.MIN_INTERACTING
                else 0
            )
            remaining -= interacting
            # Idle
            idle = self.rnd.rand_int(0, min(self.MAX_IDLE, remaining)) if remaining > 0 else 0
            remaining -= idle
            # Off Queue
            off_queue = self.rnd.rand_int(0, min(self.MAX_OFF_QUEUE, remaining)) if remaining > 0 else 0
            # Any residual remaining time is implicitly unallocated but constraint holds.
            rows.append({
                "Interval Start": now.isoformat(timespec="seconds"),
                "Interval End": now.isoformat(timespec="seconds"),
                "Interval Complete": "true",
                "Filters": "",
                "Agent Id": emp.uuid,
                "Agent Name": emp.name,
                "Logged In": str(logged_in),
                "On Queue": str(on_queue),
                "Idle": str(idle),
                "Off Queue": str(off_queue),
                "Interacting": str(interacting),
            })
        return rows

__all__ = ["ProductivityGenerator"]
