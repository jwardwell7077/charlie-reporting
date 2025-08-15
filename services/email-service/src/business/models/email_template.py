"""Email_Template domain model for email - service
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass


class Email_Template:
    """Email_Template domain model
    TODO: Define attributes and methods
    """

    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # TODO: Add domain - specific attributes