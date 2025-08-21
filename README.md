# Charlie Reporting (Lean Foundation Restart)

[![Quality Gate](https://github.com/jwardwell7077/charlie-reporting/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/jwardwell7077/charlie-reporting/actions/workflows/quality-gate.yml)

This repository has been reset to a **minimal, configurable reporting foundation** focused on:

* Ingesting SharePoint‑exported CSV drops

# Charlie Reporting (Lean Foundation Restart)

[![Quality Gate](https://github.com/jwardwell7077/charlie-reporting/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/jwardwell7077/charlie-reporting/actions/workflows/quality-gate.yml)

This repository has been reset to a minimal, configurable reporting foundation focused on:

* Ingesting SharePoint‑exported CSV drops
* Loading data into a lightweight local SQLite store
* Generating hourly and quad‑daily Excel/HTML outputs
* Preparing for later email distribution and real SharePoint / Graph API integration

Historic microservice code has been pruned (kept in prior Git history). Documentation and configuration files remain for reference/value.

## Current Core

```text
foundation/
 README.md              # Detailed foundation architecture
 pyproject.toml         # Isolated tooling + deps (FastAPI, pandas, etc.)
 src/
  config/settings.py   # TOML settings loader (schedules, sources, columns)
  pipeline/            # collector | loader | aggregator | excel
  services/            # sharepoint_stub.py | api.py (FastAPI)
 tests/
  test_settings.py
config/
 settings.toml          # Active foundation configuration (new)
 config.toml            # Legacy (phase 2) email + attachment config (retained)
data/ (sample CSVs kept)
docs/ (original documentation preserved)
```

The repository includes a lightweight SharePoint CSV simulator (deterministic test data generator) under `sharepoint_sim` with FastAPI endpoints mounted at `/sim`.

## SharePoint CSV Simulator Testing

All dataset generators are covered by property-based tests (using Hypothesis) that verify:

* Header and schema invariants
* Role enforcement
* Value ranges and edge cases
* Row count clamping

Edge-case and regression tests are included for all error branches and invariants. See `tests/sim/` for details.

## SharePoint CSV Simulator Usage

The simulator is mounted at `/sim` in the main API. Example endpoints:

* `POST /sim/generate?types=ACQ,Productivity&rows=25` — generate one or more datasets
* `GET /sim/files` — list generated files
* `GET /sim/download/{filename}` — download CSV
* `POST /sim/reset` — clear generated files

Simulator configuration: edit `config/sharepoint_sim.toml`:

```toml
# config/sharepoint_sim.toml
seed = 12345  # (optional) for deterministic output; omit for random
output_dir = "sharepoint_sim"  # where generated CSVs are written
timezone = "UTC"  # currently only UTC supported
```

Files are named `<DATASET>__YYYY-MM-DD_HHMM.csv` (5‑minute UTC rounding) and retained until reset.

## Configuration Overview

Active runtime configuration now lives in `config/settings.toml` (see populated example in repo). Key sections:

* `[schedules]` – hourly interval + explicit quad‑daily times
* `[data_sources]` / `[[data_sources.sources]]` – list of named CSV patterns to ingest
* `[collector]` – input (SharePoint dump), staging, archive directories
* `[report]` – output directory, workbook name, per‑source column whitelists
* `[email]` – (placeholder) future outbound email metadata

Legacy `config/config.toml` provided email folder filters and per‑file column selections. These have been mapped forward:

| Legacy Section | New Mapping |
|----------------|-------------|
| `[attachments]` filename → columns | `[report.columns]` source name → columns (source name = lowercased filename stem) |
| `output.excel_dir` | `report.output_dir` |
| `output.archive_dir` | `collector.archive_dir` |
| `directory_scan.scan_path` | `collector.input_root` |

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e foundation

# Run API (inside venv)
python -m foundation.src.services.api
```

Generate an hourly workbook via API:

```bash
curl -X POST http://localhost:8000/ingest
curl -X POST http://localhost:8000/generate/hourly
```

## Dev Servers (Simulator, DB API, Scheduler)

A convenience runner is available to launch the local FastAPI dev servers for components that expose an API:

* SharePoint Simulator API: <http://127.0.0.1:8001> (module: `sharepoint_sim.server:app`)
* DB Service API: <http://127.0.0.1:8002> (module: `db_service_api:app`)
* Scheduler Control API: <http://127.0.0.1:8003> (module: `scheduler_api:app`)

Usage (from repo root, inside the venv):

```bash
python scripts/run_dev_servers.py              # start all
python scripts/run_dev_servers.py --sim        # only simulator
python scripts/run_dev_servers.py --db --sched # db + scheduler
```

Preflight checks performed:

* Ensures `uvicorn` is installed in the active environment; exits with a helpful message if missing.
* Verifies ports 8001/8002/8003 (or selected ones) are free on 127.0.0.1 before starting.
* Verifies the SQLite path `./db_service.sqlite3` is writable when starting the DB API.

Security: For now, these dev servers run without auth and bind to localhost. Do not expose them to untrusted networks.

Config file (optional): `config/dev_servers.toml`

```toml
[dev_servers]
host = "127.0.0.1"  # override bind host
sim_port = 8001
db_port = 8002
sched_port = 8003
run = ["sim", "db", "sched"]  # default set when no flags are provided
```

CLI flags override config: `--host`, and `--sim/--db/--sched` control selection.

## Quality Gate and Tooling

Strict gate (local and CI): Ruff (lint/format), mypy (strict), Pyright (strict), pydoclint, interrogate (100% doc coverage), pytest (100% line coverage enforced). Test files are included in Ruff, mypy, and Pyright runs to keep helper code quality aligned with production modules.

Run locally:

```bash
scripts/quality_gate.sh
```

Pre-commit (`pre-commit install`) runs Ruff, mypy subset, Pyright, and a quick pytest smoke.

## CI

Workflow `.github/workflows/quality-gate.yml` enforces the gate on pushes and PRs to `main` and `main-foundation`.

## Development Principles

We adhere to a core design principle: Minimal Entry / Minimal Exit.

> Each component exposes the fewest necessary public entry points and leaves every object or return value in a fully validated, deterministic state immediately upon exit—no redundant wrapper layers or deferred hidden side effects.

Examples:

* `Roster` self-loads on construction (optional `from_csv` classmethod) — removed former `load_roster()` wrapper.
* Dataset generators expose a single `build()` path instead of scattered helper functions.
* Service orchestration keeps state explicit (roster, RNG, storage) with no hidden globals.

See `docs/development_principles.md` for rationale, review checklist, and contribution guidelines.

## Baseline Tag

Tag the stabilized foundation:

```bash
git checkout main-foundation
git tag -a v0.2.0-foundation -m "Foundation quality gate baseline"
git push origin v0.2.0-foundation
```

## Roadmap (Near Term)

1. Expand tests (failure paths, loader idempotency, error cases)
2. Add scheduler (APScheduler) hourly and quad‑daily triggers
3. Implement email packaging (HTML inline and attachment)
4. Extend loader (additional sources, ingestion_log semantics)
5. Structured logging and metrics stub
6. Replace stub with Graph API SharePoint ingestion pipeline

## Contributing / Historical Docs

All prior architecture rationale, migration notes, and phase achievements remain under `docs/`.

## Diagrams

* [Architecture Overview (Mermaid)](docs/architecture/diagrams/architecture-overview.md)
* [Service Boundaries (Mermaid)](docs/architecture/diagrams/service-boundaries.md)
* [Component: Collector](docs/architecture/diagrams/component-collector.md)
* [Component: Loader](docs/architecture/diagrams/component-loader.md)
* [Component: Aggregator](docs/architecture/diagrams/component-aggregator.md)
* [Component: Excel/HTML Generator](docs/architecture/diagrams/component-excel.md)
* [Component: API](docs/architecture/diagrams/component-api.md)
* [Component: Simulator](docs/architecture/diagrams/component-simulator.md)

### UML (Mermaid)

* [UML Class: Foundation](docs/architecture/diagrams/uml/class-foundation.md)
* [UML Sequence: Ingest Flow](docs/architecture/diagrams/uml/sequence-ingest.md)
* [UML Sequence: Generate Hourly Report](docs/architecture/diagrams/uml/sequence-generate-hourly.md)
* [UML Sequence: Simulator Generate](docs/architecture/diagrams/uml/sequence-simulator-generate.md)

### Architecture Overview (inline)

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

## License

Proprietary / internal (adjust as needed). Add explicit license if distribution scope changes.

---

For deeper architectural description see `foundation/README.md`.
