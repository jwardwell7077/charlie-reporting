# Charlie Reporting (Lean Foundation Restart)

[![Quality Gate](https://github.com/jwardwell7077/charlie-reporting/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/jwardwell7077/charlie-reporting/actions/workflows/quality-gate.yml)

This repository is a minimal, configurable reporting foundation focused on:

* Ingesting SharePoint‑exported CSV drops
* Loading data into a lightweight local SQLite store
* Generating hourly and quad‑daily Excel/HTML outputs
* Preparing for later email distribution and Graph API integration

Historic microservice code was pruned (kept in prior Git history). Documentation and configuration files remain for reference/value.

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

## SharePoint CSV Simulator Testing

All dataset generators are covered by property-based tests (using Hypothesis) that verify:

* Header and schema invariants
* Role enforcement
* Value ranges and edge cases
* Row count clamping

Edge-case and regression tests are included for all error branches and invariants. See `tests/sim/` for details.

## SharePoint CSV Simulator Usage

Simulator is mounted at `/sim` in the main API. Example endpoints:

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

Active runtime configuration lives in `config/settings.toml` (see populated example). Key sections:

* `[schedules]` – hourly interval + explicit quad‑daily times
* `[data_sources]` / `[[data_sources.sources]]` – list of named CSV patterns to ingest
* `[collector]` – input (SharePoint dump), staging, archive directories
* `[report]` – output directory, workbook name, per‑source column whitelists
* `[email]` – (placeholder) future outbound email metadata

Legacy `config/config.toml` folder filters and per‑file column selections are mapped forward:

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

## Quality Gate and Tooling

Strict gate (local & CI): Ruff (lint/format), mypy (strict), Pyright (strict), pydoclint, interrogate (100% doc coverage), pytest (100% line coverage enforced). Test files are included in Ruff, mypy, and Pyright runs.

Run locally:

```bash
scripts/quality_gate.sh
```

Pre-commit (`pre-commit install`) runs Ruff, mypy subset, Pyright, quick pytest smoke.

## CI

Workflow `.github/workflows/quality-gate.yml` enforces the gate on pushes/PRs to `main` and `main-foundation`.

## Development Principles

We adhere to a core design principle: Minimal Entry / Minimal Exit.

> Each component exposes the fewest necessary public entry points and leaves every object or return value in a fully validated, deterministic state immediately upon exit—no redundant wrapper layers or deferred hidden side effects.

Examples:

* `Roster` self-loads on construction (optional `from_csv` classmethod) — removed former `load_roster()` wrapper.
* Dataset generators expose a single `build()` path instead of scattered helpers.
* Service orchestration keeps state explicit (roster, RNG, storage) with no hidden globals.

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

Proprietary/internal (adjust as needed). Add explicit license if distribution scope changes.

---
For deeper architectural description see `foundation/README.md`.
