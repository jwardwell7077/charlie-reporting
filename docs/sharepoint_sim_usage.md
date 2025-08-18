curl -O "<http://localhost:8001/sim/download/ACQ__2025-08-17_0900.csv>"

# SharePoint CSV Simulator: Usage & API Guide

## Overview

The SharePoint CSV Simulator is a deterministic, test-data generator and mock SharePoint CSV export service. It is implemented as a FastAPI app and can be run as a standalone server or mounted at `/sim` in the main API.

- **Deterministic:** Seeding ensures repeatable output for tests.
- **Configurable:** Control output directory, timezone, and seed via `config/sharepoint_sim.toml`.
- **Dataset Coverage:** ACQ, Productivity, Dials, IB_Calls, QCBS, RESC, Campaign_Interactions.

## Launching the Simulator

### Standalone Server

```bash
python -m sharepoint_sim.server
```

- The server will start on `http://localhost:8001` by default.
- Configuration is read from `config/sharepoint_sim.toml`.

### As Part of Main API

The simulator is mounted at `/sim` in the main FastAPI app. All endpoints below are available at `/sim/...`.

## API Endpoints

- `POST /sim/generate?types=ACQ,Productivity&rows=25`  
  Generate one or more datasets. Returns filenames.
- `GET /sim/files`  
  List all generated files.
- `GET /sim/download/{filename}`  
  Download a generated CSV file.
- `POST /sim/reset`  
  Delete all generated files.

### Example: Generate and Download

```bash
curl -X POST "http://localhost:8001/sim/generate?types=ACQ,Productivity&rows=25"
curl -O "http://localhost:8001/sim/download/ACQ__2025-08-17_0900.csv"
```

## Configuration

Edit `config/sharepoint_sim.toml`:

```toml
seed = 12345           # (optional) for deterministic output
output_dir = "sharepoint_sim"  # where generated CSVs are written
timezone = "UTC"       # currently only UTC supported
```

## Testing & Coverage

- Run all tests: `pytest --cov=src/sharepoint_sim tests/sim/`
- 100% line and docstring coverage is enforced (see `pyproject.toml` for settings).
- Property-based and edge-case tests are included for all dataset generators and error branches.

## Implementation Notes

- All datasets use a shared clock for deterministic timestamps.
- Row counts are bounded [10, 1000].
- Role and header rules are enforced per dataset spec.
- See `docs/sharepoint_sim_spec_addendum.md` for invariants and edge-case handling.

## Extending

- Add new datasets by subclassing `DatasetGenerator` in `datasets/base.py`.
- Register new types in `service.py`.

---

For full architectural and testing rationale, see `docs/sharepoint_sim_spec_addendum.md` and `docs/testing-approach.md`.
