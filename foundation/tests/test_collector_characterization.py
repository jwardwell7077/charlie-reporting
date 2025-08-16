"""Characterization tests for collector (file discovery & staging)."""
from __future__ import annotations

from pathlib import Path

from config.settings import DataSource, CollectorConfig, Settings, SchedulesConfig, ReportConfig, EmailConfig
from pipeline.collector import discover_source_files, stage_file, collect


def _settings_for(root: Path) -> Settings:
	return Settings(
		schedules=SchedulesConfig(),
		data_sources=[DataSource(name="prod", pattern="Productivity_*.csv")],
		collector=CollectorConfig(
			input_root=root / "incoming", staging_dir=root / "staging", archive_dir=root / "archive"
		),
		report=ReportConfig(output_dir=root / "reports", workbook_name="r.xlsx", columns={"productivity": []}),
		email=EmailConfig(from_addr="x@y", recipients=[], subject_template="s", include_sheets=[]),
	)


def test_discover_source_files_filters_disabled(tmp_path: Path) -> None:
	ds = DataSource(name="x", pattern="*.csv", enabled=False)
	files = discover_source_files(tmp_path, ds)
	assert files == []


def test_collect_stages_matching_files(tmp_path: Path) -> None:
	s = _settings_for(tmp_path)
	s.collector.input_root.mkdir(parents=True)
	# Matching and non-matching
	(s.collector.input_root / "Productivity_2025.csv").write_text("agent,date,acq,revenue\na,2025,1,2\n")
	(s.collector.input_root / "Ignore_2025.csv").write_text("x")
	staged = collect(s)
	assert len(staged) == 1
	assert staged[0].parent == s.collector.staging_dir
	assert staged[0].name.startswith("Productivity_")


def test_stage_file_idempotent_filename(tmp_path: Path) -> None:
	src_root = tmp_path / "in"
	src_root.mkdir()
	f = src_root / "Productivity_X.csv"
	f.write_text("agent,date,acq,revenue\na,2025,1,2\n")
	staging = tmp_path / "stage"
	first = stage_file(f, staging)
	second = stage_file(f, staging)
	assert first == second
	assert second.read_text() == f.read_text()
