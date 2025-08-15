"""Job domain model for scheduler - service
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass


class Job:
    """Job domain model
    TODO: Define attributes and methods
    """

    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # TODO: Add domain - specific attributes