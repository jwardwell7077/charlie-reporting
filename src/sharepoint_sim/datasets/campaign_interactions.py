"""Campaign_Interactions dataset generator.

Addendum: timestamps sourced from shared ``RandomProvider`` for deterministic tests.
"""
from __future__ import annotations

from datetime import UTC

from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import CAMPAIGN_INTERACTIONS_HEADERS


class CampaignInteractionsGenerator(DatasetGenerator):
    """Generator for the Campaign_Interactions dataset."""

    name = "Campaign_Interactions"
    headers = CAMPAIGN_INTERACTIONS_HEADERS

    def row_count(self, requested: int | None = None) -> int:
        """Return number of rows to generate (min 10, max 1000, default 50)."""
        if requested is not None:
            return max(10, min(1000, requested))
        return 50

    def generate_rows(self, count: int) -> list[dict[str, str]]:
        """Generate Campaign_Interactions rows."""
        rows: list[dict[str, str]] = []
        now = self.rnd.now().astimezone(UTC).replace(second=0, microsecond=0)
        for _ in range(count):
            emp = self.pick_employee()  # all roles allowed
            rows.append(
                {
                    "Full Export Completed": now.isoformat(timespec="seconds"),
                    "Partial Result Timestamp": now.isoformat(timespec="seconds"),
                    "Filters": "",
                    "Users": emp.uuid,
                    "Date": now.date().isoformat(),
                    "Initial Direction": "inbound"
                    if self.rnd.rand_int(0, 1) == 0
                    else "outbound",
                    "First Queue": "q1",
                }
            )
        return rows

__all__ = ["CampaignInteractionsGenerator"]
