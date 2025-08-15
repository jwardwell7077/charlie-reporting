"""Excel workbook builder."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd


def build_workbook(frames: Mapping[str, pd.DataFrame], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:  # type: ignore[arg-type]
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    return output_path


def sheet_to_html(frame: pd.DataFrame, max_rows: int = 50) -> str:
    return frame.head(max_rows).to_html(index=False)
