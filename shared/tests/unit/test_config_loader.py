"""Basic tests for ConfigLoader and BaseServiceConfig functionality."""
from pathlib import Path

from shared.config import ConfigLoader, OutlookRelayConfig


def test_config_loader_creates_defaults(tmp_path: Path):
    cfg_dir = tmp_path / "conf"
    cfg_dir.mkdir()
    # Write minimal service.toml
    (cfg_dir / "service.toml").write_text("service_name='outlook-relay'\nport=8080\napi_key='x'\n")
    cfg = ConfigLoader.load_config(OutlookRelayConfig, "outlook-relay", config_dir=str(cfg_dir))
    assert cfg.service_name == "outlook-relay"
    assert cfg.port == 8080
    assert cfg.api_key == "x"


def test_config_loader_env_override(tmp_path: Path, monkeypatch):
    cfg_dir = tmp_path / "conf"
    cfg_dir.mkdir()
    (cfg_dir / "service.toml").write_text("service_name='outlook-relay'\nport=8080\napi_key='x'\n")
    monkeypatch.setenv("ENVIRONMENT", "production")
    cfg = ConfigLoader.load_config(OutlookRelayConfig, "outlook-relay", config_dir=str(cfg_dir))
    assert cfg.environment.value == "production"
