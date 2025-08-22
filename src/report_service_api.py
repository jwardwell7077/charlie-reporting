"""
Report Service API (FastAPI) for generating, listing, and downloading reports.

Design goals:
- Pull rows from the existing DB Service API using an injected HTTP session (FastAPI TestClient in tests).
- Generate CSV reports for a given dataset and time window (ISO 8601 strings).
- Store reports on disk in a configurable directory and expose download/list endpoints.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import csv
import os


app = FastAPI(title="Report Service API")


def _get_reports_dir() -> Path:
    # Allow override via app.state or environment; default to ./reports
    reports_dir: Optional[Path] = getattr(app.state, "reports_dir", None)  # type: ignore[attr-defined]
    if reports_dir is None:
        env_dir = os.environ.get("REPORTS_DIR")
        reports_dir = Path(env_dir) if env_dir else Path("./reports")
        app.state.reports_dir = reports_dir  # type: ignore[attr-defined]
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def _db_session() -> Any:
    sess = getattr(app.state, "db_session", None)  # type: ignore[attr-defined]
    if sess is None:
        try:
            import requests  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=500, detail="DB session not configured") from exc
        base_url = os.environ.get("DB_API_URL", "http://localhost:8000").rstrip("/")
        s = requests.Session()  # type: ignore
        # Wrap to prepend base_url for path-only requests
        class _Wrapper:
            def __init__(self, session: Any, base: str):
                self._s = session
                self._base = base
            def get(self, url: str, **kwargs: Any):  # noqa: D401
                full = url if url.startswith("http") else f"{self._base}{url}"
                return self._s.get(full, **kwargs)
        sess = _Wrapper(s, base_url)
        app.state.db_session = sess  # type: ignore[attr-defined]
    return sess


class ReportRequest(BaseModel):
    dataset: str = Field(..., description="Dataset/table name to query")
    start_time: str = Field(..., description="Inclusive ISO 8601 start time")
    end_time: str = Field(..., description="Inclusive ISO 8601 end time")
    format: str = Field("csv", description="Report format (csv)")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/reports")
def list_reports() -> JSONResponse:
    reports_dir = _get_reports_dir()
    items: List[Dict[str, Any]] = []
    for p in sorted(reports_dir.glob("*.csv")):
        stat = p.stat()
        items.append({
            "filename": p.name,
            "path": str(p.resolve()),
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        })
    return JSONResponse(content={"reports": items})


def _fetch_rows(dataset: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
    sess = _db_session()
    params = {
        "start_time": start_time,
        "end_time": end_time,
        "timestamp_column": "timestamp",
    }
    resp = sess.get(f"/tables/{dataset}/rows", params=params)
    if getattr(resp, "status_code", 200) == 404:
        return []
    try:
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"DB API error: {getattr(resp, 'text', str(exc))}")
    data_raw: Any = resp.json()
    if not isinstance(data_raw, list):
        raise HTTPException(status_code=502, detail="Unexpected DB API response")
    rows: List[Dict[str, Any]] = []
    for item in data_raw:
        try:
            mapping: Dict[str, Any] = dict(item) if isinstance(item, dict) else dict(item)
            rows.append(mapping)
        except Exception:
            # Skip rows that cannot be coerced; defensive
            continue
    return rows


def _write_csv(rows: List[Dict[str, Any]], path: Path) -> int:
    if not rows:
        # Write just headers if no data? Keep minimal CSV with no header if unknown columns.
        path.write_text("")
        return 0
    # Determine fieldnames from first row (stable order by insertion or sorted as fallback)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


@app.post("/reports/generate")
def generate_report(payload: ReportRequest = Body(...)) -> JSONResponse:
    if payload.format.lower() != "csv":
        raise HTTPException(status_code=400, detail="Only csv format is supported")

    rows = _fetch_rows(payload.dataset, payload.start_time, payload.end_time)
    reports_dir = _get_reports_dir()
    safe_dataset = "".join(ch for ch in payload.dataset if ch.isalnum() or ch in ("_", "-")) or "dataset"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_dataset}_{timestamp}.csv"
    out_path = reports_dir / filename
    count = _write_csv(rows, out_path)

    return JSONResponse(content={
        "message": "Report generated",
        "dataset": payload.dataset,
        "format": "csv",
        "row_count": count,
        "filename": filename,
        "path": str(out_path.resolve()),
    })


@app.get("/reports/download/{filename}")
def download_report(filename: str) -> FileResponse:
    reports_dir = _get_reports_dir()
    path = (reports_dir / filename).resolve()
    if not path.exists() or not str(path).startswith(str(reports_dir.resolve())):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="text/csv", filename=filename)
 
