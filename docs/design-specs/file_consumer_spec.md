# File Consumer Component Design Spec

**Location:** `src/consumer/file_watcher.py`

## Purpose

A robust, scheduler-driven component that:

- Monitors a directory for new SharePoint CSV files
- Tracks which files have been processed
- Archives files after successful processing
- Sends file contents to the DB service
- Handles errors, retries, and logging

## Requirements

### Inputs

- **Input directory:** Path to watch for new files (configurable)
- **Archive directory:** Path to move processed files (configurable)
- **DB service endpoint/config:** How to send data (API or direct DB)
- **Scheduler integration:** Exposed function for periodic invocation

### Behavior

- On each run:
  1. List all files in the input directory
  2. For each unprocessed file:
     - Validate file (extension, schema)
     - Send to DB service
     - On success, move to archive
     - On failure, log and optionally quarantine
  3. Track processed files (in-memory, file, or DB)
- Log all actions and errors
- Expose a function for the scheduler to call

### Error Handling

- Retry or quarantine on failure
- Log errors and optionally alert

### Extensibility

- Easy to add new file types or DB targets
- Configurable polling interval, directories, and DB endpoint

## Interfaces

### Main Class: `FileConsumer`

- `__init__(input_dir, archive_dir, db_service, tracker=None, logger=None)`
- `consume_new_files()` — main entry point for scheduler
- `process_file(path)` — process a single file
- `archive_file(path)` — move file to archive
- `send_to_db(data)` — send parsed data to DB service
- `validate_file(path)` — check extension/schema

### Tracker

- Tracks processed files (default: local file or in-memory)

### Logger

- Standard logging, with info and error levels

## Example Usage

```python
from consumer.file_watcher import FileConsumer
consumer = FileConsumer(input_dir="sharepoint_sim/", archive_dir="archive/", db_service=MyDBService())
consumer.consume_new_files()
```

## Out of Scope

- Real-time file watching (use polling)
- UI or CLI (can be added later)

## Testing

- Unit tests for file detection, archiving, DB send, error handling
- Integration test with mock DB service

---
**Review and approve this spec before writing tests or implementation.**
