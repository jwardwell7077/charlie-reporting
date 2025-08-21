# Scheduler Design Spec

## Overview

The scheduler is responsible for automating the retrieval of files from a SharePoint (or Graph API) directory and moving them into the local ingestion directory on a configurable schedule. It does **not** handle idempotency, file tracking, or archiving—these are the responsibility of the File Watcher (FileConsumer) and/or the DB service.

---

## Responsibilities

- Authenticate with SharePoint/Graph API.
- Query the DB service for a list of already ingested files for the current time interval.
- List and download only new files from a configured SharePoint directory (skip files already processed).
- Move downloaded files into the local ingestion directory.
- Run on a configurable schedule (interval and/or explicit times).
- Log all actions and errors.
- Provide a CLI or API for manual triggering.
- Support graceful shutdown and error handling.

---

## Out of Scope

- Idempotency and file tracking (handled by File Watcher or DB service).
- Archiving or moving processed files (handled by File Watcher).

---

## Class & Function Structure

### 1. Scheduler

- **Class:** `Scheduler`
  - Loads schedule config from `settings.toml`.
  - Registers and runs jobs (using APScheduler or similar).
  - Handles graceful shutdown and logging.

### 2. SharePoint/Graph API Client

- **Class:** `SharePointClient`
  - Handles authentication.
  - Lists files in a SharePoint directory.
  - Downloads files to a local path.
  - (For now, these methods call sim service stubs; see TODO below.)

### 3. DB Service Client

- **Class:** `DBServiceClient`
  - Queries the DB service for a list of already ingested files for a given time interval.
  - Used by the scheduler to avoid re-downloading files that have already been processed.

### 3. Job Logic

- **Class:** `SyncJob`
  - Orchestrates the end-to-end sync: authenticate, list, download, move files.
  - Handles retries and error logging.

### 4. CLI Entrypoint

- **Function:** `main()`
  - Parses CLI arguments (run, trigger, etc.).
  - Starts the scheduler or triggers a one-off sync.

---

## Example Flow

1. Scheduler wakes up on interval or at explicit time.
2. `SyncJob` authenticates with SharePoint/Graph API.
3. Queries the DB service for a list of already ingested files for the current time interval.
4. Lists files in the configured SharePoint directory.
5. Downloads only files that have not already been processed to the ingestion directory.
6. Logs all actions and errors.

---

## Configuration Example (`settings.toml`)

```toml
[scheduler]
enabled = true
log_level = "INFO"
max_retries = 3
retry_delay_seconds = 60
sharepoint_site_url = "https://yourtenant.sharepoint.com/sites/YourSite"
sharepoint_folder = "/Shared Documents/Reports"
ingestion_dir = "data/incoming"
client_id = "your-app-client-id"
client_secret = "your-app-client-secret"
tenant_id = "your-tenant-id"
```

---

## TODO

- Implement function stubs for SharePoint/Graph API communication. For now, these should call sim service functions as placeholders. When ready to integrate the real API, replace the sim calls with actual SharePoint/Graph API logic.
- Implement a DB service client for querying already ingested files.
- Ensure documentation and code clearly separate scheduler responsibilities from file watcher and DB service.
- Implement all classes and functions as described above.

---

> **Note:** This design ensures that when the sim service is dropped, only the SharePoint/Graph API client needs to be updated, minimizing refactor effort.
