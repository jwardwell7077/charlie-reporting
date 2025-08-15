# Charlie Reporting (Lean Foundation Restart)

This repository has been reset to a **minimal, configurable reporting foundation** focused on:

* Ingesting SharePoint‑exported CSV drops
* Loading data into a lightweight local SQLite store
* Generating hourly and quad‑daily Excel/HTML outputs
* Preparing for later email distribution & real SharePoint / Graph API integration

Historic microservice code has been pruned (kept in prior Git history). Documentation & configuration files remain for reference/value.

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

## Configuration Overview

Active runtime configuration now lives in `config/settings.toml` (see populated example in repo). Key sections:

* `[schedules]` – hourly interval + explicit quad‑daily times
* `[data_sources]` / `[[data_sources.sources]]` – list of named CSV patterns to ingest
* `[collector]` – input (SharePoint dump), staging, archive directories
* `[report]` – output directory, workbook name, per‑source column whitelists
* `[email]` – (placeholder) future outbound email metadata

Legacy `config/config.toml` provided email folder filters & per‑file column selections. These have been **mapped forward**:

| Legacy Section | New Mapping |
|----------------|-------------|
| `[attachments]` filename → columns | `[report.columns]` source name → columns (source name = lowercased filename stem) |
| `output.excel_dir` | `report.output_dir` |
| `output.archive_dir` | `collector.archive_dir` |
| `directory_scan.scan_path` | `collector.input_root` |
| `email.sender[0]` | `email.from` |
| `email.subject_contains[0]` | `email.subject_template` (placeholder) |

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # root (global tooling) if still used
pip install -e foundation         # optional editable install of foundation package

# Run API (inside venv)
python -m foundation.src.services.api
```

Generate an hourly workbook via API (example):

```bash
curl -X POST http://localhost:8000/ingest
curl -X POST http://localhost:8000/generate/hourly
```

## Roadmap (Near Term)

1. Add scheduler (APScheduler) harness for hourly + quad‑daily triggers
2. Implement email packaging (HTML inline + attachment) using configured sheet list
3. Extend loader to additional sources & enforce idempotent ingestion tracking
4. Introduce metrics & lightweight logging format
5. Replace stub with Graph API SharePoint ingestion pipeline

## Contributing / Historical Docs

All prior microservices architecture rationale, migration notes, and phase achievements remain under `docs/` for portfolio storytelling. Use `git log` or GitHub history to view removed code.

## License

Proprietary / internal (adjust as needed). Add explicit license file if distribution requirements change.

---
This README intentionally reflects the lean restart state; for deeper architectural description see `foundation/README.md`.
