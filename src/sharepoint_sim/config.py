"""Configuration loader for SharePoint CSV simulator.

Reads a dedicated TOML file `config/sharepoint_sim.toml` if present; otherwise uses defaults.

Config keys:
- seed: int | null (if null -> random seed each process)
- output_dir: relative or absolute path (default: sharepoint_sim)
- timezone: "UTC" for now (placeholder for future local offset support)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

CONFIG_PATH = Path("config/sharepoint_sim.toml")
DEFAULT_OUTPUT = Path("sharepoint_sim")


@dataclass(frozen=True, slots=True)
class SimConfig:
    seed: int | None
    output_dir: Path
    timezone: str = "UTC"


def load_config(path: Path | None = None) -> SimConfig:
    p = path or CONFIG_PATH
    if p.exists():
        data = tomllib.loads(p.read_text())
    else:
        data = {}
    seed = data.get("seed")
    output_dir = Path(data.get("output_dir", DEFAULT_OUTPUT))
    timezone = data.get("timezone", "UTC")
    return SimConfig(seed=seed, output_dir=output_dir, timezone=timezone)


__all__ = ["SimConfig", "load_config"]
