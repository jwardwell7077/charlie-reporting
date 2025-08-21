"""Scheduler Control API.

This FastAPI app exposes endpoints to manage and observe the in-process Scheduler:
- Health and status
- Start/stop
- Manual trigger and run-once
- Get/update minimal runtime config

It is optional and can be run in-process for simple deployments.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import threading

from scheduler import Scheduler, SharePointClient, DBServiceClient


app = FastAPI(title="Scheduler API")
_lock = threading.Lock()
_scheduler: Optional[Scheduler] = None


class SchedulerConfig(BaseModel):
    interval_minutes: Optional[int] = None
    interval_seconds: Optional[float] = None
    jitter_seconds: Optional[int] = None
    allow_overlap: Optional[bool] = None
    shutdown_timeout_seconds: Optional[float] = None
    sharepoint_folder: Optional[str] = None
    ingestion_dir: Optional[str] = None


def _get_or_create_scheduler() -> Scheduler:
    global _scheduler
    with _lock:
        if _scheduler is None:
            cfg: Dict[str, Any] = {
                "interval_minutes": 60,
                "jitter_seconds": 0,
                "allow_overlap": False,
                "shutdown_timeout_seconds": 30,
            }
            _scheduler = Scheduler(cfg, SharePointClient(), DBServiceClient())
        return _scheduler


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/status")
def status() -> Dict[str, Any]:
    s = _get_or_create_scheduler()
    return {
        "running": s.is_running(),
        "in_progress": s.in_progress(),
        "config": s.config,
    }


@app.post("/start")
def start() -> Dict[str, str]:
    s = _get_or_create_scheduler()
    if s.is_running():
        return {"message": "scheduler already running"}
    s.start()
    return {"message": "scheduler started"}


@app.post("/trigger")
def trigger(force: bool = False) -> Dict[str, Any]:
    s = _get_or_create_scheduler()
    started = s.trigger(force=force)
    return {"started": started}


@app.post("/run-once")
def run_once() -> Dict[str, str]:
    s = _get_or_create_scheduler()
    s.run_once()
    return {"message": "run_once invoked"}


@app.post("/shutdown")
def shutdown() -> Dict[str, str]:
    s = _get_or_create_scheduler()
    s.shutdown()
    return {"message": "scheduler stopped"}


@app.get("/config")
def get_config() -> Dict[str, Any]:
    s = _get_or_create_scheduler()
    return s.config


@app.put("/config")
def update_config(cfg: SchedulerConfig) -> Dict[str, Any]:
    s = _get_or_create_scheduler()
    # Update only provided fields
    for k, v in cfg.model_dump(exclude_none=True).items():
        s.config[k] = v
    # If interval config changes while running, changes apply on next tick
    return s.config
