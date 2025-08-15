"""Settings loader (TOML-based) for foundation platform."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib


@dataclass(slots=True)
class DataSource:
    name: str
    pattern: str
    enabled: bool = True


@dataclass(slots=True)
class SchedulesConfig:
    hourly_interval_minutes: int = 60
    quad_daily_times: list[str] | None = None  # e.g. ["08:00","12:00","16:00","19:00"]


@dataclass(slots=True)
class CollectorConfig:
    input_root: Path
    staging_dir: Path
    archive_dir: Path


@dataclass(slots=True)
class ReportConfig:
    output_dir: Path
    workbook_name: str
    columns: dict[str, list[str]]


@dataclass(slots=True)
class EmailConfig:
    from_addr: str
    recipients: list[str]
    subject_template: str
    include_sheets: list[str]


@dataclass(slots=True)
class Settings:
    schedules: SchedulesConfig
    data_sources: list[DataSource]
    collector: CollectorConfig
    report: ReportConfig
    email: EmailConfig

    @classmethod
    def load(cls, path: Path) -> "Settings":
        raw = tomllib.loads(path.read_text())

        schedules = SchedulesConfig(
            hourly_interval_minutes=raw.get("schedules", {}).get("hourly_interval_minutes", 60),
            quad_daily_times=raw.get("schedules", {}).get("quad_daily_times"),
        )
        sources = [
            DataSource(name=s["name"], pattern=s["pattern"], enabled=s.get("enabled", True))
            for s in raw.get("data_sources", {}).get("sources", [])
        ]
        collector = CollectorConfig(
            input_root=Path(raw.get("collector", {}).get("input_root", "./_sharepoint_drop")),
            staging_dir=Path(raw.get("collector", {}).get("staging_dir", "./_staging")),
            archive_dir=Path(raw.get("collector", {}).get("archive_dir", "./_archive")),
        )
        report = ReportConfig(
            output_dir=Path(raw.get("report", {}).get("output_dir", "./_reports")),
            workbook_name=raw.get("report", {}).get("workbook_name", "hourly_report.xlsx"),
            columns=raw.get("report", {}).get("columns", {}),
        )
        email = EmailConfig(
            from_addr=raw.get("email", {}).get("from", "reports@example.com"),
            recipients=raw.get("email", {}).get("recipients", []),
            subject_template=raw.get("email", {}).get("subject_template", "Daily Report {date}"),
            include_sheets=raw.get("email", {}).get("include_sheets", []),
        )
        return cls(
            schedules=schedules,
            data_sources=sources,
            collector=collector,
            report=report,
            email=email,
        )


def load_settings(settings_path: str | Path = "config/settings.toml") -> Settings:
    path = Path(settings_path)
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    return Settings.load(path)
