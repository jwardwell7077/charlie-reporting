# Design Spec: Ingestion Log & Idempotent Loader

Date: 2025-08-15

Status: Draft (pre-test)

Owner: JW

Related Backlog Items: ingestion_log, run_history integration

## 1. Purpose

Provide **idempotent, observable ingestion** of staged CSV files so that re-running ingestion does not duplicate rows and each file's processing status (success / error / skipped) is recorded with basic metrics.

## 2. Scope

In Scope:

- `ingestion_log` table (schema, constraints)
- File hash based duplicate detection (sha256 streamed)
- Class-based loader orchestration (replace procedural functions)
- Integration with `run_history` (start/end + counts)
- Basic structured logging events (key=value) for ingest stages

Out of Scope (future):

- Parallel ingestion
- Partial file retry logic
- Metrics export (Prometheus)
- Email notifications

## 3. Data Model

### ingestion_log

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Identity |
| file_name | TEXT | Leaf filename (no dirs) |
| file_path | TEXT | Absolute or relative path at ingest time |
| file_hash | TEXT UNIQUE | sha256 hex digest of file content |
| size_bytes | INTEGER | File size in bytes |
| loaded_at | TEXT | UTC ISO timestamp when completed (success or error) |
| rows_ingested | INTEGER | Rows written to target table(s) |
| status | TEXT | running / success / error / skipped |
| error | TEXT NULL | Short error summary if status=error |

### run_history usage

- Use existing `run_history` table; one row for each ingest invocation (even if zero files).
- `files_found`, `files_loaded`, `rows_ingested`, `failed_files` updated upon completion.

## 4. Class Design

```text
+------------------+        +------------------------+
| FileHasher       |        | IngestionLogRepository |
|------------------|        |------------------------|
| +hash(path)->str |        | +ensure_schema()       |
| (sha256 stream)  |        | +already_seen(hash)->? |
+------------------+        | +start_entry(meta)->id |
             |              | +mark_success(id, rows)|
             |              | +mark_error(id, err)   |
             v              | +mark_skipped(meta)    |
+------------------+        +------------------------+
| LoaderService    |              ^
|------------------|              |
| +ingest_all()    | uses         |
| +_ingest_file()  +--------------+
| (coordinates)    |
+------------------+
            uses
            v
+------------------+
| RunTracker       |
|------------------|
| +start(run_type) |
| +finish(...)     |
+------------------+
```

### Responsibilities

- `FileHasher`: Pure utility (stateless) calculates sha256.
- `IngestionLogRepository`: DB operations for ingestion_log and duplicate detection.
- `RunTracker`: Wrapper around existing run_history helpers.
- `LoaderService`: High-level orchestration: discover staged files, attempt ingest, update ingestion_log & run_history, aggregate counts.

All external code will call `LoaderService.ingest_all()`; no direct table manipulation.

## 5. Sequence Flow (Single Run)

```text
User/API triggers ingest
  -> RunTracker.start("ingest") returns run_id
  -> LoaderService lists staging_dir for patterns (via Settings.data_sources)
  For each file:
     -> hash = FileHasher.hash(path)
     -> repo.already_seen(hash)?
          yes -> repo.mark_skipped(meta); increment skipped count
          no  -> entry_id = repo.start_entry(meta,status=running)
                  try load rows -> repo.mark_success(entry_id, rows)
                  except Exception e -> repo.mark_error(entry_id,str(e)); failed++
  -> RunTracker.finish(run_id, counts, status=success|partial|error)
  -> Return summary dict
```

## 6. Error Modes

| Scenario | Detection | Handling | Log Event | ingestion_log.status | run_history.status Impact |
|----------|-----------|----------|-----------|----------------------|----------------------------|
| Duplicate file (same hash) | already_seen(hash) | Skip ingest | stage=loader action=skip file=... | skipped | success (if no other failures) |
| CSV read error | Exception while iterating rows | Catch, mark error | stage=loader action=error file=... err=... | error | partial (if others ok) or error (if all failed) |
| Empty file | Reader has zero rows | Mark success rows=0 | stage=loader action=success rows=0 | success | success |
| DB write error | sqlite3.Error | Catch, mark error | action=error | error | partial/error |

Status Resolution for Run:

- If any successful loads and any failures -> `partial`.
- If all failures -> `error`.
- Else -> `success`.

## 7. Success Criteria / Assertions (used by tests)

1. First ingest of file inserts one row in target table + ingestion_log row (status=success, rows_ingested>0 or =0 if empty).
2. Re-ingest without modification: no additional productivity rows; ingestion_log gets a new row with status=skipped OR (optionally) reuse existing row (decision: create new row? -> Decision: create *no* new row for skip, but log skip event). Simpler: maintain log history? Choose: **Insert a new ingestion_log row with status=skipped for traceability.**
3. Modified file (content differs) ingests again and creates new success row (different hash) + added data (separate test ensures counts reflect additional rows).
4. Corrupt CSV results in ingestion_log row with status=error and error text substring.
5. run_history row aggregates counts correctly (files_found, files_loaded, failed_files, rows_ingested sum).
6. LoaderService returns dict summary with keys: files_found, files_loaded, skipped, failed, rows_ingested, run_id.

## 8. Test Matrix

| Test ID | Focus | Setup | Expected |
|---------|-------|-------|----------|
| T1 | Success ingest | 1 valid CSV | ingestion_log success row; productivity rows inserted |
| T2 | Duplicate skip | Same ingest twice | Second run logs skip entries, no new productivity rows |
| T3 | Content change | Modify file (append row) | Second run processes again; new ingestion_log success row; delta rows appended |
| T4 | Corrupt file | Truncate file mid-line | ingestion_log error; run_history.status partial |
| T5 | Empty file | 0-row CSV (header only) | success rows_ingested=0 |
| T6 | Aggregate counts | Mix success/skip/error | run_history counts accurate |

## 9. Open Decisions (Record Here)

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Skip row creation? | Create skip rows | Provides audit trail |
| Hash algorithm | sha256 | Stdlib, input files small (<1MB) |
| Status partial vs success when errors + skips only | partial if any error | Clarity |

## 10. Implementation Notes

- Use single sqlite connection per ingest run for efficiency; pass to collaborators.
- Wrap each file load in its own transaction (BEGIN/COMMIT) for isolation; rollback on error.
- Ensure schema creation idempotent in repository `ensure_schema()`.
- Consider index on (file_name, loaded_at) only if needed later.

## 11. Refactoring Plan (Procedural -> OOP)

Current modules (`collector.py`, `loader.py`) are procedural; they will be refactored *incrementally*:

- Introduce new classes in separate modules (`core/ingestion.py` or similar).
- Keep legacy functions delegating to new classes until callers updated.
- Remove old functions once tests pass on class-based path.

## 12. Deliverables Checklist (Gate)

- [ ] Spec file merged (this document)
- [ ] Unit tests for FileHasher + IngestionLogRepository behaviors (duplicate detection, status updates)
- [ ] Integration tests covering matrix T1–T6
- [ ] LoaderService implemented with classes only
- [ ] Existing procedural ingest path removed or wrapped
- [ ] Docs updated (`api_overview.md` if endpoint changes; `foundation-overview.md` if architecture updated)

## 13. Acceptance

Feature accepted when all success criteria met, all tests green, and no ruff/mypy issues introduced.

---
(End of spec)
