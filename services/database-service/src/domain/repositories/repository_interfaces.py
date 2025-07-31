"""
Abstract repository interfaces for domain models.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.attachment import Attachment
from ..models.user import User
from ..models.report import Report


from uuid import UUID
from typing import Optional
from typing import List


class AttachmentRepository(ABC):
        """Abstract repository for Attachment entities"""

    @abstractmethod

    async def save(self, attachment: Attachment) -> Attachment:
            """Save an attachment"""
        pass

    @abstractmethod

    async def find_by_id(self, attachment_id: UUID) -> Optional[Attachment]:
            """Find attachment by ID"""
        pass

    @abstractmethod

    async def find_by_email_id(self, email_id: UUID) -> List[Attachment]:
            """Find attachments by email ID"""
        pass

    @abstractmethod

    async def delete(self, attachment_id: UUID) -> bool:
            """Delete an attachment"""
        pass


class UserRepository(ABC):
        """Abstract repository for User entities"""

    @abstractmethod

    async def save(self, user: User) -> User:
            """Save a user"""
        pass

    @abstractmethod

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
            """Find user by ID"""
        pass

    @abstractmethod

    async def find_by_email(self, email: str) -> Optional[User]:
            """Find user by email"""
        pass

    @abstractmethod

    async def find_by_username(self, username: str) -> Optional[User]:
            """Find user by username"""
        pass

    @abstractmethod

    async def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[User]:
            """Find all users with optional pagination"""
        pass

    @abstractmethod

    async def delete(self, user_id: UUID) -> bool:
            """Delete a user"""
        pass


class ReportRepository(ABC):
        """Abstract repository for Report entities"""

    @abstractmethod

    async def save(self, report: Report) -> Report:
            """Save a report"""
        pass

    @abstractmethod

    async def find_by_id(self, report_id: UUID) -> Optional[Report]:
            """Find report by ID"""
        pass

    @abstractmethod

    async def find_by_user_id(self, user_id: UUID) -> List[Report]:
            """Find reports by user ID"""
        pass

    @abstractmethod

    async def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Report]:
            """Find all reports with optional pagination"""
        pass

    @abstractmethod

    async def delete(self, report_id: UUID) -> bool:
        """Delete a report"""
        pass
