"""
Abstract EmailRepository interface.
"""

from abc import abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .base_repository import BaseRepository
from ..models.email_record import EmailRecord, EmailStatus


class EmailRepositoryInterface(BaseRepository):
    """Abstract repository for EmailRecord entities"""
    
    # Base repository methods with type hints
    @abstractmethod
    async def create(self, email_record: EmailRecord) -> EmailRecord:
        """Create a new email record"""
        pass
    
    @abstractmethod
    async def get_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        """Get email record by ID"""
        pass
    
    @abstractmethod
    async def update(self, email_record: EmailRecord) -> EmailRecord:
        """Update an existing email record"""
        pass
    
    @abstractmethod
    async def delete(self, email_id: UUID) -> bool:
        """Delete an email record by ID"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[EmailRecord]:
        """List all email records"""
        pass
    
    @abstractmethod
    async def exists(self, email_id: UUID) -> bool:
        """Check if email record exists by ID"""
        pass
    
    # Email-specific methods
    @abstractmethod
    async def get_by_message_id(
        self, message_id: str
    ) -> Optional[EmailRecord]:
        """Find email record by message ID"""
        pass
    
    @abstractmethod
    async def get_by_sender(self, sender: str) -> List[EmailRecord]:
        """Find email records by sender"""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[EmailRecord]:
        """Find email records within a date range"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: EmailStatus) -> List[EmailRecord]:
        """Find email records by status"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: EmailStatus) -> int:
        """Count email records by status"""
        pass
