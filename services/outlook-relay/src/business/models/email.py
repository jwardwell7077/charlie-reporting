"""
Email domain model for outlook-relay
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Email:
    """
    Email domain model
    TODO: Define attributes and methods
    """
    
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # TODO: Add domain-specific attributes
