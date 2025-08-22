"""
Report Generation Service Core Logic.
Fetches data from DB Service API and emits reports (CSV/XLSX).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class ReportDBClient:
    def __init__(self, api_url: Optional[str] = None, session: Optional[Any] = None) -> None:
        self.api_url = (api_url or "http://localhost:8000").rstrip("/")
        self.session = session
        if self.session is None:
            try:
                import requests  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError("ReportDBClient requires an HTTP session in this environment") from exc
            self.session = requests.Session()  # type: ignore

    def _url(self, path: str) -> str:
        if path.startswith("/"):
            return f"{self.api_url}{path}"
        return f"{self.api_url}/{path}"

    def get_rows(
        self,
        dataset: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        timestamp_column: str = "timestamp",
        columns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"timestamp_column": timestamp_column}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if columns:
            params["columns"] = ",".join(columns)
        resp: Any = self.session.get(self._url(f"/tables/{dataset}/rows"), params=params)  # type: ignore[attr-defined]
        resp.raise_for_status()
        return list(resp.json())


@dataclass
class ReportResult:
    dataset: str
    format: str
    path: Path
    row_count: int
    generated_at: str


class ReportService:
    def __init__(self, db_client: ReportDBClient, reports_dir: Path | str = "./reports") -> None:
        self.db = db_client
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        dataset: str,
        start_time: Optional[str],
        end_time: Optional[str],
        format: str = "xlsx",
    ) -> ReportResult:
        rows = self.db.get_rows(dataset, start_time=start_time, end_time=end_time)
        df = pd.DataFrame(rows)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"{dataset}_report_{ts}"
        generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if format.lower() == "csv":
            path = self.reports_dir / f"{base}.csv"
            df.to_csv(path, index=False)
            return ReportResult(dataset=dataset, format="csv", path=path, row_count=len(df), generated_at=generated_at)
        elif format.lower() in {"xlsx", "excel"}:
            path = self.reports_dir / f"{base}.xlsx"
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                sheet = dataset[:31] or "Sheet1"
                df.to_excel(writer, sheet_name=sheet, index=False)
            return ReportResult(dataset=dataset, format="xlsx", path=path, row_count=len(df), generated_at=generated_at)
        else:
            raise ValueError(f"Unsupported report format: {format}")
