"""Clean, minimal shared test fixtures (rebuilt)."""

from __future__ import annotations

import random
import shutil
import sys
import tempfile
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

import pytest

try:  # Optional
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

REPO_ROOT = Path(__file__).parent.parent
for p in (REPO_ROOT / "services", REPO_ROOT / "shared", REPO_ROOT / "src"):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

TEST_AGENTS = [
    "Alice Johnson", "Bob Smith", "Charlie Davis", "Diana Wilson",
    "Edward Brown", "Fiona Taylor", "George Miller", "Hannah Davis",
]
TEST_CAMPAIGNS = [
    "Q1_2024_Acquisition", "Spring_Outreach", "Summer_Campaign",
    "Fall_Revival", "Year_End_Push",
]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def temp_test_dir() -> Iterator[Path]:
    d = Path(tempfile.mkdtemp(prefix="charlie_reporting_test_"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    d = Path(tempfile.mkdtemp(prefix="charlie_reporting_case_"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def csv_test_files(temp_test_dir: Path) -> dict[str, dict]:
    rng = random.Random(42)
    def dt(back: int) -> str:
        return (datetime.now() - timedelta(days=back)).strftime("%Y-%m-%d")

    rows = [
        {
            "Agent": rng.choice(TEST_AGENTS),
            "Date": dt(rng.randint(0, 30)),
            "Campaign": rng.choice(TEST_CAMPAIGNS),
            "Acquisitions": rng.randint(0, 10),
            "Revenue": round(rng.uniform(1000, 50000), 2),
        }
        for _ in range(15)
    ]
    path = temp_test_dir / "ACQ.csv"
    if pd:
        import pandas as _pd  # local alias
        _pd.DataFrame(rows).to_csv(path, index=False)  # type: ignore[arg-type]
    else:
        with path.open("w", encoding="utf-8") as f:
            f.write("Agent,Date,Campaign,Acquisitions,Revenue\n")
            for r in rows:
                f.write(f"{r['Agent']},{r['Date']},{r['Campaign']},{r['Acquisitions']},{r['Revenue']}\n")
    return {"ACQ.csv": {"path": path, "data": rows}}


@pytest.fixture
def performance_test_data() -> list[dict[str, object]]:
    rng = random.Random(7)
    return [
        {
            "Agent": rng.choice(TEST_AGENTS),
            "Date": (datetime.now() - timedelta(days=rng.randint(0, 45))).strftime("%Y-%m-%d"),
            "Acquisitions": rng.randint(0, 10),
            "Revenue": round(rng.uniform(500, 40000), 2),
        }
        for _ in range(60)
    ]


@pytest.fixture
def malformed_csv_data(temp_test_dir: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    p1 = temp_test_dir / "no_headers.csv"
    p1.write_text("Alice,100,2025-01-01\nBob,200,2025-01-02\n")
    p2 = temp_test_dir / "inconsistent.csv"
    p2.write_text("Agent,Revenue,Date\nAlice,100\nBob,200,2025-01-02,Extra\n")
    p3 = temp_test_dir / "empty.csv"
    p3.write_text("")
    files.update({"no_headers": p1, "inconsistent": p2, "empty": p3})
    return files


@pytest.fixture
def mock_email_data() -> dict[str, object]:
    return {
        "sender": "test@example.com",
        "recipients": ["recipient1@example.com", "recipient2@example.com"],
        "subject": f"Test Report - {datetime.now():%Y-%m-%d}",
        "body": "Automated test email.",
        "attachments": [],
    }


@pytest.fixture
def mock_logger():
    class Logger:
        def __init__(self) -> None:
            self.events: list[tuple[str, str]] = []
        def info(self, m: str, **_): self.events.append(("INFO", m))
        def warning(self, m: str, **_): self.events.append(("WARNING", m))
        def error(self, m: str, **_): self.events.append(("ERROR", m))
        def debug(self, m: str, **_): self.events.append(("DEBUG", m))
    return Logger()


@pytest.fixture
def performance_thresholds() -> dict[str, int | float]:
    return {"csv_processing_seconds": 30, "memory_usage_mb": 150}


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "performance: performance tests")
    config.addinivalue_line("markers", "slow: slow tests")