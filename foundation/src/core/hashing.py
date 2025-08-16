"""Small hashing utilities used for ingestion deduplication."""
from __future__ import annotations

import hashlib
from pathlib import Path


def file_sha256(path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hex digest for a file.

    Args:
        path: Path to the file.
        chunk_size: Read size in bytes for streaming; keep memory bounded.

    Returns:
        Hexadecimal digest string.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
