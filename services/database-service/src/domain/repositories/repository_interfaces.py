"""
Abstract repository interfaces for domain models.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..models.attachment import Attachment
from ..models.user import User
from ..models.report import Report


class AttachmentRepository(ABC):
    """Abstract repository for Attachment entities."""

    @abstractmethod
    async def save(self, attachment: Attachment) -> Attachment:
        """Save an attachment"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, attachment_id: UUID) -> Optional[Attachment]:
        """Find attachment by ID"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_email_id(self, email_id: UUID) -> List[Attachment]:
        """Find attachments by email ID"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, attachment_id: UUID) -> bool:
        """Delete an attachment"""
        raise NotImplementedError


class UserRepository(ABC):
    """Abstract repository for User entities."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[User]:
        """Find all users with optional pagination"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user"""
        raise NotImplementedError


class ReportRepository(ABC):
    """Abstract repository for Report entities."""

    @abstractmethod
    async def save(self, report: Report) -> Report:
        """Save a report"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, report_id: UUID) -> Optional[Report]:
        """Find report by ID"""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[Report]:
        """Find reports by user ID"""
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[Report]:
        """Find all reports with optional pagination"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, report_id: UUID) -> bool:
        """Delete a report"""
        raise NotImplementedError
