# Component: API (FastAPI)

```mermaid
This repository exposes two FastAPI apps:
- SharePoint Simulator API (test data generation and file listing/download)
- DB Service API (table/row CRUD, CSV ingest, time-window filtering via ISO timestamps)

## Simulator API surface

```mermaid
flowchart LR
  C[Client / Tests] -->|POST /sim/generate| SIM[(Simulator)]
  C -->|GET /sim/spec| SIM
  C -->|GET /sim/files| SIM
  C -->|GET /sim/download/{filename}| SIM
  C -. optional .->|POST /sim/reset| SIM
```

## DB Service API surface

```mermaid
flowchart LR
  C[Client / Scheduler / Consumer / Tests] -->|GET /health| DBAPI[(DB Service API)]
  C -->|POST /tables| DBAPI
  C -->|GET /tables| DBAPI
  C -->|GET /tables/{table}/schema| DBAPI
  C -->|DELETE /tables/{table}| DBAPI
  C -->|POST /tables/{table}/rows| DBAPI
  C -->|GET /tables/{table}/rows?start_time&end_time&timestamp_column&columns| DBAPI
  C -->|DELETE /tables/{table}/rows/{id}| DBAPI
  C -->|PUT /tables/{table}/rows/{id}| DBAPI
  C -->|POST /ingest (CSV or JSON rows)| DBAPI
```

Notes:

- Time-window filtering is lexical on ISO 8601 strings (e.g., 2025-08-20T11:00:00+00:00).
- ingestion_log is a first-class table used by the scheduler to determine already ingested filenames.

## End-to-end API touchpoints

```mermaid
sequenceDiagram
  participant S as Scheduler
  participant SIM as SharePoint Simulator API
  participant DB as DB Service API
  participant CON as File Consumer

  S->>DB: GET /tables/ingestion_log/rows?start_time&end_time&timestamp_column=ingested_at&columns=filename
  DB-->>S: [already ingested filenames]
  S->>SIM: GET /sim/files
  SIM-->>S: [available filenames]
  loop for each new file
    S->>SIM: GET /sim/download/{filename}
    SIM-->>S: CSV bytes
    S->>CON: place file in ingestion dir
    CON->>DB: POST /tables/{dataset}/rows (batched inserts)
    CON->>DB: POST /tables/ingestion_log/rows { filename, dataset, ingested_at }
  end
```

```markdown
````
