"""
Scheduler implementation with interval scheduling, non-overlap, and graceful shutdown.
Follows the design spec in docs/design-specs/scheduler_design_spec.md.
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime, timedelta, timezone
import threading
import time
import random
import scheduler_sharepoint_api as sp_api

# --- DBServiceClient ---
class DBServiceClient:
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or "http://localhost:8000"
    def get_ingested_files(self, start_time: str, end_time: str) -> List[str]:
        """Query the DB service for already ingested files in the given interval."""
        # TODO: Implement real HTTP call
        return []

# --- SharePointClient ---
class SharePointClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config: Dict[str, Any] = config or {}

    def authenticate(self) -> bool:
        """Authenticate with SharePoint/Graph API using sim-backed stub."""
        sp_api.authenticate_sharepoint()
        return True

    def list_files(self, folder: str) -> List[str]:
        """List files in a SharePoint/Graph API folder using sim-backed stub."""
        return sp_api.list_sharepoint_files(folder)

    def download_file(self, folder: str, filename: str, dest: Path) -> Path:
        """Download a file from SharePoint/Graph API using sim-backed stub."""
        return sp_api.download_sharepoint_file(folder, filename, dest)

# --- SyncJob ---
class SyncJob:
    def __init__(self, config: Dict[str, Any], sharepoint_client: SharePointClient, db_service_client: DBServiceClient):
        self.config: Dict[str, Any] = config
        self.sharepoint_client = sharepoint_client
        self.db_service_client = db_service_client
        self.logger = logging.getLogger("SyncJob")
    def run(self) -> List[str]:
        """Run one sync: get already ingested, list new, download new, move files.

        Returns:
            List[str]: Filenames successfully downloaded.
        """
        folder: str = self.config.get("sharepoint_folder", "")
        ingestion_dir = Path(self.config.get("ingestion_dir", "."))
        ingestion_dir.mkdir(parents=True, exist_ok=True)

        # Determine a simple time window (last hour) for querying ingested files
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        # Query already ingested files
        already_ingested: List[str] = self.db_service_client.get_ingested_files(
            start_time.isoformat(timespec="seconds"), end_time.isoformat(timespec="seconds")
        )

        # List available files from SharePoint
        files: List[str] = self.sharepoint_client.list_files(folder)
        if not files:
            return []

        downloaded: List[str] = []
        for name in files:
            if name in already_ingested:
                continue
            dest = ingestion_dir / name
            try:
                self.sharepoint_client.download_file(folder, name, dest)
            except Exception as exc:  # noqa: BLE001
                self.logger.error("Failed to download %s: %s", name, exc)
                continue
            downloaded.append(name)

        return downloaded
    def _move_file(self, path: Path) -> None:
        """Move file to ingestion directory (stub)."""
        # TODO: Implement real move
        pass

# --- Scheduler ---
class Scheduler:
    def __init__(self, config: Dict[str, Any], sharepoint_client: SharePointClient, db_service_client: DBServiceClient):
        self.config: Dict[str, Any] = config
        self.sharepoint_client = sharepoint_client
        self.db_service_client = db_service_client
        self.sync_job = SyncJob(config, sharepoint_client, db_service_client)
        self.logger = logging.getLogger("Scheduler")
        # Scheduling state
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._running_lock = threading.Lock()
        self._in_progress = False
    def _schedule_jobs(self) -> None:
        """Register scheduled jobs (stub for patching in tests)."""
        # TODO: Integrate with APScheduler or similar
        return
    def _handle_shutdown(self) -> None:
        """Handle graceful shutdown (stub for patching in tests)."""
        return
    def _run_job_if_allowed(self, *, force: bool = False) -> bool:
        """Run the sync job respecting overlap policy.

        Returns True if the job started; False if skipped due to overlap.
        """
        allow_overlap = bool(self.config.get("allow_overlap", False))
    # overlap_policy reserved for future queue behavior; default is skip

        with self._running_lock:
            if self._in_progress and not (allow_overlap or force):
                # Skip according to policy (queue is not implemented in-process; next tick will run)
                self.logger.warning("Skip run: previous job still in progress (overlap disabled)")
                return False
            # Mark as in-progress
            self._in_progress = True

        try:
            self.sync_job.run()
        finally:
            with self._running_lock:
                self._in_progress = False
        return True

    def run_once(self) -> None:
        self.logger.info("Running scheduled sync job...")
        # run_once is a direct call; allow_overlap does not apply here unless concurrently invoked
        self._run_job_if_allowed()

    def trigger(self, *, force: bool = False) -> bool:
        self.logger.info("Manual trigger of sync job%s...", " (force)" if force else "")
        return self._run_job_if_allowed(force=force)

    def _scheduler_loop(self) -> None:
        interval_minutes = int(self.config.get("interval_minutes", 60))
        interval_seconds = float(self.config.get("interval_seconds", interval_minutes * 60))
        jitter_seconds = int(self.config.get("jitter_seconds", 0))
        self.logger.info(
            "Scheduler loop started (interval=%ss, jitter=%ss)", interval_seconds, jitter_seconds
        )
        while not self._stop_event.is_set():
            start = time.monotonic()
            try:
                self._run_job_if_allowed()
            except Exception as exc:  # noqa: BLE001
                self.logger.exception("Scheduled run failed: %s", exc)
            # Compute next sleep with optional jitter
            base_delay = max(0.001, float(interval_seconds))
            jitter = random.randint(0, jitter_seconds) if jitter_seconds > 0 else 0
            elapsed = time.monotonic() - start
            sleep_for = max(0, base_delay + jitter - elapsed)
            # Wait but wake early on shutdown
            if self._stop_event.wait(timeout=sleep_for):
                break
        self.logger.info("Scheduler loop exiting")

    def start(self) -> None:
        """Start the background scheduler loop."""
        if self._thread and self._thread.is_alive():
            self.logger.info("Scheduler already running")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._scheduler_loop, name="SchedulerLoop", daemon=True)
        self._thread.start()

    def shutdown(self) -> None:
        """Signal the scheduler to stop and wait for in-flight work up to timeout."""
        self.logger.info("Scheduler shutting down...")
        self._stop_event.set()
        timeout = float(self.config.get("shutdown_timeout_seconds", 30))
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        # Best-effort wait for in-flight job
        t0 = time.monotonic()
        while True:
            with self._running_lock:
                if not self._in_progress:
                    break
            if time.monotonic() - t0 > timeout:
                self.logger.warning("Shutdown timeout reached with job still in progress")
                break
            time.sleep(0.05)
        self.logger.info("Scheduler shutdown complete")
    # TODO: Add signal handling, full config loading, cron times support.

    # --- Introspection helpers for API/UI ---
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def in_progress(self) -> bool:
        with self._running_lock:
            return self._in_progress

# --- CLI Entrypoint ---
def main():
    # TODO: Parse CLI args, load config, instantiate Scheduler, run/trigger
    pass

# Provide a minimal load_config stub to support tests that patch this symbol.
def load_config() -> Dict[str, Any]:
    """Load scheduler configuration (stub for tests)."""
    return {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": "./data/incoming",
        "interval_minutes": 60,
        "max_retries": 3,
        "retry_delay_seconds": 60,
    }
