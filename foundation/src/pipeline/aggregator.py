"""Aggregator: produce DataFrames for report sheets."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


def fetch_hourly_productivity(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql_query(
            """
            SELECT substr(date,1,13) as hour, sum(acq) as total_acq, sum(revenue) as total_revenue
            FROM productivity
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 24
            """,
            conn,
        )
    finally:
        conn.close()


def build_report_frames(db_path: Path) -> dict[str, pd.DataFrame]:
    return {
        "HourlySummary": fetch_hourly_productivity(db_path),
    }
