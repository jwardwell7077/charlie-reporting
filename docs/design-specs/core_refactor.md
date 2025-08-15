# Design Spec: Core Service OOP Refactor

Date: 2025-08-15

Status: Draft (characterization phase)

Owner: JW

## 1. Purpose

Refactor existing procedural pipeline modules (collector, loader, aggregator, excel) into cohesive, testable classes without changing observable behavior, establishing a foundation for upcoming ingestion_log & run_history integration.

## 2. Current vs Target

| Concern | Current (Procedural) | Target (OOP) |
|---------|----------------------|--------------|
| File discovery | free functions in collector.py | CollectorService.collect() |
| Loading CSV -> DB | free functions in loader.py | LoaderService.ingest_staged() (later: IngestionLog integration) |
| Aggregation | free function build_report_frames() | Aggregator.build_frames() |
| Excel writing | build_workbook() free function | WorkbookBuilder.build() |

## 3. Class Sketch

```text
CollectorService
  +collect(settings: Settings) -> list[Path]

LoaderService
  +ingest_staged(settings: Settings, db_path: Path) -> dict[str,int]
  (later: +ingest_with_log())

Aggregator
  +hourly_productivity(db_path: Path) -> DataFrame
  +build_frames(db_path: Path) -> dict[str,DataFrame]

WorkbookBuilder
  +build(frames: Mapping[str,DataFrame], output_path: Path) -> Path
  +sheet_html(frame: DataFrame, max_rows:int=50) -> str
```

## 4. Non-Goals (This Refactor)

- Adding ingestion_log logic (separate spec covers it)
- Changing data shapes / column names
- Performance optimizations

## 5. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Silent behavior change | Characterization tests before refactor |
| Over-abstraction | Keep classes thin wrappers around existing logic initially |
| Harder future rename | Centralize class names now, keep public methods stable |

## 6. Success Criteria

1. All characterization tests (collector, loader, aggregator, excel) pass pre and post refactor.
2. Public method contracts documented (docstrings + type hints) and mypy clean.
3. No increase in lines-of-code > 20% (guard against bloat) for these modules.
4. Ruff/mypy produce no new warnings/errors.

## 7. Test Plan (Characterization)

| ID | Area | Behavior Captured |
|----|------|-------------------|
| C1 | Collector | Copies matching files to staging, preserves filename |
| C2 | Loader | Inserts correct row count into productivity table |
| C3 | Aggregator | Returns DataFrame with columns hour,total_acq,total_revenue |
| C4 | Excel | Writes workbook with expected sheet name |

## 8. Implementation Steps

1. Add characterization tests (fail if assumptions drift).
2. Introduce classes in new module(s) `core/services.py` OR in existing modules first.
3. Classes delegate to existing functions; tests updated to use classes.
4. Inline/refactor logic into class methods; remove old free functions when unused.
5. Update docs/context if public API (import paths) changes.

## 9. Deliverables Checklist

- [ ] Spec merged
- [ ] Tests C1–C4 added & green on current procedural code
- [ ] Classes added & tests updated to use them
- [ ] Old functions removed / deprecated comments
- [ ] Type hints + docstrings present

## 10. Acceptance

Refactor accepted when criteria met and no functional regressions observed.

---
(End of spec)
