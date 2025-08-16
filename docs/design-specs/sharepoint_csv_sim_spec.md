# Lean SharePoint CSV Simulation Specification

> Location moved from `docs/sharepoint_csv_sim_spec.md` into `docs/design-specs/` to align with existing design document structure.

## 1. Purpose

Provide a lightweight, fully testable simulation of a remote SharePoint (or similar) file drop that produces CSV files matching real production-like schemas. This enables end‑to‑end pipeline testing (fetch → transform → aggregate → export) without external dependencies and is trivial to swap out later.

## 2. Scope (Intentionally Minimal)

In scope:

* Deterministic generation of CSV data for the currently observed source types.
* FastAPI router exposing minimal endpoints to trigger generation and retrieve/list files.
* Role‑aware random assignment of employees to rows (with constraints by dataset type).
* Single seed input (optional) for reproducibility.
* No persistence beyond writing CSV files into a designated simulation “remote” directory (which tests can control / isolate).

Out of scope (explicitly deferred):

* Versioning, JSON index files, soft deletes.
* Complex metadata / audit trails.
* Failure / latency injection (can be added later if needed).
* Multi-tenancy or auth.
* Background scheduling (external orchestrator or tests will call the API directly).

## 3. Data Sources & Schemas (Derived from `sample_data/`)

The generator must emit exact headers, order preserved. Columns are treated as strings on write (allowing the pipeline to parse as needed). Existing samples show 1000 data rows plus header (we can parameterize row count).

### 3.1 ACQ

`Interval Start,Interval End,Interval Complete,Filters,Media Type,Agent Id,Agent Name,Handle`

### 3.2 Productivity

`Interval Start,Interval End,Interval Complete,Filters,Agent Id,Agent Name,Logged In,On Queue,Idle,Off Queue,Interacting`

### 3.3 QCBS

`Interval Start,Interval End,Interval Complete,Filters,Media Type,Agent Id,Agent Name,Handle`

### 3.4 RESC

`Interval Start,Interval End,Interval Complete,Filters,Media Type,Agent Id,Agent Name,Handle`

### 3.5 Campaign_Interactions

`Full Export Completed,Partial Result Timestamp,Filters,Users,Date,Initial Direction,First Queue`

### 3.6 Dials

`Interval Start,Interval End,Interval Complete,Filters,Media Type,Agent Id,Agent Name,Handle,Avg Handle,Avg Talk,Avg Hold,Avg ACW,Total Handle,Total Talk,Total Hold,Total ACW`

### 3.7 IB_Calls

`Interval Start,Interval End,Interval Complete,Filters,Media Type,Agent Id,Agent Name,Handle,Avg Handle`

## 4. Employee Roster Requirement

Generate (once per process start or on first request) a roster of 100 employees with:

* 40 Inbound agents
* 40 Outbound agents
* 20 Hybrid agents
* Each employee has: UUID (`employee_id`), `display_name`, `role` in {`inbound`, `outbound`, `hybrid`}.

### 4.1 Determinism Strategy

To maintain reproducibility while still “random”:

1. Use a fixed seed (default) OR caller‑supplied seed (query param / internal function argument) that seeds `random.Random(seed)`.
2. Build a name pool (two lists: first names, last names). Generate combinations until 100 unique names chosen.
3. Shuffle; assign first 40 as inbound, next 40 outbound, final 20 hybrid.
4. UUIDs generated via `uuid5(NAMESPACE_DNS, f"{name}-{role}")` for seed stability (so same seed → same IDs). Avoid uuid4 to keep deterministic outputs.

### 4.2 Role Selection Rules per Dataset

| Dataset | Eligible Roles | Notes |
|---------|----------------|-------|
| ACQ, RESC, IB_Calls, Productivity | inbound + hybrid | These represent inbound or general productivity metrics. |
| Dials, QCBS | outbound + hybrid | Outbound dialing or callback contexts. |
| Campaign_Interactions | all roles | Mixed / interaction log style. |

When building each row, select a random eligible employee uniformly from the subset matching rules.

### 4.3 Per-Row Employee Randomization (Added Requirement)

For every generated row the employee is independently sampled (uniformly) from the eligible role-filtered pool using the deterministic RNG instance. This ensures:

* Distribution over many rows approximates uniform usage of eligible employees.
* Re-running with the same seed yields identical sequence of employee selections, making snapshot tests stable.
* No caching of a fixed per-dataset subset—selection truly per-row.

## 5. Generation Model

Each dataset type has a generation function returning a list of row dicts (or directly writing rows). Shared helpers supply:

* `employee_pool.get(role_filter: set[str]) -> list[Employee]`
* `choose_employee(role_set)` — random choice with deterministic RNG.
* Time windows: Use provided interval start/end (default: a single 24h range matching samples) or parameterizable `--interval-start`, `--interval-end`.
* Numeric metrics: For count columns (e.g., `Handle`) choose small integers or floats mirroring magnitudes seen in samples; may scale with an optional `intensity` parameter.
* A single `seed` controls RNG for: roster generation (if not already cached) and per-dataset row content.

## 6. File Naming Convention

`<DATASET>__YYYY-MM-DD_HHMM.csv`

* Timestamp uses generation start time truncated to nearest 5 minutes (as observed in `demo/data/generated/`).
* Collision handling: overwrite (simple) OR if same minute & dataset exists, append `__n` (deferred; default overwrite to keep minimal scope).

## 7. Directory Layout (Proposed)

```text
src/sharepoint_sim/
  __init__.py
  generator.py          # Core generation logic (per dataset functions)
  employees.py          # Roster creation & caching (deterministic)
  api.py                # FastAPI router exposing endpoints
  types.py              # (Optional) TypedDict / dataclasses (keep lean)
```

Tests will live under `tests/` (not yet created to preserve current 100% coverage until implementation + tests added together).

## 8. FastAPI Endpoints

All endpoints mounted under `/sim`.

| Method | Path | Purpose | Key Params |
|--------|------|---------|------------|
| POST | `/sim/generate` | Generate one or more dataset CSVs | `types` (comma list), `rows` (int, optional per type default 1000), `seed` (int optional) |
| GET | `/sim/files` | List generated files (dataset, timestamp, size) | (none) |
| GET | `/sim/download/{filename}` | Stream a specific CSV file | (filename) |
| POST | `/sim/reset` | Delete all generated files & reset cached roster | (none) |

Responses minimal JSON. Errors use FastAPI standard 4xx.

## 9. Programmatic Interface

`SharePointCSVGenerator` class:

* `__init__(root_dir: Path, seed: int | None = None)` — prepares RNG & roster.
* `generate(dataset: str, rows: int = DEFAULT_ROWS) -> Path`
* `generate_many(datasets: list[str], rows: int | dict[str,int]) -> list[Path]`
* `list_files() -> list[FileInfo]`
* `reset()` — clears directory & roster cache.

This class decouples generation from API so tests can bypass HTTP.

## 10. Determinism & Randomness Contract

Given identical `(seed, dataset, rows, interval_start, interval_end)` the output rows (including employee assignments & numeric metrics) must be byte‑identical. This allows snapshot tests for smaller row counts (e.g., 5 rows) to assert stability.

## 11. Testing Strategy (To Be Implemented Concurrently With Code)

Add tests simultaneously with code to maintain 100% coverage:

1. Roster distribution test (counts 40/40/20, stable UUIDs under fixed seed).
2. Per-dataset header test (exact header order).
3. Role constraint tests (e.g., `Dials` only uses outbound/hybrid employees).
4. Deterministic snapshot test (seeded small row count).
5. API smoke tests (POST /sim/generate then GET /sim/files & download).
6. Reset endpoint test (files removed + roster regenerated identically with same seed).

Edge cases:

* Zero rows requested (returns header-only file) — optional; default disallow `rows < 1` (return 422).
* Unknown dataset → 400.
* Duplicate generation in same minute (overwrite acceptable for now).

## 12. Performance & Complexity

All operations are in-memory row construction then single write → negligible (< ms for small sets, < few hundred ms for 1000 rows). No optimization work needed.

## 13. Implementation Phases

1. Add module skeleton + spec (this file).
2. Implement `employees.py` + tests (distribution + determinism).
3. Implement minimal generators for ACQ, Productivity, RESC, QCBS + tests.
4. Extend to Dials, IB_Calls, Campaign_Interactions + tests.
5. Add FastAPI router & integration tests.
6. Optional enhancements (row count variability, intensity param) — gated by need.

## 14. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Coverage drop on adding new code | Commit code + tests in same change set. |
| Over-expansion of feature set | Keep spec as enforcement boundary. |
| Non-deterministic UUIDs | Use uuid5 with namespace & seed‑stable input string. |
| Role leakage (wrong roles in dataset) | Dedicated role filter tests. |

## 15. Open Questions (If Needed Later)

* Should file naming add second granularity? (Currently 5‑minute rounding.)
* Do we need per-dataset distinct interval windows? (Phase 2 if required.)
* Should numeric magnitudes be parameterized? (Add optional `intensity`.)

## 16. Acceptance Criteria

* Spec file committed (this file) in `docs/design-specs/`.
* When implemented: All new modules covered 100%, lint/type/doc gates pass.
* Deterministic roster (stable IDs under same seed) with 40/40/20 distribution.
* Per-row random employee selection (uniform within eligible pool) reproducible under fixed seed.
* All dataset headers match source samples exactly.
* API endpoints operational & tested.

---
End of specification.
