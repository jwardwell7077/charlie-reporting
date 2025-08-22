"""
Scheduler FastAPI adapter (placeholder).

This module intentionally remains minimal. The scheduler is currently a CLI-driven component
implemented in `scheduler.py` with a `SyncJob` that interacts with the SharePoint simulator
and the DB Service API. If/when an HTTP control plane is desired for the scheduler
(e.g., start/stop/status endpoints), the FastAPI app and routes will live here.

Tests reference the CLI and core classes directly; keeping this file present avoids
import errors in places where `scheduler_api` might be referenced.
"""

__all__: list[str] = []
