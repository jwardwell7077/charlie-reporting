"""Validation tests for config/config.toml [reports] section.

These tests ensure the config declares exact column names and expected structure
for each dataset. They don't touch report generation yet.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, cast


def _load_config() -> Dict[str, Any]:
	# Prefer stdlib tomllib (Python 3.11+), fallback to 'toml' if available
	repo_root = Path(__file__).resolve().parents[2]
	cfg_path = repo_root / "config" / "config.toml"
	try:  # pragma: no cover - import path distinction only
		import tomllib  # type: ignore
		data = cfg_path.read_bytes()
		loaded: Mapping[str, Any] = tomllib.loads(data.decode("utf-8"))  # type: ignore[no-any-return]
		return dict(loaded)
	except Exception:
		import toml  # type: ignore
		text = cfg_path.read_text(encoding="utf-8")
		loaded2: Dict[str, Any] = toml.loads(text)  # type: ignore[no-any-return]
		return loaded2


def _get_dataset_columns(cfg: Dict[str, Any]) -> Dict[str, List[str]]:
	# Prefer [reports]. If absent, derive from [attachments] (strip .csv suffix)
	if "reports" in cfg and isinstance(cfg["reports"], dict):
		rep_any: Dict[str, Any] = dict(cast(Dict[str, Any], cfg["reports"]))
		out: Dict[str, List[str]] = {}
		for k, v in rep_any.items():
			out[str(k)] = list(cast(List[str], v)) if isinstance(v, list) else []
		return out
	if "attachments" in cfg and isinstance(cfg["attachments"], dict):
		att_any: Dict[str, Any] = dict(cast(Dict[str, Any], cfg["attachments"]))
		derived: Dict[str, List[str]] = {}
		for k, v in att_any.items():
			name = str(k)
			ds = name[:-4] if name.lower().endswith(".csv") else name
			derived[ds] = list(cast(List[str], v)) if isinstance(v, list) else []
		return derived
	return {}


def test_reports_section_exists_and_is_mapping() -> None:
	cfg = _load_config()
	mapping = _get_dataset_columns(cfg)
	assert mapping, "No report dataset columns found in config (expected [reports] or [attachments])"


def test_each_dataset_has_nonempty_string_columns() -> None:
	cfg = _load_config()
	reports = _get_dataset_columns(cfg)
	for dataset, cols in reports.items():
		assert isinstance(cols, list), f"[reports.{dataset}] must be a list"
		assert cols, f"[reports.{dataset}] must not be empty"
		for c in cols:
			assert isinstance(c, str), f"Column '{c}' in [reports.{dataset}] must be a string"
			# Ensure exactness: no surrounding whitespace or empty values
			assert c == c.strip() and c != "", (
				f"Column '{c}' in [reports.{dataset}] should be exact (no leading/trailing spaces)"
			)


def test_known_datasets_have_expected_columns_subset() -> None:
	"""Spot-check a few datasets for expected column labels.

	This is resilient: only asserts presence of some known labels, not full equality,
	so config can evolve without breaking the test for unrelated columns.
	"""
	cfg = _load_config()
	reports = _get_dataset_columns(cfg)

	# ACQ should include at least these columns
	if "ACQ" in reports:
		acq = reports["ACQ"]
		for expected in ("Agent Name", "Handle"):
			assert expected in acq

	# Productivity should include common columns
	if "Productivity" in reports:
		prod = reports["Productivity"]
		for expected in ("Agent Name", "Logged In"):
			assert expected in prod


def test_output_section_has_excel_settings() -> None:
	cfg = _load_config()
	assert "output" in cfg, "[output] section missing in config/config.toml"
	output_any = cfg["output"]
	assert isinstance(output_any, dict)
	output: Dict[str, Any] = dict(cast(Dict[str, Any], output_any))
	assert isinstance(output.get("excel_dir"), str) and output["excel_dir"], "output.excel_dir must be a non-empty string"
	assert isinstance(output.get("excel_prefix"), str) and output["excel_prefix"], "output.excel_prefix must be a non-empty string"

