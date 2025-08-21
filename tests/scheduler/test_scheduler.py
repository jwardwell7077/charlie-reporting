"""
Tests for the Scheduler orchestration and integration with SharePoint/Graph API and DB service.
"""

from pathlib import Path
from typing import Any, Dict, Iterator

import pytest
from unittest.mock import MagicMock, patch

from scheduler import Scheduler, SyncJob


@pytest.fixture
def mock_sharepoint_client() -> Iterator[MagicMock]:
    """
    Fixture for a mocked SharePointClient.

    Yields:
        MagicMock: Mocked SharePointClient instance.
    """
    with patch("scheduler.SharePointClient") as MockClient:
        yield MockClient.return_value


@pytest.fixture
def mock_db_service_client() -> Iterator[MagicMock]:
    """
    Fixture for a mocked DBServiceClient.

    Yields:
        MagicMock: Mocked DBServiceClient instance.
    """
    with patch("scheduler.DBServiceClient") as MockDB:
        yield MockDB.return_value


@pytest.fixture
def scheduler_config(tmp_path: Path) -> Dict[str, Any]:
    """
    Provide a scheduler configuration dictionary.

    Args:
        tmp_path: Temporary directory path provided by pytest.

    Returns:
        dict: Scheduler configuration dictionary.
    """
    return {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": str(tmp_path / "ingest"),
        "interval_minutes": 60,
        "max_retries": 2,
        "retry_delay_seconds": 1,
    }


@pytest.fixture
def scheduler_instance(
    scheduler_config: Dict[str, Any],
    mock_sharepoint_client: MagicMock,
    mock_db_service_client: MagicMock,
) -> Scheduler:
    """
    Construct a Scheduler with mocked dependencies.

    Args:
        scheduler_config: Scheduler configuration.
        mock_sharepoint_client: Mocked SharePoint client.
        mock_db_service_client: Mocked DB service client.

    Returns:
        Scheduler: Scheduler instance.
    """
    return Scheduler(
        config=scheduler_config,
        sharepoint_client=mock_sharepoint_client,
        db_service_client=mock_db_service_client,
    )


def test_scheduler_runs_sync_job(scheduler_instance: Scheduler) -> None:
    """
    Scheduler.run_once should call SyncJob.run exactly once.

    Args:
        scheduler_instance: Scheduler instance.
    """
    scheduler = scheduler_instance
    scheduler.sync_job = MagicMock()
    scheduler.run_once()
    scheduler.sync_job.run.assert_called_once()


def test_sync_job_skips_already_ingested_files(
    mock_sharepoint_client: MagicMock,
    mock_db_service_client: MagicMock,
    scheduler_config: Dict[str, Any],
    tmp_path: Path,
) -> None:
    """
    SyncJob should skip files that the DB service reports as already ingested.

    Args:
        mock_sharepoint_client: Mocked SharePoint client.
        mock_db_service_client: Mocked DB service client.
        scheduler_config: Scheduler configuration.
        tmp_path: Temporary directory path.
    """
    mock_db_service_client.get_ingested_files.return_value = ["already.csv"]
    mock_sharepoint_client.list_files.return_value = ["already.csv", "new.csv"]

    # Simulate download path for new file
    mock_sharepoint_client.download_file.return_value = tmp_path / "ingest" / "new.csv"

    job = SyncJob(
        config=scheduler_config,
        sharepoint_client=mock_sharepoint_client,
        db_service_client=mock_db_service_client,
    )

    downloaded = job.run()

    assert "new.csv" in downloaded
    assert "already.csv" not in downloaded


def test_sync_job_handles_sharepoint_errors(
    mock_sharepoint_client: MagicMock,
    mock_db_service_client: MagicMock,
    scheduler_config: Dict[str, Any],
) -> None:
    """
    SyncJob should propagate SharePoint list errors.

    Args:
        mock_sharepoint_client: Mocked SharePoint client.
        mock_db_service_client: Mocked DB service client.
        scheduler_config: Scheduler configuration.
    """
    mock_sharepoint_client.list_files.side_effect = Exception("SharePoint error")

    job = SyncJob(
        config=scheduler_config,
        sharepoint_client=mock_sharepoint_client,
        db_service_client=mock_db_service_client,
    )

    with pytest.raises(Exception):
        job.run()


def test_sync_job_handles_db_errors(
    mock_sharepoint_client: MagicMock,
    mock_db_service_client: MagicMock,
    scheduler_config: Dict[str, Any],
) -> None:
    """
    SyncJob should propagate DB service errors.

    Args:
        mock_sharepoint_client: Mocked SharePoint client.
        mock_db_service_client: Mocked DB service client.
        scheduler_config: Scheduler configuration.
    """
    mock_db_service_client.get_ingested_files.side_effect = Exception("DB error")

    job = SyncJob(
        config=scheduler_config,
        sharepoint_client=mock_sharepoint_client,
        db_service_client=mock_db_service_client,
    )

    with pytest.raises(Exception):
        job.run()


def test_scheduler_manual_trigger(scheduler_instance: Scheduler) -> None:
    """
    Scheduler.trigger should call SyncJob.run exactly once.

    Args:
        scheduler_instance: Scheduler instance.
    """
    scheduler = scheduler_instance
    scheduler.sync_job = MagicMock()
    scheduler.trigger()
    scheduler.sync_job.run.assert_called_once()
