"""Domain-to-ORM Mappers.
Convert between Pydantic domain models and SQLAlchemy ORM models.
"""


from ...domain.models.attachment import Attachment
from ...domain.models.email_record import (
    EmailPriority,
    EmailRecord,
    EmailStatus,
)
from ...domain.models.report import Report, ReportStatus, ReportType
from ...domain.models.user import User, UserRole, UserStatus
from .models.email_models import (
    AttachmentORM,
    EmailRecordORM,
    ReportORM,
    UserORM,
)


class EmailRecordMapper:
    """Maps between EmailRecord domain model and EmailRecordORM."""

    @staticmethod
    def to_orm(domain_model: EmailRecord) -> EmailRecordORM:
        return EmailRecordORM(
            id=domain_model.id,
            message_id=domain_model.message_id,
            subject=domain_model.subject,
            sender=domain_model.sender,
            recipients=domain_model.recipients,
            cc_recipients=domain_model.cc_recipients,
            bcc_recipients=domain_model.bcc_recipients,
            body_text=domain_model.body_text,
            body_html=domain_model.body_html,
            sent_date=domain_model.sent_date,
            received_date=domain_model.received_date,
            priority=domain_model.priority.value,
            status=domain_model.status.value,
            created_at=domain_model.received_date,
        )

    @staticmethod
    def to_domain(orm_model: EmailRecordORM) -> EmailRecord:
        return EmailRecord(
            id=orm_model.id,
            message_id=orm_model.message_id,
            subject=orm_model.subject,
            sender=orm_model.sender,
            recipients=orm_model.recipients or [],
            cc_recipients=orm_model.cc_recipients or [],
            bcc_recipients=orm_model.bcc_recipients or [],
            body_text=orm_model.body_text or "",
            body_html=orm_model.body_html or "",
            sent_date=orm_model.sent_date,
            received_date=orm_model.received_date,
            priority=EmailPriority(orm_model.priority),
            status=EmailStatus(orm_model.status),
            attachments=[],  # Loaded separately
        )


class AttachmentMapper:
    """Maps between Attachment domain model and AttachmentORM."""

    @staticmethod
    def to_orm(domain_model: Attachment) -> AttachmentORM:
        return AttachmentORM(
            id=domain_model.id,
            filename=domain_model.filename,
            content_type=domain_model.content_type,
            size_bytes=str(domain_model.size_bytes),  # Stored as text
            file_path=domain_model.file_path,
            content_id=domain_model.content_id,
            is_inline="true" if domain_model.is_inline else "false",
            created_at=domain_model.created_at,
        )

    @staticmethod
    def to_domain(orm_model: AttachmentORM) -> Attachment:
        return Attachment(
            id=orm_model.id,
            filename=orm_model.filename,
            content_type=orm_model.content_type,
            size_bytes=int(orm_model.size_bytes),
            file_path=orm_model.file_path,
            content_id=orm_model.content_id,
            is_inline=orm_model.is_inline == "true",
            created_at=orm_model.created_at,
        )


class UserMapper:
    """Maps between User domain model and UserORM."""

    @staticmethod
    def to_orm(domain_model: User) -> UserORM:
        return UserORM(
            id=domain_model.id,
            email=domain_model.email,
            username=domain_model.username,
            first_name=domain_model.first_name,
            last_name=domain_model.last_name,
            role=domain_model.role.value,
            status=domain_model.status.value,
            last_login=domain_model.last_login,
            created_at=domain_model.created_at,
        )

    @staticmethod
    def to_domain(orm_model: UserORM) -> User:
        return User(
            id=orm_model.id,
            email=orm_model.email,
            username=orm_model.username,
            first_name=orm_model.first_name or "",
            last_name=orm_model.last_name or "",
            role=UserRole(orm_model.role),
            status=UserStatus(orm_model.status),
            last_login=orm_model.last_login,
            created_at=orm_model.created_at,
        )


class ReportMapper:
    """Maps between Report domain model and ReportORM."""

    @staticmethod
    def to_orm(domain_model: Report) -> ReportORM:
        return ReportORM(
            id=domain_model.id,
            title=domain_model.title,
            description=domain_model.description,
            report_type=domain_model.report_type.value,
            status=domain_model.status.value,
            created_by_id=domain_model.created_by.id,
            email_record_ids=[
                str(email.id) for email in domain_model.email_records
            ],
            file_path=domain_model.file_path,
            completed_at=domain_model.completed_at,
            created_at=domain_model.created_at,
        )

    @staticmethod
    def to_domain(
        orm_model: ReportORM,
        created_by_user: User,
        email_records: list[EmailRecord] | None = None,
    ) -> Report:
        return Report(
            id=orm_model.id,
            title=orm_model.title,
            description=orm_model.description or "",
            report_type=ReportType(orm_model.report_type),
            status=ReportStatus(orm_model.status),
            created_by=created_by_user,
            email_records=email_records or [],
            file_path=orm_model.file_path,
            completed_at=orm_model.completed_at,
            created_at=orm_model.created_at,
        )
