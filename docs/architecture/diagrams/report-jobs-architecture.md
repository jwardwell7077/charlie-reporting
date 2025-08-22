# Report Jobs Architecture

This page visualizes the scheduler-driven Excel report generation using the DB Service.

## component diagram

```mermaid
flowchart LR
  UI[User UI/CLI] --> CFG[(TOML Config)]
  SCH[Scheduler] -->|reads| CFG
  SCH -->|POST /reports/jobs| DBAPI[(DB Service API)]
  SCH -->|GET /reports/jobs/{id}| DBAPI
  DBAPI --> WORKER[Report Worker]
  WORKER -->|write .xlsx| FS[(reports/)]
  SCH -->|verify| DBAPI
```

## sequence diagram

```mermaid
sequenceDiagram
  participant SCH as Scheduler
  participant CFG as TOML Config
  participant DB as DB Service (Report Jobs)
  participant FS as reports/

  SCH->>CFG: Load dataset columns and output dir/prefix
  SCH->>SCH: Compute ISO start/end
  SCH->>DB: POST /reports/jobs {dataset, start, end, format, columns, Interval Start/End, idempotency_key}
  DB-->>SCH: {job_id, status: queued}
  loop poll
    SCH->>DB: GET /reports/jobs/{job_id}
    DB-->>SCH: {status, filename?, row_count?}
  end
  SCH->>DB: GET /reports/files?dataset&from&to (optional)
  SCH->>FS: Verify file presence (optional)
```

## uml diagram (logical)

```mermaid
classDiagram
  class Scheduler {
    +loadConfig(): Config
    +computeWindow(job): (start,end)
    +submitJob(req): JobId
    +pollUntilComplete(jobId): JobStatus
    +verifyArtifact(JobStatus): bool
  }
  class ReportJobRequest {
    +dataset: str
    +start_time: str
    +end_time: str
    +format: str
    +columns: List~str~
    +interval_start_column: str
    +interval_end_column: str
    +idempotency_key: str
  }
  class DBReportJobsAPI {
    +createJob(ReportJobRequest): JobId
    +getJobStatus(JobId): JobStatus
    +listFiles(filter): List~ReportFile~
    +download(filename): bytes
  }
  class ReportWorker {
    +execute(jobId)
    -fetchRows(req): List~dict~
    -shape(rows, columns): DataFrame
    -writeXlsx(df, path): Path
  }
  class Config {
    +reports: Map~dataset, List~columns~~
    +output: {excel_dir, excel_prefix}
  }
  Scheduler --> DBReportJobsAPI
  Scheduler --> Config
  DBReportJobsAPI --> ReportWorker
  ReportWorker --> Config
```

## fsm diagrams

```mermaid
stateDiagram-v2
  direction LR
  state "Scheduler FSM" as SCH {
    [*] --> Idle
    Idle --> LoadConfig: schedule_tick | config_update
    LoadConfig --> ComputeWindow: config_ok
    LoadConfig --> Fail: config_error
    ComputeWindow --> SubmitJob: build idempotency_key
    SubmitJob --> Polling: submit.ok(job_id)
    SubmitJob --> Succeeded: submit.409(idempotent)
    SubmitJob --> BackoffWait: submit.5xx | submit.timeout
    SubmitJob --> Fail: submit.4xx
    BackoffWait --> SubmitJob: retry_left
    BackoffWait --> Fail: retry_exhausted
    Polling --> VerifyArtifact: job.succeeded
    Polling --> BackoffWait: job.running | poll.timeout
    Polling --> Fail: job.failed
    VerifyArtifact --> Succeeded: file_ok
    VerifyArtifact --> BackoffWait: file_missing | meta_mismatch
  }

  state "DB Report Job FSM" as DBJ {
    [*] --> Queued
    Queued --> Running: worker_claims
    Running --> Succeeded: xlsx_written & metadata_recorded
    Running --> Failed: error
    Queued --> Succeeded: idempotency_hit
  }
```
