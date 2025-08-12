"""
Schedule domain model for scheduler - service
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass


class Schedule:
    """
    Schedule domain model
    TODO: Define attributes and methods
    """

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # TODO: Add domain - specific attributes