# E2E Quickstart (Current Pipeline)

This guide shows how to run the end-to-end flow using provided VS Code tasks.

Pipeline:

- SharePoint Simulator → Scheduler (download CSVs) → Consumer (ingest + archive) → DB Service → Report Service (CSV/XLSX)

## 1) Start services

- Run: SharePoint Simulator (port 8001)
- Run: DB Service API (port 8000)
- Run: Report Service API (port 8091)

These tasks are added under “Run and Debug” → “Tasks”. Use the stop button to terminate servers.

## 2) Generate simulator data

Invoke the simulator to create fresh CSVs (ACQ, Productivity, etc.). With the "Run Simulator (uvicorn)" task active on port 8001, trigger generation:

Example (using curl):

Endpoint: `http://localhost:8001/sim/generate`
Body (JSON): `{"dataset": "acq", "rows": 50}`

Files will appear under the simulator’s output directory and then be fetched by the scheduler.

## 3) Download new files

- Run: Scheduler (Run Once)

This downloads new files from the simulator into `./data/incoming`, skipping already ingested files.

## 4) Ingest and archive

- Run: Consumer (Run Once)

This processes `./data/incoming` CSVs: validates, ingests to SQLite (`db_service.sqlite3`), and moves files to `./data/outputs`.

## 5) Generate a report

With the "Run Report Service API (uvicorn)" task active on port 8091, POST `/reports/generate` with your dataset and time window (format: `csv` or `xlsx`). Then GET `/reports` to list and `/reports/download/{filename}` to fetch.

## Notes

- Environment variables:
  - SIM_BASE_URL defaults to `http://localhost:8001`
  - REPORTS_DIR defaults to `./reports`
  - DB_API_URL defaults to `http://localhost:8000`
- Tests: Use the “Run Unit Tests (pytest)” task.
