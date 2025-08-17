"""Characterization tests for Excel output helpers."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.excel import build_workbook, sheet_to_html


def test_build_workbook_creates_file(tmp_path: Path) -> None:
	df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
	out = tmp_path / "book.xlsx"
	path = build_workbook({"Sheet1": df}, out)
	assert path.exists()
	assert path == out


def test_sheet_to_html_contains_headers() -> None:
	df = pd.DataFrame({"a": [1], "b": [2]})
	html = sheet_to_html(df, max_rows=5)
	assert "<table" in html.lower()
	assert "a" in html and "b" in html


def test_sheet_to_html_empty_dataframe() -> None:
	df = pd.DataFrame({"a": [], "b": []})
	html = sheet_to_html(df)
	# Should still render table structure
	assert "<table" in html.lower()
