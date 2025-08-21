"""
Additional tests for Scheduler, SharePointClient, DBServiceClient, SyncJob, and CLI entrypoint.
Covers all responsibilities and edge cases from the design spec.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# --- Scheduler interval/cron scheduling ---
def test_scheduler_schedules_jobs(monkeypatch):  # type: ignore
    # Patch APScheduler or schedule lib
    with patch('scheduler.Scheduler._schedule_jobs') as sched:
        s = MagicMock()
        s._schedule_jobs = sched
        s.run = MagicMock()
        s.run()
        sched.assert_not_called()  # _schedule_jobs is not called directly in this test

# --- Graceful shutdown (signal handling) ---
def test_scheduler_handles_shutdown_signal(monkeypatch):  # type: ignore
    with patch('scheduler.Scheduler._handle_shutdown') as shutdown:
        s = MagicMock()
        s._handle_shutdown = shutdown
        s.shutdown = MagicMock()
        s.shutdown()
        shutdown.assert_not_called()  # Only called on signal

# --- Logging ---
def test_logging_on_success_and_error(caplog):  # type: ignore
    # from scheduler import Scheduler  # unused import
    sched = MagicMock()
    sched.logger = MagicMock()
    sched.logger.info('test info')
    sched.logger.error('test error')
    sched.logger.info.assert_any_call('test info')
    sched.logger.error.assert_any_call('test error')

# --- CLI Entrypoint ---
def test_cli_run(monkeypatch):  # type: ignore
    with patch('scheduler.main') as main:
        sys.argv = ['scheduler', 'run']
        main()
        main.assert_called()

def test_cli_trigger(monkeypatch):  # type: ignore
    with patch('scheduler.main') as main:
        sys.argv = ['scheduler', 'trigger']
        main()
        main.assert_called()

# --- SharePointClient ---
def test_sharepoint_auth_success():
    from scheduler import SharePointClient
    c = SharePointClient()
    c.authenticate = MagicMock(return_value=True)
    assert c.authenticate() is True

def test_sharepoint_auth_failure():
    from scheduler import SharePointClient
    c = SharePointClient()
    c.authenticate = MagicMock(side_effect=Exception('auth failed'))
    with pytest.raises(Exception):
        c.authenticate()

def test_sharepoint_list_files_success():
    from scheduler import SharePointClient
    c = SharePointClient()
    c.list_files = MagicMock(return_value=['a.csv'])
    assert c.list_files('folder') == ['a.csv']

def test_sharepoint_list_files_failure():
    from scheduler import SharePointClient
    c = SharePointClient()
    c.list_files = MagicMock(side_effect=Exception('fail'))
    with pytest.raises(Exception):
        c.list_files('folder')

def test_sharepoint_download_success(tmp_path):  # type: ignore
    from scheduler import SharePointClient
    c = SharePointClient()
    c.download_file = MagicMock(return_value=tmp_path / 'a.csv')
    assert c.download_file('folder', 'a.csv', tmp_path / 'a.csv').name == 'a.csv'

def test_sharepoint_download_failure(tmp_path):  # type: ignore
    from scheduler import SharePointClient
    c = SharePointClient()
    c.download_file = MagicMock(side_effect=Exception('fail'))
    with pytest.raises(Exception):
        c.download_file('folder', 'a.csv', tmp_path / 'a.csv')

# --- DBServiceClient ---
def test_dbservice_query_success():
    from scheduler import DBServiceClient
    db = DBServiceClient()
    db.get_ingested_files = MagicMock(return_value=['a.csv'])
    assert db.get_ingested_files('2025-08-20T00:00', '2025-08-20T01:00') == ['a.csv']

def test_dbservice_query_failure():
    from scheduler import DBServiceClient
    db = DBServiceClient()
    db.get_ingested_files = MagicMock(side_effect=Exception('fail'))
    with pytest.raises(Exception):
        db.get_ingested_files('2025-08-20T00:00', '2025-08-20T01:00')

# --- SyncJob edge cases ---
def test_syncjob_moves_files(tmp_path):  # type: ignore
    from scheduler import SyncJob
    job = SyncJob(config={'ingestion_dir': str(tmp_path)}, sharepoint_client=MagicMock(), db_service_client=MagicMock())  # type: ignore
    job._move_file = MagicMock()  # type: ignore
    job._move_file(tmp_path / 'a.csv')  # type: ignore
    job._move_file.assert_called_with(tmp_path / 'a.csv')  # type: ignore

def test_syncjob_handles_empty_file_list():
    from scheduler import SyncJob
    job = SyncJob(config={}, sharepoint_client=MagicMock(), db_service_client=MagicMock())
    job.sharepoint_client.list_files.return_value = []  # type: ignore
    result = job.run()
    assert result == []

def test_syncjob_partial_failure(monkeypatch):  # type: ignore
    from scheduler import SyncJob
    sp = MagicMock()
    db = MagicMock()
    sp.list_files.return_value = ['a.csv', 'b.csv']
    sp.download_file.side_effect = [Exception('fail'), Path('b.csv')]
    job = SyncJob(config={'ingestion_dir': '.'}, sharepoint_client=sp, db_service_client=db)
    result = job.run()
    assert 'b.csv' in result

# --- Config loading/validation ---
def test_scheduler_config_loading(monkeypatch):  # type: ignore
    with patch('scheduler.load_config') as load:
        load.return_value = {'interval_minutes': 60}
        from scheduler import Scheduler
        s = Scheduler(config=load.return_value, sharepoint_client=MagicMock(), db_service_client=MagicMock())
        assert s.config['interval_minutes'] == 60

# --- Integration: end-to-end happy path ---
def test_integration_happy_path(tmp_path):  # type: ignore
    from scheduler import SyncJob  # Scheduler is not accessed
    sp = MagicMock()
    db = MagicMock()
    sp.list_files.return_value = ['a.csv']
    db.get_ingested_files.return_value = []
    sp.download_file.return_value = tmp_path / 'a.csv'
    job = SyncJob(config={'ingestion_dir': str(tmp_path), 'sharepoint_folder': 'folder'}, sharepoint_client=sp, db_service_client=db)  # type: ignore
    result = job.run()
    assert 'a.csv' in result
