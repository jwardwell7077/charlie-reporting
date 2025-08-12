"""
Excel_Format domain model for report - generator
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass


class Excel_Format:
    """
    Excel_Format domain model
    TODO: Define attributes and methods
    """

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # TODO: Add domain - specific attributes
