"""SharePoint/Graph API shim that proxies to the simulator HTTP service.

This module provides a minimal compatibility layer for legacy callers that expect
"authenticate", "list files", and "download" functions. Under the hood it calls the
SharePoint simulator FastAPI endpoints (mounted under /sim).
"""
from __future__ import annotations

from typing import List
from pathlib import Path
import os

try:
    import requests  # type: ignore
except Exception as exc:  # pragma: no cover - environment dependent
    requests = None  # type: ignore


def _base_url() -> str:
    # Prefer environment, fall back to localhost:8001
    return os.environ.get("SIM_BASE_URL", "http://localhost:8001").rstrip("/")


def authenticate_sharepoint() -> None:
    """Authenticate with SharePoint/Graph API (no-op for simulator)."""
    if requests is None:  # pragma: no cover
        return
    try:
        requests.get(f"{_base_url()}/sim/spec", timeout=5)
    except Exception:
        # Reachability is best-effort; callers can proceed and handle failures lazily
        return


def list_sharepoint_files(folder: str) -> List[str]:
    """List files via the simulator service.

    Args:
        folder: SharePoint folder path (ignored by simulator).
    Returns:
        List of filenames available on the simulator.
    """
    if requests is None:  # pragma: no cover
        return []
    resp = requests.get(f"{_base_url()}/sim/files", timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    files = payload.get("files", [])
    return [str(f.get("filename")) for f in files if f.get("filename")]


def download_sharepoint_file(folder: str, filename: str, dest: Path) -> Path:
    """Download a file via the simulator service to the destination path.

    Args:
        folder: SharePoint folder (ignored by simulator)
        filename: File to download
        dest: Destination path on disk
    Returns:
        The destination path
    """
    if requests is None:  # pragma: no cover
        raise RuntimeError("HTTP client unavailable in this environment")
    resp = requests.get(f"{_base_url()}/sim/download/{filename}", timeout=30)
    resp.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Write bytes; requests returns bytes for content
    dest.write_bytes(resp.content)
    return dest
