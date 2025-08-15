# Testing Approach (Lean Foundation)

Focus: confidence in a single ingestion → SQLite → aggregation → Excel pipeline without microservice overhead.

Principles:

1. Fast feedback – majority of tests exercise pure functions / small units.
2. Deterministic data – tiny inline CSV fixtures (StringIO) where possible.
3. Clear boundaries – one integration test per stage boundary (collector→loader, loader→aggregator, aggregator→excel, API end-to-end).
4. Minimal mocks – real in-memory SQLite; stub only external SharePoint/email.
5. Contract focus – assert observable outputs (DataFrame columns, sheet names, HTTP status) not internals.

Test pyramid (target proportions):

- 70% unit
- 25% integration
- 5% smoke

Key cases:

- Settings: missing sections, disabled source filtered.
- Collector: pattern match, duplicate skip, archive move idempotent.
- Loader: column whitelist enforcement, duplicate ingestion, corrupt CSV skip.
- Aggregator: empty DB, hour boundary grouping, multiple sources.
- Excel: sheet ordering, column subset, empty data safe.
- API: /health 200, /ingest triggers count >0 when files exist, /generate/hourly returns workbook path.

Error strategy:

- Fail fast on malformed settings.
- Log & skip corrupt CSV (record file + reason).
- 500 only for unexpected exceptions (reduce over time).

Coverage goals:

- Core pipeline modules ≥ 90%.
- Overall ≥ 80%.

Future enhancements:

- Property-based tests for loader mapping.
- Performance micro-benchmark.
- Snapshot sheet headers.
