"""Collector module
Scans configured input_root for matching source patterns, moves new files to staging.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from config.settings import DataSource, Settings, load_settings


def discover_source_files(root: Path, source: DataSource) -> list[Path]:
    """Return matching files for a single data source.

    Skips disabled sources and silently returns an empty list if the root does not exist.

    Args:
        root: Directory containing incoming files.
        source: Data source configuration.

    Returns:
        Sorted list of matching file paths.
    """
    if not source.enabled:
        return []
    if not root.exists():
        return []
    return sorted(root.glob(source.pattern))


def stage_file(file_path: Path, staging_dir: Path) -> Path:
    """Copy a file into the staging directory (idempotent by filename).

    Args:
        file_path: Source file path.
        staging_dir: Directory to copy into (created if absent).

    Returns:
        Path to staged file.
    """
    staging_dir.mkdir(parents=True, exist_ok=True)
    target = staging_dir / file_path.name
    shutil.copy2(file_path, target)
    return target


def collect(settings: Settings | None = None) -> list[Path]:
    """Discover and stage files for all configured data sources.

    Args:
        settings: Optional pre-loaded settings. If omitted they are loaded from disk.

    Returns:
        List of staged file paths in processing order.
    """
    settings = settings or load_settings()
    staged: list[Path] = []
    for source in settings.data_sources:
        files = discover_source_files(settings.collector.input_root, source)
        for f in files:
            staged.append(stage_file(f, settings.collector.staging_dir))
    return staged
