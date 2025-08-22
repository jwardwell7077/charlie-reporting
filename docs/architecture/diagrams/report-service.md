# Component: Report Service

Generates tabular reports (CSV/XLSX) by querying the DB Service API.

```mermaid
flowchart LR
  RS[Report Service API] -->|GET /tables/{dataset}/rows| DB[DB Service API]
  RS -->|writes CSV/XLSX| FS[(reports/)]
  C[Client/Operator] -->|POST /reports/generate| RS
  C -->|GET /reports| RS
  C -->|GET /reports/download/{file}| RS
```

```mermaid
sequenceDiagram
  participant C as Client
  participant RS as Report Service API
  participant DB as DB Service API
  participant FS as File System (reports/)

  C->>RS: POST /reports/generate { dataset, start, end, format }
  RS->>DB: GET /tables/{dataset}/rows?start_time&end_time
  DB-->>RS: JSON rows
  RS->>FS: write CSV/XLSX
  RS-->>C: 200 { filename, path, row_count }
  C->>RS: GET /reports/download/{filename}
  RS-->>C: File bytes
```
