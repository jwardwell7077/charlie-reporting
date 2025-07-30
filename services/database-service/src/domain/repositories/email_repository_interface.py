"""
Abstract EmailRepository interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..models.email_record import EmailRecord


class EmailRepositoryInterface(ABC):
    """Abstract repository for EmailRecord entities"""
    
    @abstractmethod
    async def save(self, email_record: EmailRecord) -> EmailRecord:
        """Save an email record"""
        pass
    
    @abstractmethod
    async def find_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        """Find email record by ID"""
        pass
    
    @abstractmethod
    async def find_by_message_id(self, message_id: str) -> Optional[EmailRecord]:
        """Find email record by message ID"""
        pass
    
    @abstractmethod
    async def find_all(self, limit: Optional[int] = None, 
                      offset: int = 0) -> List[EmailRecord]:
        """Find all email records with optional pagination"""
        pass
    
    @abstractmethod
    async def delete(self, email_id: UUID) -> bool:
        """Delete an email record"""
        pass
