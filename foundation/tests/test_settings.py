from pathlib import Path
from config.settings import Settings


def test_settings_load_example(tmp_path: Path):
    cfg = tmp_path / "settings.toml"
    cfg.write_text("""
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
    )
    settings = Settings.load(cfg)
    assert settings.schedules.hourly_interval_minutes == 30
    assert settings.data_sources[0].name == "productivity"
