# DB Service API Design Spec

**Location:** `src/db_service/api.py`

## Purpose

A local, file-based (SQLite) database service with a REST API for ingesting and querying SharePoint CSV data. Designed for easy migration to Postgres/SQL in the future. No authentication or user management; API is open to all.

## Requirements

### Storage

- **Initial backend:** SQLite (local file)
- **Future backend:** Postgres (schema and code should allow easy migration)
- **Schema:** One table per dataset type, columns match CSV headers
- **File tracking:** Track all ingested files (filename, dataset, timestamp, etc.) to support idempotency and integration with the scheduler.

### API Endpoints

- `POST /ingest` — Ingest a CSV file (raw or as JSON rows)
  - Accepts: file upload (CSV) or JSON array of row dicts
  - Returns: success/failure, row count, error details if any
- `GET /datasets` — List all dataset types/tables
- `GET /data/{dataset}` — Query all rows for a dataset (optionally with filters)
- `DELETE /data/{dataset}` — Delete all rows for a dataset
- `GET /ingested-files` — List all ingested files (optionally filter by time interval, dataset, etc.)

### Behavior

- On ingest:
  - Validate schema matches expected columns
  - Insert rows into the appropriate table
  - Create table if it does not exist
  - Record the filename and metadata of each ingested file for tracking
- On query:
  - Return all rows (optionally filter by date, etc.)
- On delete:
  - Remove all rows for the dataset
- On ingested file query:
  - Return list of ingested files, optionally filtered by time interval, dataset, etc. (for use by the scheduler and for idempotency)

### Security

- No authentication or authorization (open API)
- No user management

### Extensibility

- Easy to add new dataset types (dynamic table creation)
- Easy to switch to Postgres (SQLAlchemy or similar ORM)

### Error Handling

- Return clear error messages for schema mismatch, DB errors, etc.
- Log all actions and errors

## Interfaces

### Main API (FastAPI)

- `POST /ingest` — Ingest CSV or JSON
- `GET /datasets` — List datasets
- `GET /data/{dataset}` — Query dataset
- `DELETE /data/{dataset}` — Delete dataset

### Internal

- `DatabaseService` class for DB logic (init, ingest, query, delete)

## Example Usage

```python
# Ingest via API
POST /ingest (file or JSON)

# Query via API
GET /data/ACQ
```

## Out of Scope

- Authentication, user management
- Advanced query/filtering (can be added later)

## Testing

- Unit tests for ingest, query, delete, error handling
- Integration tests for API endpoints

---
**Review and approve this spec before writing tests or implementation.**
