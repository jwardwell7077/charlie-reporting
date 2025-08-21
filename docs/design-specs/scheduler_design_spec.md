# Scheduler Design Spec

## Overview

The scheduler is responsible for automating the retrieval of files from a SharePoint (or Graph API) directory and moving them into the local ingestion directory on a configurable schedule. It does not handle idempotency, file tracking, or archiving—those are responsibilities of the File Watcher (FileConsumer) and/or the DB service.

This document defines the behavior contract, configuration, lifecycle, error handling, observability, and test coverage for the scheduler module (`scheduler.py`).

---

## Responsibilities

- Authenticate with SharePoint/Graph API.
- Query the DB service for a list of already ingested files for the current time interval.
- List and download only new files from a configured SharePoint directory (skip files already processed).
- Move downloaded files into the local ingestion directory.
- Run on a configurable schedule (interval and/or explicit times).
- Provide manual triggering (CLI) irrespective of schedule state.
- Log key lifecycle events, actions, and errors with structured context.
- Support graceful shutdown and well-defined error handling.

---

## Out of Scope

- Idempotency and file tracking (handled by File Watcher or DB service).
- Archiving or moving processed files (handled by File Watcher).

---

## Behavior Contract (Inputs/Outputs)

- Inputs
  - Config (see Configuration) including: `sharepoint_folder`, `ingestion_dir`, schedule settings, retry settings.
  - Time window for deduplication: by default, the last N minutes/hours based on the schedule cadence; configurable override accepted in future versions.
  - SharePoint/Graph API credentials or simulator.
  - DB service endpoint for querying already ingested filenames.
- Outputs
  - Files downloaded into `ingestion_dir` (no further processing or archiving in this component).
  - Logs and metrics indicating counts, durations, errors, and skipped files.
- Success Criteria
  - New, not-yet-ingested files within the expected time window are downloaded.
  - No duplicate downloads for files already recorded as ingested by DB service.
  - Errors are logged, and partial success is allowed; a single file failure does not fail the entire run.
- Error Modes
  - SharePoint list/download failure: log error, continue with next file; job returns successfully downloaded filenames.
  - DB service failure: job fails fast and surfaces the error (caller handles retries/backoff).
  - Filesystem errors (e.g., permission): log and continue when per-file; fail fast when directory creation not possible.

---

## Class & Function Structure

### 1. Scheduler

- **Class:** `Scheduler`
  - Loads schedule config from `settings.toml` (or environment overrides).
  - Registers and runs jobs using either:
    - Fixed interval (default; e.g., every 60 minutes), with optional jitter to avoid thundering herds.
    - Explicit daily times (e.g., 09:05, 12:05, 15:05, 18:05) in local time.
  - Prevents overlapping runs per job key (i.e., if a run is in progress, the next scheduled tick is skipped or queued based on config `allow_overlap: false` default).
  - Exposes a manual trigger that runs immediately, subject to overlap policy.
  - Handles graceful shutdown: stop scheduling new runs, optionally wait for in-flight runs (configurable timeout), then exit.
  - Emits structured logs and lightweight metrics (counters/timers) via standard logger; metrics can be extended later.

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
  - Contract: returns a list of filenames; does not raise for empty results; raises on connectivity/HTTP errors.

### 4. Job Logic

- **Class:** `SyncJob`
  - Orchestrates the end-to-end sync: authenticate, list, filter (already ingested), download, and place into `ingestion_dir`.
  - Retries per-file download failures up to `max_retries` with `retry_delay_seconds` backoff; DB list and SharePoint list are not retried by default (kept simple for now).
  - Skips files that are present in the DB service result for the time window; exact match on filename.
  - Returns the list of successfully downloaded filenames.

### 4. CLI Entrypoint

- **Function:** `main()`
  - Parses CLI arguments:
    - `run`: start the scheduler (interval/cron) and block until terminated.
    - `trigger`: run one `SyncJob` immediately (respecting overlap policy) and exit.
    - `run-once`: execute a single scheduled iteration and exit (testing/ops convenience).
  - Loads configuration, instantiates `Scheduler`, and performs the requested action.

---

## Example Flow

1. Scheduler wakes up on interval or at explicit time.
2. `SyncJob` authenticates with SharePoint/Graph API.
3. Queries the DB service for a list of already ingested files for the current time interval.
4. Lists files in the configured SharePoint directory.
5. Downloads only files that have not already been processed to the ingestion directory.
6. Logs all actions and errors.

Notes

- If overlapping is disabled (default), any tick while a run is still in progress is skipped with a warning log.
- Manual trigger respects overlap policy by default (configurable `force=true` to run concurrently if needed; default is false).

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
interval_minutes = 60               # Fixed interval mode (default)
quad_daily_times = ["09:05","12:05","15:05","18:05"]  # Optional explicit schedule
timezone = "local"                  # or IANA tz (e.g., "America/Chicago")
allow_overlap = false               # Prevent concurrent runs for the same job key
overlap_policy = "skip"            # "skip" (default) or "queue" (run immediately after current finishes)
shutdown_timeout_seconds = 30       # Max wait for in-flight jobs on shutdown
jitter_seconds = 0                  # Random jitter added to interval to avoid thundering herd
```

---

## TODO

- Implement function stubs for SharePoint/Graph API communication. For now, these should call sim service functions as placeholders. When ready to integrate the real API, replace the sim calls with actual SharePoint/Graph API logic.
- Implement a DB service client for querying already ingested files.
- Implement non-overlapping scheduling and interval/cron configuration.
- Implement graceful shutdown with in-flight job await and timeout.
- Ensure documentation and code clearly separate scheduler responsibilities from file watcher and DB service.
- Implement all classes and functions as described above.

---

## Observability

- Logging
  - `Scheduler`: start/stop, tick triggers, overlap-skipped events, manual triggers, shutdown start/complete.
  - `SyncJob`: start/end with duration, counts of files listed/skipped/downloaded, and per-file errors.
- Metrics (future-friendly; log-derived initially)
  - `scheduler.tick.count`, `scheduler.tick.skipped_overlap.count`.
  - `syncjob.download.success.count`, `syncjob.download.failure.count`.
  - `syncjob.duration.ms`.

---

## Testing Matrix

Current tests (green)

- Orchestration
  - `Scheduler.run_once` invokes `SyncJob.run` once. (tests/scheduler/test_scheduler.py)
  - `Scheduler.trigger` invokes `SyncJob.run` once. (tests/scheduler/test_scheduler.py)
- SyncJob behavior
  - Skips already ingested files (DB service). (tests/scheduler/test_scheduler.py)
  - Propagates SharePoint list errors. (tests/scheduler/test_scheduler.py)
  - Propagates DB service errors. (tests/scheduler/test_scheduler.py)
  - Handles empty file list, partial download failure. (tests/scheduler/test_scheduler_extra.py)
- Stubs/CLI/logging
  - Logging smoke, CLI entrypoint smoke, config loading stub. (tests/scheduler/test_scheduler_extra.py)

Planned tests (added as xfail scaffolds until implementation)

- Scheduling cadence and overlap
  - Interval tick triggers job and prevents overlap (skip or queue based on config).
  - Manual trigger while running respects overlap unless forced.
- Graceful shutdown
  - Shutdown waits for in-flight job up to timeout, then exits.

See `tests/scheduler/test_scheduler_timing.py` for xfail scaffolds.

---

> **Note:** This design ensures that when the sim service is dropped, only the SharePoint/Graph API client needs to be updated, minimizing refactor effort.
