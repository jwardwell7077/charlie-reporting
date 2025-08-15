"""Collector module
Scans configured input_root for matching source patterns, moves new files to staging.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from config.settings import DataSource, Settings, load_settings


def discover_source_files(root: Path, source: DataSource) -> list[Path]:
    if not source.enabled:
        return []
    if not root.exists():
        return []
    return sorted(root.glob(source.pattern))


def stage_file(file_path: Path, staging_dir: Path) -> Path:
    staging_dir.mkdir(parents=True, exist_ok=True)
    target = staging_dir / file_path.name
    shutil.copy2(file_path, target)
    return target


def collect(settings: Settings | None = None) -> list[Path]:
    settings = settings or load_settings()
    staged: list[Path] = []
    for source in settings.data_sources:
        files = discover_source_files(settings.collector.input_root, source)
        for f in files:
            staged.append(stage_file(f, settings.collector.staging_dir))
    return staged
