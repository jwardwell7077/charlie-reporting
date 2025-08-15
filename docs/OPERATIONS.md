# Operations Guide (Lean Monolith)

Practical run + maintenance notes for the current focused pipeline.

## Run Modes

| Mode | Purpose | How |
|------|---------|-----|
| Ad-hoc ingest | Pull & load new CSVs now | `python run.py ingest` (planned CLI) / POST `/ingest` |
| Hourly report | Scheduled aggregation + Excel | Future scheduler (cron/APScheduler) calling internal function |
| Daily (quad) report | 4x per day summary workbook | Future `/generate/daily` endpoint |

## Data Flow (Current)

1. Collector locates unprocessed CSVs (patterns in `config/settings.toml`).
2. Loader parses, normalizes, inserts rows (idempotent plan: `ingestion_log` table).
3. Aggregator queries SQLite for hour or period windows.
4. Excel builder writes workbook to `reports/` (naming: `hourly_YYYYMMDD_HHMM.xlsx`).
5. (Planned) Email / SharePoint distribution.

## Configuration

| File | Responsibility |
|------|----------------|
| `config/settings.toml` | Source patterns, enable flags, column allowlists |
| (future) `.env` | Paths, email creds (if required) |

Reload strategy: restart process (config small – no hot reload needed yet).

## Scheduling (Planned)

Option A: System cron invoking a small wrapper script hourly.  
Option B: APScheduler in-process (simpler deployment, single node).  
Decision pending complexity; start with cron for transparency.

## Logging

Minimum viable: structured INFO logs to stdout (timestamp, stage, file, rows).  
Error cases: corrupt CSV -> WARN (skipped); unexpected exception -> ERROR + stack.

Future: rotate file logs in `logs/` once volume grows.

## Health & Observability

| Aspect | Current | Planned |
|--------|---------|---------|
| Liveness | `/health` always 200 | Add basic DB connectivity check |
| Metrics | None | Simple counts in `run_history` table |
| Tracing | None | Probably unnecessary until async tasks |

## Manual Recovery

| Scenario | Action |
|----------|--------|
| Bad CSV repeatedly failing | Move to `quarantine/` dir; note filename in log |
| Duplicate ingestion | Confirm loader idempotency key; purge offending rows if needed |
| Corrupt workbook output | Delete file, re-run aggregation function |

## Data Retention (Initial Thought)

- Keep raw rows indefinitely (small volume expected).  
- Consider monthly archive to parquet if DB grows > ~1M rows.

## Security / Access

Internal trusted environment; no auth layer yet.  
Trigger endpoints not exposed publicly; add token auth before external exposure.

## Future Ops TODO

- [ ] Implement ingestion_log table & duplicate check.
- [ ] Add run_history (start_ts, end_ts, rows_loaded, rows_aggregated, status).
- [ ] Email sender stub & configuration doc.
- [ ] SharePoint sync script (download & mark processed).
- [ ] Basic metrics endpoint `/metrics` (JSON counts) if needed.

See also: `foundation-overview.md`, `testing-approach.md`.
