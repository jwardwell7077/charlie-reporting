# API Overview (Minimal Foundation)

Current scope: single FastAPI app exposing health, ingestion, hourly report generation.

Endpoints:

| Method | Path | Purpose | Notes |
|--------|------|---------|-------|
| GET | /health | Liveness check | Static JSON |
| POST | /ingest | Run collector+loader | Synchronous MVP |
| POST | /generate/hourly | Aggregate + Excel + stub upload | Returns workbook path & sheets |
| POST | /reports/jobs | Create a scheduler-driven report job | Accepts dataset, ISO start/end, columns, Interval Start/End, idempotency_key |
| GET | /reports/jobs/{id} | Poll job status | Returns status, filename, row_count |
| GET | /reports/files | List generated reports by filters | Filter by dataset and time range |
| GET | /reports/download/{filename} | Download generated report | xlsx content |

Simplifications vs prior microservice vision:

- No gateway, no multi-service orchestration.
- No background job queue yet.
- No auth; trusted environment assumption.

Example /generate/hourly response:

```json
{"status":"ok","workbook":"_reports/hourly_report.xlsx","sheets":["HourlySummary"]}
```

Planned extensions:

1. /generate/daily (quad-daily set)
2. Async background jobs + /jobs/{id} (superseded by /reports/jobs)
3. Email dispatch endpoint
4. Token auth when external exposure needed

Non-goals now: user management, file uploads, pagination.
