"""FastAPI service exposing minimal endpoints.
- /ingest : trigger collection + load
- /generate/hourly : build workbook and push via stub
- /health : basic status
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from sharepoint_sim.api import router as sim_router

from config.settings import load_settings
from pipeline import aggregator, collector, excel, loader
from services.sharepoint_stub import SharePointStub

app = FastAPI(title="Reporting Foundation", version="0.1.0")
app.include_router(sim_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health probe endpoint.

    Returns:
        Simple status dictionary when the service is responsive.
    """
    return {"status": "ok"}


@app.post("/ingest")
async def ingest() -> dict[str, int]:
    """Run collection + load pipeline steps.

    Returns:
        Counts of staged files and total rows loaded.
    """
    settings = load_settings()
    staged = collector.collect(settings)
    results = loader.load_staged(settings)
    return {"staged_files": len(staged), "rows_loaded_total": sum(results.values())}


@app.post("/generate/hourly")
async def generate_hourly() -> dict[str, str]:
    """Generate the hourly workbook and upload via SharePoint stub.

    Returns:
        Path (string) to uploaded workbook inside stub library.
    """
    settings = load_settings()
    db_path = Path("foundation.sqlite")
    frames = aggregator.build_report_frames(db_path)
    output_file = Path(settings.report.output_dir) / settings.report.workbook_name
    excel.build_workbook(frames, output_file)

    sp_root = Path("./_sharepoint_library")
    sharepoint = SharePointStub(sp_root)
    uploaded = sharepoint.upload(output_file)
    return {"workbook": str(uploaded)}
