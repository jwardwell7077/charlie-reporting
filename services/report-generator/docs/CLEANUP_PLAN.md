# Report Generator Service Cleanup Plan

Purpose: Consolidate, modernize, and align the `report-generator` service with the emerging shared service standards (logging, config, packaging, testing, observability). This document captures the agreed cleanup goals so work can proceed incrementally without ambiguity.

## High-Level Objectives

1. Unify logging with `shared.logging` (structlog) and remove bespoke `infrastructure/logging.py` implementation.
2. Standardize naming: use `report-generator` consistently (no spaces) for service name, logs, and configuration.
3. Replace fragile custom configuration manager with shared config pattern (Pydantic Settings) or a slim wrapper; eliminate variable/typo issues.
4. Simplify entrypoint: minimal `main.py` (load config → setup logging → launch app) with no `sys.path` hacks.
5. Package service (PEP 621) similar to `database-service`; add console script entrypoint.
6. Remove / deprecate corrupted or redundant modules (phase demos, custom logging, overly large config code) with compatibility shims + warnings if needed.
7. Prune or relocate ad‑hoc demo/test scripts (`main_phase1.py`, `project_summary.py`, validation scripts) to `examples/` or docs.
8. Audit and minimize `requirements.txt`; rely on root/shared dependencies where possible.
9. Add/shore up tests: transformation → report build → excel prep; one integration-style path with mocked inputs.
10. Improve error handling: focused exception types (configuration, processing) + consistent logging of failures.
11. Observability parity: standard log fields (service, version, request_id) + stub metrics integration (align with other services).
12. Performance hygiene: lazy import heavy libs (pandas/openpyxl), respect file size & row limits.
13. Security & robustness: validate/sanitize directory paths; enforce size and count limits; tighten permissive defaults only where safe.
14. Consolidate domain model overlap (future): evaluate merging duplicate report / CSV logic with existing shared components.
15. Documentation refresh: README usage, configuration table, logging guidance, migration notes for removed modules.
16. Migration safety: Provide temporary deprecation shims for removed logging/config symbols with warnings.
17. Tooling alignment: ensure linting, type-checking, and tests integrate with top-level CI; no `sys.path` edits required.

## Current Pain Points (Snapshot)

- Custom `infrastructure/logging.py` contains numerous typos (`log_entry` vs `logentry`, variable name mismatches) and reimplements structuring logic poorly.
- Configuration manager has naming inconsistencies (`configfile`, `config_file`, `configloaded_at`, etc.) and broken env var parsing mappings.
- Entry points (`main.py`, `main_phase1.py`) contain inconsistent naming and direct `sys.path` manipulation.
- Demo / phase artifacts clutter production surface.
- No unified packaging (PEP 621 metadata missing) unlike `database-service`.
- Potentially unused scripts (`project_summary.py`, `validate_final.py`).

## Deliverables & Acceptance Criteria

| Goal | Deliverable | Acceptance Criteria |
|------|-------------|---------------------|
| Logging unification | Remove old logging module; adopt `shared.logging.setup_service_logging` | Service runs; logs show structured output with service + level; no imports of old module |
| Config modernization | New `config.py` (Pydantic Settings) | Loads from env & optional TOML; passes validation; no typos; tests cover bad input |
| Entry point cleanup | New lean `main.py` | No `sys.path` hacks; starts uvicorn (or future runner) successfully |
| Packaging | Updated `pyproject.toml` + console script | `pip install -e .` exposes `report-generator` command; imports resolve |
| Legacy removal | Demos moved / removed with changelog note | Imports of removed modules raise clear DeprecationWarning |
| Tests | New test suite | All pass under `pytest`; coverage for happy path + at least one error case |
| Docs | Updated README + this plan retained | README reflects new run + config instructions |
| Dependencies | Trimmed requirements | No unused packages flagged by import scan |

## Phased Execution Plan

Phase 1 (Infrastructure Alignment): logging, config, entrypoint, packaging.
Phase 2 (Codebase Prune & Tests): remove legacy modules, add tests, restructure demos.
Phase 3 (Observability & Hardening): metrics hooks, validation, performance & security passes.
Phase 4 (Consolidation & Docs): unify domain overlaps, finalize documentation, remove shims.

## Risk Mitigation

- Introduce deprecation shims (Phase 2) before hard removals (Phase 4).
- Keep changes incremental; run full test suite after each phase.
- Maintain backwards-compatible environment variables where practical.

## Open Questions (to resolve before Phase 1 starts)

1. Should report-generator expose a REST API immediately (FastAPI/Starlette) or remain CLI/worker until endpoints are defined? (Impacts entrypoint design.)
2. Are any external consumers importing `infrastructure.logging` or `ConfigurationManager` directly? (Determines necessity of deprecation shim.)
3. Preferred metrics backend (Prometheus style placeholders vs no-op)?

## Next Immediate Steps

1. Implement `shared.logging` adoption in `main.py`.
2. Introduce Pydantic-based settings module with minimal key set; map existing TOML/env names.
3. Add package metadata + console script.
4. Draft deprecation shim (`infrastructure/logging_legacy.py`) emitting warning.

---
Maintainer: (Add name / team)
Initial Version Date: 2025-08-14
Status: Draft (ready for Phase 1 execution)
