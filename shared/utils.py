"""
utils.py
--------
Utility functions for the reporting pipeline.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import re
from typing import Optional, Tuple
from openpyxl.utils import column_index_from_string


def sanitize_filename(name: str) -> str:
    """
    Remove or replace invalid filesystem characters from a filename.
    Args:
        name (str): Input filename or base name.
    Returns:
        str: Sanitized filename.
    """
    # Allow alphanumerics, spaces, underscores, hyphens, and dots
    cleaned = re.sub(r'[^\w\s\-\.]', '', name)
    # Collapse whitespace
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned.strip('_')




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
