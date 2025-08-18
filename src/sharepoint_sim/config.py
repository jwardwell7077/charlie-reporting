"""Configuration loader for SharePoint CSV simulator.

Reads a dedicated TOML file `config/sharepoint_sim.toml` if present; otherwise uses defaults.

Config keys:
- seed: int | null (if null -> random seed each process)
- output_dir: relative or absolute path (default: sharepoint_sim)
- timezone: "UTC" for now (placeholder for future local offset support)
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path("config/sharepoint_sim.toml")
DEFAULT_OUTPUT = Path("sharepoint_sim")


@dataclass(frozen=True, slots=True)
class SimConfig:
    """Runtime configuration values for the simulator."""

    seed: int | None
    output_dir: Path
    timezone: str = "UTC"


def load_config(path: Path | None = None) -> SimConfig:
    """Load configuration from TOML file or return defaults.

    Parameters
    ----------
    path: Optional override path for tests.
    """
    p = path or CONFIG_PATH
    data = tomllib.loads(p.read_text()) if p.exists() else {}
    seed = data.get("seed")
    # Allow environment variable override primarily for tests / ephemeral runs
    env_override = os.getenv("SP_SIM_OUTPUT_DIR")
    output_dir = (
        Path(env_override)
        if env_override
        else Path(data.get("output_dir", DEFAULT_OUTPUT))
    )
    timezone = data.get("timezone", "UTC")
    return SimConfig(seed=seed, output_dir=output_dir, timezone=timezone)


__all__ = ["SimConfig", "load_config"]
