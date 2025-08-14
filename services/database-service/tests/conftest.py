"""Pytest configuration for database-service.

Makes this service's `src` package importable as top-level `src` by adding
the service root directory (the parent of the `src` folder) to sys.path.
"""
from __future__ import annotations

import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
if SERVICE_ROOT.exists():
    root_str = str(SERVICE_ROOT)
    if root_str not in sys.path:
        # Append so repository root 'src' (if any) remains first.
        sys.path.append(root_str)
