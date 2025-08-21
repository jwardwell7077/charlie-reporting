# Integration Pipeline TODOs

The following work is required to achieve a fully automated, end-to-end integration pipeline for Charlie Reporting:

## Outstanding Work

1. **Scheduler Implementation**
   - Implement a scheduler/orchestrator that triggers the SharePoint simulator to generate files on a schedule (e.g., every N minutes).
   - Scheduler should call the simulator's `/sim/generate/all` endpoint (or similar) via HTTP.

2. **File Watcher Integration**
   - Ensure the `FileConsumer` is invoked after new files are generated, to process and ingest them into the DB service.
   - Integrate the file watcher with the scheduler, or run it as a persistent service.

3. **End-to-End Integration Test**
   - Write a test or script that:
     1. Triggers the simulator to generate files.
     2. Runs the file consumer to process those files.
     3. Verifies the data is ingested into the DB.

4. **Service Wiring**
   - Ensure all services (simulator, file watcher, DB service) can be started and orchestrated together, either via scripts or a unified entrypoint.

5. **Documentation**
   - Document the integration pipeline, scheduler configuration, and how to run the full workflow locally and in production.

---

# Scheduler Design Spec (Draft)

## Purpose

Automate the generation of simulated SharePoint CSV files on a schedule, triggering downstream ingestion and DB population.

## Requirements

- Configurable schedule (interval, cron, etc.)
- Triggers the SharePoint simulator's `/sim/generate/all` endpoint
- Handles errors and retries
- Logs all actions and errors
- Optionally notifies or triggers the file consumer after generation

## Proposed Design

- **Language:** Python
- **Scheduling Library:** `schedule` or `APScheduler`
- **Trigger:** HTTP POST to simulator endpoint
- **Config:** YAML or TOML for schedule and endpoint settings
- **Logging:** Standard Python logging
- **Error Handling:** Retry with backoff, log failures

## Example Flow

1. Scheduler wakes up on interval
2. Sends POST to `/sim/generate/all` (optionally with row count)
3. Waits for file generation to complete
4. (Optional) Notifies or triggers file consumer to process new files
5. Logs success/failure

## Extensibility

- Support for multiple simulators or datasets
- Pluggable notification/trigger for downstream consumers
- CLI and config file support

---

> **Note:** This spec is a draft. Please review and expand as needed for your use case.
