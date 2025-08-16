"""Characterization tests for CSV loader -> SQLite ingestion."""
from __future__ import annotations

from pathlib import Path
import sqlite3

from config.settings import Settings, SchedulesConfig, CollectorConfig, ReportConfig, EmailConfig, DataSource
from pipeline.loader import init_db, load_csv_into_table, load_staged


def _settings(tmp: Path) -> Settings:
	return Settings(
		schedules=SchedulesConfig(),
		data_sources=[DataSource(name="prod", pattern="Productivity_*.csv")],
		collector=CollectorConfig(
			input_root=tmp / "incoming", staging_dir=tmp / "staging", archive_dir=tmp / "archive"
		),
		report=ReportConfig(
			output_dir=tmp / "reports", workbook_name="r.xlsx", columns={"productivity": ["agent", "date", "acq", "revenue"]}
		),
		email=EmailConfig(from_addr="z@y", recipients=[], subject_template="s", include_sheets=[]),
	)


def test_init_db_idempotent(tmp_path: Path) -> None:
	db = tmp_path / "db.sqlite"
	init_db(db)
	size1 = db.stat().st_size
	init_db(db)
	assert db.stat().st_size == size1


def test_load_csv_into_table_roundtrip(tmp_path: Path) -> None:
	db = tmp_path / "db.sqlite"
	init_db(db)
	csv_path = tmp_path / "p.csv"
	csv_path.write_text("agent,date,acq,revenue\na,2025-01-01T00:00:00,1,2.5\n")
	rows = load_csv_into_table(db, csv_path, "productivity", ["agent", "date", "acq", "revenue"])
	assert rows == 1
	conn = sqlite3.connect(db)
	try:
		cur = conn.execute("SELECT count(*) FROM productivity")
		assert cur.fetchone()[0] == 1
	finally:
		conn.close()


def test_load_staged_ingests_all(tmp_path: Path) -> None:
	s = _settings(tmp_path)
	s.collector.staging_dir.mkdir(parents=True)
	(s.collector.staging_dir / "Productivity_a.csv").write_text(
		"agent,date,acq,revenue\na,2025-01-01T00:00:00,1,2\n"
	)
	(s.collector.staging_dir / "Productivity_b.csv").write_text(
		"agent,date,acq,revenue\nb,2025-01-01T01:00:00,2,3\n"
	)
	result = load_staged(s, db_path=tmp_path / "db.sqlite")
	assert set(result.keys()) == {"Productivity_a.csv", "Productivity_b.csv"}
