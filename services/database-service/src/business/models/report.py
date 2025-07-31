"""
Report domain model for database-service
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from typing import Optional
from datetime import datetime, timezone
@dataclass


class Report:
    """
    Report domain model
    TODO: Define attributes and methods
    """

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # TODO: Add domain-specific attributes
