"""
Tests for Email Business Service.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.domain.models.email_record import EmailRecord, EmailStatus, EmailPriority
from src.domain.models.user import User, UserRole, UserStatus
from src.business.services.email_service import EmailService


class TestEmailService:
    """Test email business service functionality"""
    
    @pytest.fixture
    def mock_email_repository(self):
        """Mock email repository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection"""
        return AsyncMock()
    
    @pytest.fixture
    def email_service(self, mock_email_repository, mock_db_connection):
        """Email service instance"""
        return EmailService(
            email_repository=mock_email_repository,
            db_connection=mock_db_connection
        )
    
    @pytest.fixture
    def sample_email_data(self):
        """Sample email data for testing"""
        return {
            "message_id": "test@example.com",
            "subject": "Test Email",
            "sender": "sender@example.com",
            "recipients": ["recipient@example.com"],
            "cc_recipients": [],
            "bcc_recipients": [],
            "body_text": "Test body",
            "body_html": "<p>Test body</p>",
            "sent_date": datetime.now(),
            "received_date": datetime.now(),
            "priority": "normal"
        }
    
    @pytest.mark.asyncio
    async def test_import_email_success(self, email_service, mock_email_repository, sample_email_data):
        """Test successful email import"""
        # Setup
        mock_email_repository.find_by_message_id.return_value = None  # No duplicate
        mock_email_repository.save.return_value = EmailRecord(
            id=uuid4(),
            message_id=sample_email_data["message_id"],
            subject=sample_email_data["subject"],
            sender=sample_email_data["sender"],
            recipients=sample_email_data["recipients"],
            cc_recipients=[],
            bcc_recipients=[],
            body_text=sample_email_data["body_text"],
            body_html=sample_email_data["body_html"],
            sent_date=sample_email_data["sent_date"],
            received_date=sample_email_data["received_date"],
            priority=EmailPriority.NORMAL,
            status=EmailStatus.RECEIVED,
            attachments=[]
        )
        
        # Execute
        result = await email_service.import_email(sample_email_data)
        
        # Verify
        assert result is not None
        assert result.message_id == sample_email_data["message_id"]
        assert result.status == EmailStatus.RECEIVED
        mock_email_repository.find_by_message_id.assert_called_once()
        mock_email_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_import_email_duplicate_raises_error(self, email_service, mock_email_repository, sample_email_data):
        """Test that importing duplicate email raises error"""
        # Setup - simulate existing email
        existing_email = EmailRecord(
            id=uuid4(),
            message_id=sample_email_data["message_id"],
            subject="Existing",
            sender="existing@example.com",
            recipients=["existing@example.com"],
            cc_recipients=[],
            bcc_recipients=[],
            body_text="",
            body_html="",
            sent_date=datetime.now(),
            received_date=datetime.now(),
            priority=EmailPriority.NORMAL,
            status=EmailStatus.RECEIVED,
            attachments=[]
        )
        mock_email_repository.find_by_message_id.return_value = existing_email
        
        # Execute & Verify
        with pytest.raises(ValueError, match="already exists"):
            await email_service.import_email(sample_email_data)
    
    @pytest.mark.asyncio
    async def test_process_email_success(self, email_service, mock_email_repository):
        """Test successful email processing"""
        # Setup
        email_id = uuid4()
        email = EmailRecord(
            id=email_id,
            message_id="test@example.com",
            subject="Test",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            cc_recipients=[],
            bcc_recipients=[],
            body_text="",
            body_html="",
            sent_date=datetime.now(),
            received_date=datetime.now(),
            priority=EmailPriority.NORMAL,
            status=EmailStatus.RECEIVED,
            attachments=[]
        )
        
        processed_email = EmailRecord(
            id=email_id,
            message_id="test@example.com",
            subject="Test",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            cc_recipients=[],
            bcc_recipients=[],
            body_text="",
            body_html="",
            sent_date=datetime.now(),
            received_date=datetime.now(),
            priority=EmailPriority.NORMAL,
            status=EmailStatus.PROCESSED,
            attachments=[]
        )
        
        mock_email_repository.find_by_id.return_value = email
        mock_email_repository.save.return_value = processed_email
        
        # Execute
        result = await email_service.process_email(email_id)
        
        # Verify
        assert result.status == EmailStatus.PROCESSED
        mock_email_repository.find_by_id.assert_called_once_with(email_id)
        mock_email_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_email_not_found(self, email_service, mock_email_repository):
        """Test processing non-existent email raises error"""
        # Setup
        email_id = uuid4()
        mock_email_repository.find_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Email not found"):
            await email_service.process_email(email_id)
    
    @pytest.mark.asyncio
    async def test_get_email_statistics(self, email_service, mock_email_repository):
        """Test email statistics generation"""
        # Setup
        mock_email_repository.count_by_status.side_effect = [5, 10, 2, 1]  # received, processed, failed, archived
        mock_email_repository.find_by_date_range.return_value = [
            # Mock recent emails
            EmailRecord(
                id=uuid4(),
                message_id="recent1@example.com",
                subject="Recent 1",
                sender="sender@example.com",
                recipients=["recipient1@example.com"],
                cc_recipients=[],
                bcc_recipients=[],
                body_text="",
                body_html="",
                sent_date=datetime.now(),
                received_date=datetime.now(),
                priority=EmailPriority.HIGH,
                status=EmailStatus.RECEIVED,
                attachments=[]
            ),
            EmailRecord(
                id=uuid4(),
                message_id="recent2@example.com",
                subject="Recent 2",
                sender="sender@example.com",
                recipients=["recipient2@example.com"],
                cc_recipients=[],
                bcc_recipients=[],
                body_text="",
                body_html="",
                sent_date=datetime.now(),
                received_date=datetime.now(),
                priority=EmailPriority.NORMAL,
                status=EmailStatus.RECEIVED,
                attachments=[]
            )
        ]
        
        # Execute
        stats = await email_service.get_email_statistics()
        
        # Verify
        assert "count_received" in stats
        assert "count_processed" in stats
        assert "recent_count" in stats
        assert "high_priority_count" in stats
        assert stats["recent_count"] == 2
        assert stats["high_priority_count"] == 1
