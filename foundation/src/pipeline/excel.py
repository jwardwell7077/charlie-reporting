"""Excel workbook builder."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pandas as pd


def build_workbook(frames: Mapping[str, pd.DataFrame], output_path: Path) -> Path:
    """Write provided DataFrames to an Excel workbook on disk.

    Args:
        frames: Mapping of sheet name to DataFrame.
        output_path: Destination workbook file path.

    Returns:
        The `output_path` for convenience / chaining.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            # to_excel has partially unknown type info in stubs under strict pyright
            df.to_excel(writer, sheet_name=sheet, index=False)  # pyright: ignore[reportUnknownMemberType]
    return output_path


def sheet_to_html(frame: pd.DataFrame, max_rows: int = 50) -> str:
    """Convert a DataFrame preview to simple HTML table markup.

    Args:
        frame: Source DataFrame.
        max_rows: Limit of rows to include (head of frame).

    Returns:
        HTML string representing the head of the DataFrame.
    """
    return frame.head(max_rows).to_html(index=False)
