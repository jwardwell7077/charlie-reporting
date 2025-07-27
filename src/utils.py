import os
import re
from typing import Optional, Tuple
from openpyxl.utils import column_index_from_string


def sanitize_filename(name: str) -> str:
    """
    Remove or replace invalid filesystem characters from a filename.
    """
    # Allow alphanumerics, spaces, underscores, hyphens, and dots
    cleaned = re.sub(r'[^\w\s\-\.]', '', name)
    # Collapse whitespace
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned.strip('_')


def parse_excel_range(range_str: str) -> Tuple[int, int]:
    """
    Convert an Excel-style column range (e.g., 'G:I') into zero-based start and end indices.

    Returns:
        (start_idx, end_idx)
    """
    start_col, end_col = range_str.split(':')
    start_idx = column_index_from_string(start_col) - 1
    end_idx = column_index_from_string(end_col) - 1
    return start_idx, end_idx


def extract_date_from_filename(filename: str) -> Optional[str]:
    """
    Extract a date in YYYY-MM-DD format from a filename that contains '__YYYY-MM-DD'.

    Returns:
        The date string if found, otherwise None.
    """
    match = re.search(r'__(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None
