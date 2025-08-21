"""Scheduler Control API.

This FastAPI app exposes endpoints to manage and observe the in-process Scheduler:
- Health and status
- Start/stop
- Manual trigger and run-once
- Get/update minimal runtime config

It is optional and can be run in-process for simple deployments.
"""
from __future__ import annotations

import threading
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from scheduler import DBServiceClient, Scheduler, SharePointClient

app = FastAPI(title="Scheduler API")
_lock = threading.Lock()


class _SchedulerHolder:
    """Mutable holder for lazily created singleton scheduler."""

    instance: Scheduler | None = None


class SchedulerConfig(BaseModel):
    """Scheduler configuration surface exposed via API."""
    interval_minutes: int | None = None
    interval_seconds: float | None = None
    jitter_seconds: int | None = None
    allow_overlap: bool | None = None
    shutdown_timeout_seconds: float | None = None
    sharepoint_folder: str | None = None
    ingestion_dir: str | None = None


def _get_or_create_scheduler() -> Scheduler:
    with _lock:
        if _SchedulerHolder.instance is None:
            cfg: dict[str, Any] = {
                "interval_minutes": 60,
                "jitter_seconds": 0,
                "allow_overlap": False,
                "shutdown_timeout_seconds": 30,
            }
            _SchedulerHolder.instance = Scheduler(cfg, SharePointClient(), DBServiceClient())
        return _SchedulerHolder.instance


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok"}


@app.get("/status")
def status() -> dict[str, Any]:
    """Return scheduler runtime status and current config."""
    s = _get_or_create_scheduler()
    return {
        "running": s.is_running(),
        "in_progress": s.in_progress(),
        "config": s.config,
    }


@app.post("/start")
def start() -> dict[str, str]:
    """Start the scheduler loop if not already running."""
    s = _get_or_create_scheduler()
    if s.is_running():
        return {"message": "scheduler already running"}
    s.start()
    return {"message": "scheduler started"}


@app.post("/trigger")
def trigger(force: bool = False) -> dict[str, Any]:
    """Manually trigger a run; set force=true to bypass non-overlap policy."""
    s = _get_or_create_scheduler()
    started = s.trigger(force=force)
    return {"started": started}


@app.post("/run-once")
def run_once() -> dict[str, str]:
    """Run the scheduled job once synchronously."""
    s = _get_or_create_scheduler()
    s.run_once()
    return {"message": "run_once invoked"}


@app.post("/shutdown")
def shutdown() -> dict[str, str]:
    """Signal the scheduler to stop and wait for in-flight work."""
    s = _get_or_create_scheduler()
    s.shutdown()
    return {"message": "scheduler stopped"}


@app.get("/config")
def get_config() -> dict[str, Any]:
    """Return the current scheduler configuration."""
    s = _get_or_create_scheduler()
    return s.config


@app.put("/config")
def update_config(cfg: SchedulerConfig) -> dict[str, Any]:
    """Update mutable configuration keys; returns the resulting config."""
    s = _get_or_create_scheduler()
    # Update only provided fields
    for k, v in cfg.model_dump(exclude_none=True).items():
        s.config[k] = v
    # If interval config changes while running, changes apply on next tick
    return s.config
