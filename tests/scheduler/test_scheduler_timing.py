"""
Timing and concurrency tests for scheduler cadence, non-overlap, and graceful shutdown.
These are designed to run quickly and deterministically.
"""
import time
import threading
from unittest.mock import MagicMock

from scheduler import Scheduler


def test_interval_cadence_triggers_repeated_runs():  # type: ignore[no-untyped-def]
    # Use sub-second interval for speed
    s = Scheduler(
        config={"interval_seconds": 0.05, "allow_overlap": False, "shutdown_timeout_seconds": 1},
        sharepoint_client=MagicMock(),
        db_service_client=MagicMock(),
    )  # type: ignore
    s.sync_job = MagicMock()
    s.start()
    time.sleep(0.18)  # allow ~3-4 ticks
    s.shutdown()
    # Expect at least 2 runs, given small interval and small test overhead
    assert s.sync_job.run.call_count >= 2


def test_non_overlap_skips_when_in_progress():  # type: ignore[no-untyped-def]
    s = Scheduler(
        config={"interval_seconds": 0.02, "allow_overlap": False, "shutdown_timeout_seconds": 1},
        sharepoint_client=MagicMock(),
        db_service_client=MagicMock(),
    )  # type: ignore
    # Make run take longer than interval to force overlap
    def long_run():
        time.sleep(0.08)
    s.sync_job = MagicMock()
    s.sync_job.run.side_effect = long_run
    s.start()
    time.sleep(0.2)
    s.shutdown()
    # With non-overlap, despite multiple ticks, runs should not explode
    # We expect around 2 calls: one starts, next tick(s) skip while in progress
    assert 1 <= s.sync_job.run.call_count <= 3


def test_manual_trigger_force_overrides_non_overlap():  # type: ignore[no-untyped-def]
    s = Scheduler(
        config={"interval_seconds": 1.0, "allow_overlap": False, "shutdown_timeout_seconds": 1},
        sharepoint_client=MagicMock(),
        db_service_client=MagicMock(),
    )  # type: ignore
    start_gate = threading.Event()
    finish_gate = threading.Event()

    def gated_run():
        start_gate.set()
        finish_gate.wait(timeout=1)

    s.sync_job = MagicMock()
    s.sync_job.run.side_effect = gated_run
    # Start a background run
    t = threading.Thread(target=s.run_once)
    t.start()
    start_gate.wait(timeout=0.5)
    # Trigger with force=True should attempt to run concurrently
    s.trigger(force=True)
    # Release first run
    finish_gate.set()
    t.join(timeout=1)
    assert s.sync_job.run.call_count >= 2


def test_graceful_shutdown_waits_for_inflight():  # type: ignore[no-untyped-def]
    s = Scheduler(
        config={"interval_seconds": 0.05, "allow_overlap": False, "shutdown_timeout_seconds": 0.5},
        sharepoint_client=MagicMock(),
        db_service_client=MagicMock(),
    )  # type: ignore
    blocker = threading.Event()

    def blocking_run():
        blocker.wait(timeout=0.2)  # shorter than shutdown timeout

    s.sync_job = MagicMock()
    s.sync_job.run.side_effect = blocking_run
    s.start()
    time.sleep(0.06)  # let one run start
    t0 = time.monotonic()
    s.shutdown()
    t1 = time.monotonic()
    # Shutdown should wait at least a little if a run was in progress
    assert (t1 - t0) >= 0.05
