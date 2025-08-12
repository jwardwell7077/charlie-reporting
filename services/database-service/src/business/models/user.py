"""
User domain model for database-service
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    """
    User domain model
    TODO: Define attributes and methods
    """

    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # TODO: Add domain-specific attributes