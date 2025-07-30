"""
Repository implementations using Pydantic domain models with SQLAlchemy.
Provides clean conversion between domain and infrastructure layers.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from ..domain.models.email_record import EmailRecord
from ..domain.models.attachment import Attachment
from ..domain.models.user import User
from ..domain.models.report import Report
from ..domain.repositories.email_repository_interface import (
    EmailRepositoryInterface
)
from ..domain.repositories.repository_interfaces import (
    AttachmentRepository, UserRepository, ReportRepository
)
from .persistence.models.email_models import (
    EmailRecordORM, AttachmentORM, UserORM, ReportORM
)
from .persistence.mappers import (
    EmailRecordMapper, AttachmentMapper, UserMapper, ReportMapper
)


class SQLAlchemyEmailRepository(EmailRepositoryInterface):
    """SQLAlchemy implementation of EmailRepository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def save(self, email_record: EmailRecord) -> EmailRecord:
        """Save an email record"""
        orm_model = EmailRecordMapper.to_orm(email_record)
        
        # Check if exists (upsert behavior)
        existing = self.session.get(EmailRecordORM, email_record.id)
        if existing:
            # Update existing
            for key, value in orm_model.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            orm_result = existing
        else:
            # Insert new
            self.session.add(orm_model)
            orm_result = orm_model
        
        self.session.flush()
        return EmailRecordMapper.to_domain(orm_result)
    
    async def find_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        """Find email record by ID"""
        orm_model = self.session.get(EmailRecordORM, email_id)
        if orm_model:
            return EmailRecordMapper.to_domain(orm_model)
        return None
    
    async def find_by_message_id(self, message_id: str) -> Optional[EmailRecord]:
        """Find email record by message ID"""
        stmt = select(EmailRecordORM).where(EmailRecordORM.message_id == message_id)
        result = self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model:
            return EmailRecordMapper.to_domain(orm_model)
        return None
    
    async def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[EmailRecord]:
        """Find all email records with optional pagination"""
        stmt = select(EmailRecordORM).offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = self.session.execute(stmt)
        orm_models = result.scalars().all()
        return [EmailRecordMapper.to_domain(orm) for orm in orm_models]
    
    async def delete(self, email_id: UUID) -> bool:
        """Delete an email record"""
        stmt = delete(EmailRecordORM).where(EmailRecordORM.id == email_id)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.rowcount > 0


class SQLAlchemyAttachmentRepository(AttachmentRepository):
    """SQLAlchemy implementation of AttachmentRepository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def save(self, attachment: Attachment) -> Attachment:
        """Save an attachment"""
        orm_model = AttachmentMapper.to_orm(attachment)
        
        existing = self.session.get(AttachmentORM, attachment.id)
        if existing:
            for key, value in orm_model.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            orm_result = existing
        else:
            self.session.add(orm_model)
            orm_result = orm_model
        
        self.session.flush()
        return AttachmentMapper.to_domain(orm_result)
    
    async def find_by_id(self, attachment_id: UUID) -> Optional[Attachment]:
        """Find attachment by ID"""
        orm_model = self.session.get(AttachmentORM, attachment_id)
        if orm_model:
            return AttachmentMapper.to_domain(orm_model)
        return None
    
    async def find_by_email_id(self, email_id: UUID) -> List[Attachment]:
        """Find attachments by email ID"""
        stmt = select(AttachmentORM).where(AttachmentORM.email_record_id == email_id)
        result = self.session.execute(stmt)
        orm_models = result.scalars().all()
        return [AttachmentMapper.to_domain(orm) for orm in orm_models]
    
    async def delete(self, attachment_id: UUID) -> bool:
        """Delete an attachment"""
        stmt = delete(AttachmentORM).where(AttachmentORM.id == attachment_id)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.rowcount > 0


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def save(self, user: User) -> User:
        """Save a user"""
        orm_model = UserMapper.to_orm(user)
        
        existing = self.session.get(UserORM, user.id)
        if existing:
            for key, value in orm_model.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            orm_result = existing
        else:
            self.session.add(orm_model)
            orm_result = orm_model
        
        self.session.flush()
        return UserMapper.to_domain(orm_result)
    
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID"""
        orm_model = self.session.get(UserORM, user_id)
        if orm_model:
            return UserMapper.to_domain(orm_model)
        return None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        stmt = select(UserORM).where(UserORM.email == email)
        result = self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model:
            return UserMapper.to_domain(orm_model)
        return None
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        stmt = select(UserORM).where(UserORM.username == username)
        result = self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model:
            return UserMapper.to_domain(orm_model)
        return None
    
    async def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[User]:
        """Find all users with optional pagination"""
        stmt = select(UserORM).offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = self.session.execute(stmt)
        orm_models = result.scalars().all()
        return [UserMapper.to_domain(orm) for orm in orm_models]
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user"""
        stmt = delete(UserORM).where(UserORM.id == user_id)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.rowcount > 0


class SQLAlchemyReportRepository(ReportRepository):
    """SQLAlchemy implementation of ReportRepository"""
    
    def __init__(self, session: Session, user_repo: UserRepository, 
                 email_repo: EmailRepositoryInterface):
        self.session = session
        self.user_repo = user_repo
        self.email_repo = email_repo
    
    async def save(self, report: Report) -> Report:
        """Save a report"""
        orm_model = ReportMapper.to_orm(report)
        
        existing = self.session.get(ReportORM, report.id)
        if existing:
            for key, value in orm_model.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            orm_result = existing
        else:
            self.session.add(orm_model)
            orm_result = orm_model
        
        self.session.flush()
        
        # Load related data for domain model
        created_by_user = await self.user_repo.find_by_id(orm_result.created_by_id)
        return ReportMapper.to_domain(orm_result, created_by_user, report.email_records)
    
    async def find_by_id(self, report_id: UUID) -> Optional[Report]:
        """Find report by ID"""
        orm_model = self.session.get(ReportORM, report_id)
        if orm_model:
            # Load related data
            created_by_user = await self.user_repo.find_by_id(orm_model.created_by_id)
            
            # Load email records if they exist
            email_records = []
            if orm_model.email_record_ids:
                for email_id_str in orm_model.email_record_ids:
                    email_record = await self.email_repo.find_by_id(UUID(email_id_str))
                    if email_record:
                        email_records.append(email_record)
            
            return ReportMapper.to_domain(orm_model, created_by_user, email_records)
        return None
    
    async def find_by_user_id(self, user_id: UUID) -> List[Report]:
        """Find reports by user ID"""
        stmt = select(ReportORM).where(ReportORM.created_by_id == user_id)
        result = self.session.execute(stmt)
        orm_models = result.scalars().all()
        
        reports = []
        for orm_model in orm_models:
            created_by_user = await self.user_repo.find_by_id(orm_model.created_by_id)
            # Don't load email records for list view (performance)
            report = ReportMapper.to_domain(orm_model, created_by_user, [])
            reports.append(report)
        
        return reports
    
    async def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Report]:
        """Find all reports with optional pagination"""
        stmt = select(ReportORM).offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = self.session.execute(stmt)
        orm_models = result.scalars().all()
        
        reports = []
        for orm_model in orm_models:
            created_by_user = await self.user_repo.find_by_id(orm_model.created_by_id)
            # Don't load email records for list view (performance)
            report = ReportMapper.to_domain(orm_model, created_by_user, [])
            reports.append(report)
        
        return reports
    
    async def delete(self, report_id: UUID) -> bool:
        """Delete a report"""
        stmt = delete(ReportORM).where(ReportORM.id == report_id)
        result = self.session.execute(stmt)
        self.session.flush()
        return result.rowcount > 0
