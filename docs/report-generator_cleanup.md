# Report Generator Cleanup & Modernization Plan

Purpose: Unify the report-generator service with shared service standards (config, logging, packaging, linting, tests) while removing brittle or duplicated code.

## High-Level Goals

1. Unify logging: Remove `src/infrastructure/logging.py` in favor of `shared.logging.setup_service_logging` (structlog) with consistent fields (`service`, `version`, `request_id`).
2. Standardize service name: Use `report-generator` (no spaces) everywhere (logs, config, docs, code) replacing variants like `report - generator`.
3. Modern configuration: Replace ad‑hoc `ConfigurationManager` (typos, inconsistent variable names) with Pydantic settings (likely extend `shared/config.py`). Support env overrides via `REPORT_GENERATOR_*` prefix.
4. Remove / rewrite corrupted code: Logging + config modules contain numerous naming errors (`logentry` vs `log_entry`, `consolehandler`, `csv_encoding` with spaces, etc.). Prefer clean reimplementation instead of incremental patching.
5. Simplify entrypoint: Refactor `src/main.py` into a minimal bootstrap (load settings → init logging → start ASGI app). Remove `sys.path` hacks. Deprecate or relocate `main_phase1.py` demo to `docs/examples/`.
6. Packaging parity: Provide proper package (e.g. `charlie_report_generator`) with console script entry point in root `pyproject.toml` (matching database-service approach) or its own `pyproject.toml` if isolation preferred.
7. Dependency hygiene: Audit `requirements.txt`; remove duplicates already declared at root; ensure only service-specific extras remain.
8. Tests & coverage: Add focused tests for CSV transformation, report assembly, and Excel export prep. Provide at least one integration test asserting end-to-end build of a sample report.
9. Observability: Introduce metrics placeholder + health endpoint (pattern from other services) and consistent structured logs.
10. Performance & memory: Lazy import heavy libs (`pandas`, `openpyxl`) inside functions; enforce file size & row limits early.
11. Robust validation: Harden path, size, and delimiter validations; clear custom exceptions (ConfigurationException, ProcessingException).
12. Security: Review CORS handling (if API) & limit wildcard usage; sanitize file paths (no directory traversal); enforce size limits.
13. Documentation: Update README with configuration table, logging usage, test commands, and deprecation notes for removed modules.
14. Compatibility shims: Temporary thin wrappers (with DeprecationWarning) if external code still imports old modules during transition.
15. Linting & style: Adopt Ruff (primary), keep Flake8 & Pylint temporarily for coverage gaps, use Pylance for type feedback.

## Phased Execution

### Phase 1 (Foundations)

- Add Ruff config & dependency (done in this commit).
- Create cleanup plan (this document).
- Standardize service name in docs & code comments.

### Phase 2 (Core Code Simplification)

- Replace logging usage in `main.py` with `shared.logging`.
- Introduce new `settings.py` (Pydantic BaseSettings) in service package.
- Mark old `infrastructure/logging.py` & `infrastructure/config.py` as deprecated (inline warning) pending removal.

### Phase 3 (Packaging + Entrypoint)

- Create package directory `services/report-generator/src/charlie_report_generator/`.
- Move business modules under the package; add `__init__.py`.
- Provide console script via root `pyproject.toml` (e.g. `report-generator=charlie_report_generator.main:run`).

### Phase 4 (Testing & Validation)

- Add unit tests for: CSV rule creation, report validation, Excel filename generation.
- Add integration test building a small multi-sheet report.

### Phase 5 (Removal & Docs)

- Remove deprecated logging/config modules once tests green & no imports remain.
- Update README + service-specific docs referencing new modules only.

### Phase 6 (Observability Enhancements)

- Add metrics abstraction (counter/timing placeholders) consistent with other services.
- Add health check & readiness endpoints (if API present) and test them.

## Success Metrics / Acceptance Criteria

| Area | Criteria |
|------|----------|
| Logging | Only `shared.logging` imported; structured output includes service + version |
| Config | Single Pydantic settings class; env overrides verified in tests |
| Packaging | Importable package; console script launches without errors |
| Tests | New tests pass; coverage for core business logic improved |
| Lint | `ruff check` passes (no unignored errors) |
| Docs | README + this plan reflect final state; legacy module removal noted |
| Cleanup | Removed or deprecated old `infrastructure/logging.py` & `config.py` |

## Ruff Adoption Notes

Initial configuration added to `pyproject.toml`. We select rule sets (E,F,I,B,UP,S,PT,RET,SIM,PL,RUF,N,C90) for broad coverage; can tighten gradually. Long line (E501) may be ignored initially if needed.

## Open Questions / Future Considerations

- Should report generation become an async service with background scheduling, or remain on-demand via API?
- Consolidate overlapping report/data models with existing services to reduce duplication.
- Introduce a shared metrics abstraction (Prometheus or OpenTelemetry) once patterns stabilize.

---
Maintainer Notes: Update this document as milestones are completed; strike through or move completed items to a CHANGELOG section if desired.
