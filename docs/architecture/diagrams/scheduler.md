# Component: Scheduler

## Responsibilities

- Poll SharePoint Simulator for available files via HTTP.
- Query DB Service ingestion_log for already ingested filenames in a time window.
- Download only new files to the ingestion directory with retry/backoff.
- Provide optional interval scheduling (APScheduler) and a simple CLI.

## High-level flow

```mermaid
flowchart LR
  S[Scheduler] -->|GET /tables/ingestion_log/rows| DB[(DB Service API)]
  S -->|GET /sim/files| SIM[(SharePoint Simulator API)]
  S -->|GET /sim/download/{filename}| SIM
  S -->|write CSV| FS[(Ingestion Dir)]
  FS --> CON[File Consumer]
  CON -->|POST rows| DB
  CON -->|POST /tables/ingestion_log/rows| DB
```

## Sequence

```mermaid
sequenceDiagram
  participant S as Scheduler
  participant DB as DB Service API
  participant SIM as SharePoint Simulator API
  participant CON as File Consumer
  participant FS as Ingestion Dir

  S->>DB: query ingested filenames (ISO window)
  DB-->>S: filenames
  S->>SIM: list files
  SIM-->>S: filenames
  alt for each new file
    S->>SIM: download file
    SIM-->>S: csv
    S->>FS: save csv
    S->>CON: notify/process
    CON->>DB: insert rows into per-dataset table
    CON->>DB: log ingestion
  end
```
