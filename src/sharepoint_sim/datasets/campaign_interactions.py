"""Campaign_Interactions dataset generator."""
from __future__ import annotations

from datetime import datetime, timezone
from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.schemas import CAMPAIGN_INTERACTIONS_HEADERS, ROLE_RULES


class CampaignInteractionsGenerator(DatasetGenerator):
    name = "Campaign_Interactions"
    headers = CAMPAIGN_INTERACTIONS_HEADERS

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
                if emp.role in ROLE_RULES[self.name]:  # always true
                    break
            rows.append({
                "Full Export Completed": now.isoformat(timespec="seconds"),
                "Partial Result Timestamp": now.isoformat(timespec="seconds"),
                "Filters": "",
                "Users": emp.uuid,
                "Date": now.date().isoformat(),
                "Initial Direction": "inbound" if self.rnd.rand_int(0,1)==0 else "outbound",
                "First Queue": "q1",
            })
        return rows

__all__ = ["CampaignInteractionsGenerator"]
