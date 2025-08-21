# Service Boundaries

This diagram outlines boundaries between core subsystems and external actors.

```mermaid
flowchart TB
  %% External actors
  Client["Operator / API Client"]
  SharePoint["SharePoint (CSV source)"]

  %% Bounded contexts
  subgraph Ingestion[Ingestion]
    direction TB
    InCollector[[Collector]]
    InLoader[[Loader]]
  end

  subgraph Storage[Storage]
    DB[(SQLite)]
  end

  subgraph Reporting[Reporting]
    Agg[[Aggregator]]
    XGen[[Excel/HTML Generator]]
  end

  subgraph API[API Layer]
    FastAPI[(FastAPI)]
    Sim[(CSV Simulator)]
  end

  %% External interactions
  Client -->|calls| FastAPI
  SharePoint -->|drops CSV| InCollector

  %% Internal flows across boundaries
  FastAPI -->|orchestrates| InCollector
  InCollector --> InLoader
  InLoader --> DB
  DB --> Agg
  Agg --> XGen

  %% Simulator boundary
  Client -->|request sample data| Sim
  Sim -->|writes CSVs| InCollector
```

Notes:

- Each subgraph is a boundary with well-defined contracts.
- API is the sole entry point for orchestration; no direct cross-boundary calls.
- The simulator is optional and only writes CSVs that the ingestion boundary consumes.
