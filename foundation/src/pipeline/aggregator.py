"""Aggregator: produce DataFrames for report sheets."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def fetch_hourly_productivity(db_path: Path) -> pd.DataFrame:
    """Return per-hour productivity aggregates for the last 24 hours.

    Args:
        db_path: Path to the SQLite database file containing a `productivity` table.

    Returns:
        DataFrame with columns: hour (YYYY-MM-DDTHH), total_acq, total_revenue (one row per hour).
    """
    conn = sqlite3.connect(db_path)
    try:
        sql = (
            """
            SELECT substr(date,1,13) as hour, sum(acq) as total_acq, sum(revenue) as total_revenue
            FROM productivity
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 24
            """
        )
        df: pd.DataFrame = pd.read_sql_query(sql, conn)  # pyright: ignore[reportUnknownMemberType]
        return df
    finally:
        conn.close()


def build_report_frames(db_path: Path) -> dict[str, pd.DataFrame]:
    """Build all DataFrames required for the reporting workbook.

    Args:
        db_path: SQLite database path.

    Returns:
        Mapping of sheet name to populated DataFrame.
    """
    return {"HourlySummary": fetch_hourly_productivity(db_path)}
