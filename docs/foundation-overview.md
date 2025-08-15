# Foundation Overview (Lean Restart – Aug 2025)

This repository was intentionally reset from a verbose microservices experiment to a focused, modular monolith that ingests CSV drops, stores normalized rows in SQLite, aggregates hourly/quad-daily metrics, and emits Excel workbooks (future: email + SharePoint sync).

Retained Value From Earlier Phases:

| Area | Previous Asset | What We Kept | Why |
|------|----------------|--------------|-----|
| Config | TOML mappings | `config/settings.toml` simplified | Fast iteration |
| Testing | TDD discipline | Lean pyramid & key cases | Cost vs benefit |
| API | FastAPI patterns | Single app + health/ingest/generate | Avoid premature services |
| Docs | Lessons learned | Concise summaries (`phase2-summary.md`) | Historical context |
| Tooling | Lint/type/test | Ruff, mypy (target), pytest | Quality guardrails |

Current Core Modules (planned naming):

1. collector – discover & stage new CSV files
2. loader – parse / validate / insert rows (idempotent)
3. aggregator – hourly + quad-daily rollups
4. excel_builder – assemble workbook(s)
5. api – trigger endpoints & health
6. sharepoint (stub) – future remote sync

Minimal Workflow:

```text
raw CSVs -> collector -> staged paths -> loader -> sqlite tables -> aggregator queries -> DataFrames -> excel_builder -> reports/*.xlsx
```

Near-Term Roadmap (slice small increments):

- [ ] Loader idempotency markers (ingestion_log table)
- [ ] Basic scheduler (cron or APScheduler) for hourly run
- [ ] Email packaging (zip + summary body) stub
- [ ] SharePoint pull integration (list -> download)
- [ ] Metrics: simple run_history table
- [ ] Daily generation endpoint (/generate/daily)

Principles Going Forward:

1. One obvious way: a single process with clear internal boundaries.
2. Data first: persist raw rows early; transformations are queries.
3. Fail visibly: log + skip bad files, never silent drops.
4. Prefer deletion over abstraction when unsure.
5. Each commit should keep pipeline runnable.

See also: `testing-approach.md`, `api_overview.md`, `phase2-summary.md`.
