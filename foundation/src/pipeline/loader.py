"""Loader: load staged CSV files into SQLite (idempotent)."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Sequence

from config.settings import Settings, load_settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ingested_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_name TEXT NOT NULL,
  loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS productivity (
  agent TEXT,
  date TEXT,
  acq INTEGER,
  revenue REAL
);
"""


def init_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def load_csv_into_table(db_path: Path, csv_path: Path, table: str, columns: Sequence[str]) -> int:
    conn = sqlite3.connect(db_path)
    try:
        rows = 0
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            col_subset = [c for c in columns if c in reader.fieldnames or True]
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
