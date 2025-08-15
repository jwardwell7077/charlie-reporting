# Reporting Foundation (Clean Restart)

Minimal platform for hourly & daily reporting fed by SharePoint-exported CSV data.

## Goals

- Simple, configurable ingestion (CSV drop -> local DB)
- Config-driven: data sources, schedules, columns, output sheets
- FastAPI-based service endpoints (ingest, generate report, status)
- Extensible to multiple future reports
- Re-use lessons: typing, linting, tests, small modules

## High-Level Flow

SharePoint (CSV export) -> Collector -> Staging dir -> Loader -> SQLite -> Aggregator -> Excel Builder ->

- Hourly publish (store + SharePoint upload stub)
- Daily (4x) email subset of sheets

## Components

- config: Load TOML settings (data sources, schedule, columns, sharepoint paths)
- pipeline.collector: Watches or scans configured directories
- pipeline.loader: Upserts rows into SQLite (idempotent)
- pipeline.aggregator: Builds DataFrames for defined report views
- pipeline.excel: Creates workbook, extracts sheets to HTML
- services.sharepoint_stub: Simulated push/pull endpoints
- services.reporting_api: FastAPI app orchestrating actions

## CLI (planned)

```
python -m foundation ingest-once
python -m foundation generate-hourly
python -m foundation send-daily-email
```

## Configuration (example `config/settings.toml`)

```toml
[schedules]
hourly_interval_minutes = 60
quad_daily_times = ["08:00","12:00","16:00","19:00"]

[data_sources]
# Each source maps to a directory where SharePoint auto-dumps CSVs
sources = [
  { name = "productivity", pattern = "Productivity_*.csv", enabled = true },
  { name = "calls", pattern = "Calls_*.csv", enabled = true }
]

[collector]
input_root = "./_sharepoint_drop"
staging_dir = "./_staging"
archive_dir = "./_archive"

[report]
output_dir = "./_reports"
workbook_name = "hourly_report.xlsx"

[report.columns]
productivity = ["agent","date","acq","revenue"]
calls = ["agent","call_time","duration"]

[email]
from = "reports@example.com"
recipients = ["team@example.com"]
subject_template = "Daily Performance Report {date}"
include_sheets = ["HourlySummary","DailyDetail"]
```

## SharePoint Auto Dump?

Yes, practical options:

1. Official Graph API sync job (future) writing files locally.
2. Power Automate flow: When file created -> save to on-prem / network share mapped locally.
3. Manual scheduled export script (Graph) -> local folder.

MVP uses a local folder acting as the dump location.

## Next Steps

- Implement settings loader
- Implement collector + loader stubs
- Implement DB schema + migration
- Implement aggregator & excel builder
- FastAPI endpoints + simple scheduler loop
- Tests
