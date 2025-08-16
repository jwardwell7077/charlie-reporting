"""Run tracking utilities for inserting and updating run_history records.

Minimal, SQLite-focused helpers. Avoids external ORM complexity.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class RunRecord:
    """Typed representation of a run_history row.

    Attributes mirror the columns of the run_history table for convenience.
    """
    id: int
    run_type: str
    started_at: str
    finished_at: str | None
    status: str
    files_found: int
    files_loaded: int
    rows_ingested: int
    failed_files: int


SCHEMA_ADDITIONS = """
CREATE TABLE IF NOT EXISTS run_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_type TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  duration_ms INTEGER,
  files_found INTEGER DEFAULT 0,
  files_loaded INTEGER DEFAULT 0,
  rows_ingested INTEGER DEFAULT 0,
  failed_files INTEGER DEFAULT 0,
  status TEXT NOT NULL,
  error TEXT
);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Create the run_history table if it does not already exist.

    Args:
        conn: Open SQLite connection.
    """
    conn.executescript(SCHEMA_ADDITIONS)


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO8601 (seconds precision)."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def start_run(conn: sqlite3.Connection, run_type: str) -> int:
    """Insert a new run_history record marked as running.

    Args:
        conn: SQLite connection.
        run_type: Logical pipeline run type (e.g. "hourly", "manual").

    Returns:
        Newly created run_history row id (always an int; SQLite guarantees lastrowid after INSERT).
    """
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO run_history (run_type, started_at, status) VALUES (?, ?, ?)",
        (run_type, _utc_now_iso(), "running"),
    )
    # Defensive runtime assertion for type narrowing (mypy): INSERT guarantees lastrowid.
    assert cur.lastrowid is not None, "SQLite cursor.lastrowid unexpectedly None after INSERT"
    return cur.lastrowid


def finish_run(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    files_found: int,
    files_loaded: int,
    rows_ingested: int,
    failed_files: int,
    status: str,
    error: str | None = None,
) -> None:
    """Finalize a run_history record with metrics and completion metadata.

    Args:
        conn: SQLite connection.
        run_id: Identifier returned from `start_run`.
        files_found: Count of discovered files.
        files_loaded: Number of files successfully loaded.
        rows_ingested: Total rows ingested across files.
        failed_files: Number of files that failed processing.
        status: Final run status (e.g. "success", "error").
        error: Optional error message captured for failed runs.
    """
    cur = conn.cursor()
    cur.execute("SELECT started_at FROM run_history WHERE id=?", (run_id,))
    row = cur.fetchone()
    duration_ms = None
    if row:
        try:
            started = datetime.fromisoformat(row[0])
            duration_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)
        except Exception:
            duration_ms = None
    cur.execute(
        """
        UPDATE run_history
        SET finished_at=?,
            duration_ms=?,
            files_found=?,
            files_loaded=?,
            rows_ingested=?,
            failed_files=?,
            status=?,
            error=?
        WHERE id=?
        """,
        (
            _utc_now_iso(),
            duration_ms,
            files_found,
            files_loaded,
            rows_ingested,
            failed_files,
            status,
            error,
            run_id,
        ),
    )
