"""SharePoint CSV Simulation package (lean generator implementation).

Modules:
- roster: load and access fixed employee roster.
- config: configuration loading for simulation.
- datasets: individual dataset generators.
- service: orchestration & file creation.
- api: FastAPI router exposing simulation endpoints.
"""
from __future__ import annotations

__all__ = [
    "__version__",
]

__version__ = "0.0.1"
