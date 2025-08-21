# Scheduler and File Watcher Integration – Updated Spec

## Key Responsibilities

### Scheduler

- **Purpose:**
  - Authenticate with SharePoint/Graph API and download new files from a configured SharePoint directory to the local ingestion directory on a schedule.
- **Does NOT handle:**
  - Idempotency (duplicate file tracking)
  - Archiving or moving processed files

### File Watcher (FileConsumer)

- **Purpose:**
  - Monitors the ingestion directory for new files.
  - Handles idempotency: tracks which files have been processed (in memory, DB, or persistent store).
  - Processes and sends file data to the DB service.
  - Moves processed files to the archive directory.

### DB Service

- **Purpose:**
  - Optionally, can also track ingested files for full pipeline idempotency.

## Updated Integration Flow

1. **Scheduler** downloads new files from SharePoint/Graph API to the ingestion directory (no tracking or archiving).
2. **File Watcher** detects new files, checks if they have been processed, sends data to DB, and moves them to the archive directory.
3. **DB Service** ingests data and (optionally) tracks file ingestion for audit or deduplication.

## Documentation Update Note

- Idempotency and file tracking are handled by the File Watcher (and/or DB service), NOT the scheduler.
- Scheduler is responsible only for fetching and placing files in the ingestion directory.
- File archiving is the responsibility of the File Watcher.

---

> **Action:** Update all relevant documentation and specs to reflect this separation of concerns.
