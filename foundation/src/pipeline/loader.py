"""Loader: load staged CSV files into SQLite (idempotent).

Enhancements planned/partially implemented:
- ingestion_log table for file-level idempotency & status tracking
- hashing helper (sha256) to detect changed content
- run_history integration via core.run_tracking
"""
from __future__ import annotations

import csv
import sqlite3
from collections.abc import Sequence
from pathlib import Path

from config.settings import Settings, load_settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ingestion_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    loaded_at TEXT,
    rows_ingested INTEGER DEFAULT 0,
    status TEXT NOT NULL,          -- running|success|error|skipped
    error TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_ingestion_log_hash ON ingestion_log(file_hash);

CREATE TABLE IF NOT EXISTS productivity (
    agent TEXT,
    date TEXT,
    acq INTEGER,
    revenue REAL
);
"""


def init_db(db_path: Path) -> None:
    """Initialize ingestion and productivity tables if absent.

    Args:
        db_path: SQLite database file path.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def load_csv_into_table(db_path: Path, csv_path: Path, table: str, columns: Sequence[str]) -> int:
    """Load a CSV file into a target table.

    Performs a best-effort column subset: only columns present in the CSV header are inserted.

    Args:
        db_path: SQLite database path.
        csv_path: Path to CSV file.
        table: Destination table name.
        columns: Desired column ordering subset.

    Returns:
        Number of ingested rows.
    """
    conn = sqlite3.connect(db_path)
    try:
        rows = 0
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            col_subset = list(columns)
            placeholders = ",".join(["?"] * len(col_subset))
            insert_sql = f"INSERT INTO {table} ({','.join(col_subset)}) VALUES ({placeholders})"
            for row in reader:
                values = [row.get(c) for c in col_subset]
                conn.execute(insert_sql, values)
                rows += 1
        conn.commit()
        return rows
    finally:
        conn.close()


def load_staged(settings: Settings | None = None, db_path: Path | None = None) -> dict[str, int]:
    """Load all staged productivity CSV files into the database.

    Args:
        settings: Optional settings object (loaded if missing).
        db_path: Optional override for database file (defaults foundation.sqlite).

    Returns:
        Mapping of filename to number of rows ingested.
    """
    settings = settings or load_settings()
    db = db_path or Path("foundation.sqlite")
    init_db(db)
    results: dict[str, int] = {}
    # For MVP assume only productivity mapping
    prod_cols = settings.report.columns.get("productivity", [])
    for csv_file in settings.collector.staging_dir.glob("Productivity_*.csv"):
        loaded = load_csv_into_table(db, csv_file, "productivity", prod_cols)
        results[csv_file.name] = loaded
    return results
