"""Characterization tests for aggregator module."""
from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from pipeline.aggregator import fetch_hourly_productivity, build_report_frames


def _seed_productivity(db: Path, rows: list[tuple[str, str, int, float]]) -> None:
	conn = sqlite3.connect(db)
	try:
		conn.execute(
			"CREATE TABLE IF NOT EXISTS productivity (agent TEXT, date TEXT, acq INTEGER, revenue REAL)"
		)
		conn.executemany("INSERT INTO productivity VALUES (?,?,?,?)", rows)
		conn.commit()
	finally:
		conn.close()


def test_fetch_hourly_productivity_basic(tmp_path: Path) -> None:
	db = tmp_path / "test.sqlite"
	# Two hours, multiple agents
	data = [
		("a1", "2025-08-15T10:05:00", 2, 10.0),
		("a2", "2025-08-15T10:15:00", 3, 5.0),
		("a1", "2025-08-15T11:00:00", 1, 7.5),
	]
	_seed_productivity(db, data)
	df = fetch_hourly_productivity(db)
	# Expect two rows (hours) with aggregates
	assert set(df.columns) == {"hour", "total_acq", "total_revenue"}
	assert len(df) == 2
	row10 = df[df["hour"].str.startswith("2025-08-15T10")].iloc[0]
	assert int(row10["total_acq"]) == 5
	assert float(row10["total_revenue"]) == 15.0


def test_build_report_frames_structure(tmp_path: Path) -> None:
	db = tmp_path / "test.sqlite"
	_seed_productivity(db, [("a1", "2025-08-15T09:00:00", 1, 2.0)])
	frames = build_report_frames(db)
	assert "HourlySummary" in frames
	assert isinstance(frames["HourlySummary"], pd.DataFrame)
