# API Overview (Minimal Foundation)

Current scope: single FastAPI app exposing health, ingestion, hourly report generation.

Endpoints:

| Method | Path | Purpose | Notes |
|--------|------|---------|-------|
| GET | /health | Liveness check | Static JSON |
| POST | /ingest | Run collector+loader | Synchronous MVP |
| POST | /generate/hourly | Aggregate + Excel + stub upload | Returns workbook path & sheets |

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
2. Async background jobs + /jobs/{id}
3. Email dispatch endpoint
4. Token auth when external exposure needed

Non-goals now: user management, file uploads, pagination.
