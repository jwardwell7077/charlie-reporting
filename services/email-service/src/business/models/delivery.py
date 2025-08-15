"""Delivery domain model for email - service
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass


class Delivery:
    """Delivery domain model
    TODO: Define attributes and methods
    """

    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # TODO: Add domain - specific attributes