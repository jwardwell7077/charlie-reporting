"""Tests for `Settings` loading from TOML configuration."""

from pathlib import Path
from textwrap import dedent

from config.settings import Settings, load_settings


def test_settings_load_example(tmp_path: Path) -> None:
    """End‑to‑end parse of a representative TOML file populates all sections."""
    cfg = tmp_path / "settings.toml"
    cfg.write_text(
        dedent(
            """
            [schedules]
            hourly_interval_minutes = 30
            quad_daily_times = ["08:00", "12:00", "16:00", "19:00"]

            [data_sources]
            [[data_sources.sources]]
            name = "productivity"
            pattern = "Productivity_*.csv"

            [collector]
            input_root = "./input"
            staging_dir = "./staging"
            archive_dir = "./archive"

            [report]
            output_dir = "./reports"
            workbook_name = "hr.xlsx"

            [report.columns]
            productivity = ["agent", "date", "acq", "revenue"]

            [email]
            from = "reports@example.com"
            recipients = ["team@example.com"]
            subject_template = "Daily Performance Report {date}"
            include_sheets = ["HourlySummary"]
            """
        ).strip()
    )

    settings = Settings.load(cfg)

    # Schedules
    assert settings.schedules.hourly_interval_minutes == 30
    assert settings.schedules.quad_daily_times == ["08:00", "12:00", "16:00", "19:00"]

    # Data sources
    assert len(settings.data_sources) == 1
    ds = settings.data_sources[0]
    assert ds.name == "productivity"
    assert ds.pattern.startswith("Productivity_")
    assert ds.enabled is True

    # Collector paths (just validate tail components to avoid absolute path differences)
    assert settings.collector.input_root.name == "input"
    assert settings.collector.staging_dir.name == "staging"
    assert settings.collector.archive_dir.name == "archive"

    # Report configuration
    assert settings.report.workbook_name == "hr.xlsx"
    assert settings.report.output_dir.name == "reports"
    assert settings.report.columns["productivity"] == ["agent", "date", "acq", "revenue"]

    # Email configuration
    assert settings.email.from_addr == "reports@example.com"
    assert settings.email.recipients == ["team@example.com"]
    assert settings.email.include_sheets == ["HourlySummary"]


def test_settings_defaults_when_missing(tmp_path: Path) -> None:
    """Missing optional keys fall back to documented defaults."""
    cfg = tmp_path / "settings.toml"
    # Provide only minimal sections; omit report/email/data sources for defaults.
    cfg.write_text(
        dedent(
            """
            [schedules]
            hourly_interval_minutes = 15
            """
        ).strip()
    )
    settings = Settings.load(cfg)
    # Provided value respected
    assert settings.schedules.hourly_interval_minutes == 15
    # Defaults applied
    assert settings.schedules.quad_daily_times is None
    assert settings.data_sources == []
    assert settings.report.workbook_name.endswith("hourly_report.xlsx")
    assert settings.email.from_addr == "reports@example.com"


def test_load_settings_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.toml"
    try:
        load_settings(missing)
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        assert str(missing) in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected FileNotFoundError")
