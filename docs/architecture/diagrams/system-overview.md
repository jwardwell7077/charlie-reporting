# System Overview

This diagram shows the end-to-end flow between the Scheduler, SharePoint Simulator, File Consumer, and DB Service.

```mermaid
flowchart TB
  subgraph External
    SIM[SharePoint Simulator API]
  end

  subgraph Services
    S[Scheduler]
    CON[File Consumer]
    DBAPI[DB Service API]
  end

  S -->|GET ingestion_log (ISO window)| DBAPI
  S -->|GET files| SIM
  S -->|GET download/{file}| SIM
  S -->|write CSV| FS[(Ingestion Dir)]

  FS --> CON
  CON -->|Insert per-dataset rows| DBAPI
  CON -->|Log ingestion| DBAPI
```

Related documents:

- Report Jobs Architecture: report-jobs-architecture.md
- Report Jobs Design Spec: ../../design-specs/reporting/report_jobs_spec.md
