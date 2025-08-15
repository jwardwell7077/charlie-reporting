"""Data_Model domain model for report - generator
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass


class Data_Model:
    """Data_Model domain model
    TODO: Define attributes and methods
    """

    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # TODO: Add domain - specific attributes
