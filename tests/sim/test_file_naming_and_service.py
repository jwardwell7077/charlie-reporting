"""Service + filename integration tests.

Covers:
- Filename formatting (prefix, extension, timestamp components)
- Deterministic output across instances with same seed
- Thread-safety (lock) under concurrent generation
"""
from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path

from sharepoint_sim.service import SharePointCSVGenerator  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATASET = "ACQ"
SEED_FILENAME = 123
SEED_DETERMINISTIC = 999
SEED_CONCURRENT = 42
ROWS_FILENAME = 12
ROWS_DETERMINISTIC = 10
ROWS_CONCURRENT = 11
THREAD_COUNT = 5
TIME_LEN = 4

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_filename_rounding_and_generation(tmp_path: Path) -> None:
    """Filename has expected shape and 5-minute truncated timestamp.

    Asserts:
    - File exists with correct prefix & suffix
    - Timestamp portion splits into date + time
    - Date parses as ISO YYYY-MM-DD
    - Time is HHMM (digits) and minute divisible by 5
    """
    svc = SharePointCSVGenerator(root_dir=tmp_path, seed=SEED_FILENAME)
    out = svc.generate(DATASET, rows=ROWS_FILENAME)
    assert out.exists()
    assert out.name.startswith(f"{DATASET}__")
    assert out.name.endswith(".csv")
    parts = out.name.split("__", 1)[1].removesuffix(".csv")
    date_part, time_part = parts.split("_", 1)
    # Validate date format
    datetime.strptime(date_part, "%Y-%m-%d")  # ensures valid date format
    assert len(time_part) == TIME_LEN
    assert time_part.isdigit()
    minute = int(time_part[2:])
    assert minute % 5 == 0


def test_deterministic_across_instances(tmp_path: Path) -> None:
    """Same seed + dataset + row count -> identical CSV content across directories."""
    svc1 = SharePointCSVGenerator(root_dir=tmp_path / "a", seed=SEED_DETERMINISTIC)
    p1 = svc1.generate(DATASET, rows=ROWS_DETERMINISTIC)
    text1 = p1.read_text()
    svc2 = SharePointCSVGenerator(root_dir=tmp_path / "b", seed=SEED_DETERMINISTIC)
    p2 = svc2.generate(DATASET, rows=ROWS_DETERMINISTIC)
    text2 = p2.read_text()
    assert text1 == text2


def test_concurrent_generation_locking(tmp_path: Path) -> None:
    """Multiple threads can generate without race-corrupting files (size > 0)."""
    svc = SharePointCSVGenerator(root_dir=tmp_path, seed=SEED_CONCURRENT)
    paths: list[Path] = []

    def worker() -> None:
        paths.append(svc.generate(DATASET, rows=ROWS_CONCURRENT))

    threads = [threading.Thread(target=worker) for _ in range(THREAD_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(paths) == THREAD_COUNT
    existing = [p for p in set(paths) if p.exists()]
    assert existing
    assert existing[0].stat().st_size > 0
