# Development Workflow (Lean Monolith)

Practical, lightweight flow for adding or changing functionality while keeping the pipeline always runnable.

## 1. Principles

| Principle | Why |
|-----------|-----|
| Small slices | Faster feedback & easier rollback |
| Tests guide changes | Prevents drift & accidental regressions |
| Keep surface minimal | Avoid premature abstraction |
| One obvious way | Consistent mental model |
| Fail fast, log clearly | Speeds triage |
| Delete before abstracting | Reduces dead code |
| OOP for new features | Clear seams; easier testing & extension |

## 2. Work Item Lifecycle

```text
Idea -> Ticket (issue) -> Branch -> (Update/Write Tests) -> Implement -> Local Quality Gates -> Commit(s) -> PR -> Review -> Merge -> Status Update
```

## 3. Branch Strategy

| Type | Pattern | Examples |
|------|---------|----------|
| Feature | feature/\<short-topic\> | feature/ingestion-log |
| Fix | fix/\<issue-id-or-short\> | fix/excel-empty-sheet |
| Chore | chore/\<tooling-docs\> | chore/update-ruff |
| Docs | docs/\<scope\> | docs/dev-workflow |
| Hotfix (direct to main if needed) | hotfix/\<critical-issue\> | hotfix/ingest-crash |

Keep branches < 300 lines diff when possible. Split otherwise.

## 4. Commit Conventions

Format: `<type>: <imperative present tense summary>`

Types: feat, fix, chore, docs, refactor, test, perf, build

Examples:

- feat: add ingestion_log table with hash duplicate suppression
- fix: handle empty CSV gracefully in loader

Include follow-up `Co-authored-by:` only if pairing. Avoid bundling unrelated changes.

## 5. Definition of Done (Per Change)

- Tests passing (unit + relevant integration)
- Ruff lint clean (or warnings deliberately suppressed with comment)
- Type check (mypy or Pylance) shows no new errors in touched areas
- Docs updated if: new config key, new endpoint, new operational step
- Status guidelines followed for notable changes (see `final-status-report.md`)
- Non-trivial logic added as or migrated to a focused class (constructor + small public methods)

## 6. Test-First Flow (Recommended)

1. Identify behavior delta & draft a Design Spec (see Section 6a) capturing contract.
2. Add/adjust test (fails red) encoding spec cases.
3. Implement minimal code.
4. Green tests.
5. Refactor (deduplicate / clarify names).
6. Run full quick suite.

### 6a. Design Spec (Lightweight Gate)

Create before the first failing test for any non-trivial change (new table, endpoint, scheduler, aggregation logic, cross-cutting helper).

Include 5 bullets max:

- Purpose: one-line outcome / value
- Inputs: parameters, config keys, file patterns
- Outputs: return types, db rows, side-effects (paths, table names)
- Errors: expected failure modes & handling strategy (skip, raise, log)
- Success Criteria: measurable assertions (row counts, columns, status codes)

Location options (choose one):

- New short markdown file under `docs/design-specs/<feature>.md`
- Module-level docstring in the new test file
- PR description (copy spec into repo later if durable)

Spec stays updated during Red/Green/Refactor; if behavior changes, update spec first, then tests.

See `testing-approach.md` for case ideas.

## 7. Local Quality Gates (Fast)

| Gate | Command (conceptual) | Target |
|------|----------------------|--------|
| Lint | ruff check . | 0 errors |
| Type | mypy foundation/src | No new errors |
| Unit tests | pytest -q tests/unit | <2s ideally |
| Integration | pytest -q tests/integration | Still fast (<10s) |
| Smoke API | curl /health | 200 |

Automate with a simple `make prepush` (optional future).

## 8. Adding Data Sources

Steps:

1. Add new entry in `[data_sources.sources]` in `config/settings.toml` with pattern + enabled=true.
2. Define column whitelist under `[report.columns]` if needed.
3. Add / adjust loader test for mapping & whitelist enforcement.
4. Ingest sample file into local `raw_csvs` path & run /ingest.
5. Confirm aggregator includes new source (extend query logic only if necessary).

## 9. Schema / DB Changes

- Keep SQLite migrations minimal: prefer simple `CREATE TABLE IF NOT EXISTS` append-only.
- For structural changes: create new table, backfill via script, drop old in later cleanup commit.
- Add test verifying new columns appear & ingestion_log unaffected.

## 10. Config Change Protocol

| Step | Action |
|------|--------|
| Propose | Draft change & rationale in PR description |
| Implement | Modify `config/settings.toml` (or example snippet) |
| Validate | Add test failing without new key (e.g., missing section) |
| Document | Update `foundation/README.md` + any relevant doc |

Never silently repurpose an existing key—prefer introducing new, deprecating old.

## 11. Error Handling Pattern

- Validate early (settings & file presence)
- Wrap risky I/O in narrow try/except; log with context (file, stage, reason)
- Skip corrupt file (record) rather than abort entire run unless systemic error

## 12. Logging (Planned Minimal)

Structure per line (JSON or key=value):
`ts=<iso> stage=<collector|loader|aggregator|excel|api> action=<verb> file=<name> rows=<int> ms=<duration>`

Add logging only after core path stable to avoid churn.

## 13. Performance Watchpoints

- Loader throughput (rows/sec) on larger batches
- Aggregator query time for hourly window
- Excel generation time (should stay small; watch sheet count growth)

Introduce timing decorators only if threshold > acceptable (e.g., ingest > 60s).

## 14. Introduce a New Endpoint

1. Define input/output (JSON schema) inline in test.
2. Add integration test calling endpoint.
3. Implement route in API module.
4. Update `api_overview.md`.
5. Add status report entry if user-visible.

## 15. Release / Snapshot (Optional Future)

| Step | Action |
|------|--------|
| Tag | `git tag -a v0.x.y -m "snapshot"` |
| Changelog | Summarize features & fixes since last tag |
| Verify | Run full test + quick manual /ingest + /generate/hourly |
| Publish | Push tag (internal) |

## 16. Status Reporting Tie-In

After merging meaningful increments (new source, scheduler, email stub) create a short status using template in `final-status-report.md` (guidelines) and post under project tracking (issue comment or internal note).

## 17. Handling Bugs

1. Reproduce with minimal test or sample CSV.
2. Convert reproduction into a failing test.
3. Fix; ensure no collateral behavior change unless deliberate.
4. Add root cause note (1 line) in PR description.

## 18. Deleting Legacy or Dead Code

Criteria to delete:

- Not referenced in last 30 days AND not in roadmap.
- Replaced by simpler implementation.

Process: remove code + associated doc references, confirm tests still pass.

## 19. Onboarding Checklist (New Contributor)

- Read root `README.md` & `foundation/README.md`
- Skim `testing-approach.md`, `OPERATIONS.md`
- Run tests locally
- Perform a trivial change (e.g., tweak log message) + open PR to walk full flow

## 20. Escalation / Decision Recording

If change impacts architecture or operation (scheduler strategy, data retention): add one-line decision to a PR description and, if lasting, append to `foundation-overview.md` decision/log section (future addition).

---
Lean first. If a step regularly causes friction, automate it. If a rule adds friction without protecting value, remove or simplify it.
