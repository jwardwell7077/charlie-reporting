# Architecture Overview

This document provides a high-level view of the foundation architecture and data flow.

```mermaid
flowchart LR
  %% External actors and sources
  subgraph External
    SP["SharePoint (CSV exports)"]
    Operator["Operator / API Client"]
  end

  %% Foundation components
  subgraph Foundation
    direction LR
    Collector[["Collector\n(move + stage + archive)"]]
    Staging[("Staging Dir")]
    Archive[("Archive Dir")]

    Loader[["Loader\n(parse CSV → rows)"]]
    DB[("SQLite DB")]

    Aggregator[["Aggregator\n(group + compute metrics)"]]
    ExcelGen[["Excel/HTML Generator"]]

    API[("FastAPI /main API/")]
    Sim[("SharePoint CSV Simulator (/sim)")]
  end

  %% Flows
  SP -->|CSV drops| Collector
  Collector -->|stage| Staging
  Collector -->|archive| Archive
  Collector --> Loader
  Loader --> DB
  DB --> Aggregator
  Aggregator --> ExcelGen

  Operator -->|trigger ingest/generate| API
  API -->|orchestrates| Collector
  API -->|orchestrates| Aggregator
  API -->|orchestrates| ExcelGen

  %% Simulator path
  Operator -->|generate sample data| Sim
  Sim -->|write CSVs| Staging
  Staging -.-> |picked up by| Collector
```

Legend:

- External systems on the left; internal components grouped as “Foundation.”
- The API exposes endpoints to generate sample CSVs (via the simulator), trigger ingest, and produce reports.
- The collector moves files from the input root into staging and archive, then the loader parses for storage; aggregation and report generation follow.
