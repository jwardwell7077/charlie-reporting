"""Unit tests for EmailRecord repository.
Following TDD - these tests are written BEFORE implementation.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.domain.models.email_record import EmailRecord, EmailStatus
from src.domain.repositories.email_repository import EmailRepository
from src.infrastructure.persistence.database import DatabaseConnection
from src.infrastructure.persistence.models.email_models import EmailRecordORM


class TestEmailRepository:
    """Test EmailRecord repository implementation"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection"""
        return AsyncMock(spec=DatabaseConnection)
    
    @pytest.fixture
    def email_repository(self, mock_db_connection):
        """EmailRepository instance with mocked dependencies"""
        return EmailRepository(mock_db_connection)
    
    @pytest.fixture
    def sample_email_record(self):
        """Sample email record for testing"""
        return EmailRecord(
            message_id="test-message-123@example.com",
            subject="Test Email Subject",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            sent_date=datetime(2025, 7, 29, 10, 0, 0, tzinfo=UTC)
        )

    def setup_mock_session_with_result(self, email_repository, mock_result):
        """Helper method to setup mock session with result"""
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        db_connection = email_repository._db_connection
        get_session_mock = db_connection.get_session.return_value
        get_session_mock.__aenter__ = AsyncMock(return_value=mock_session)
        get_session_mock.__aexit__ = AsyncMock(return_value=None)
        
        return mock_session
    
    def setup_mock_session(self, email_repository, mock_session):
        """Helper to set up mock session context manager"""
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
    
    @pytest.mark.asyncio
    async def test_create_email_record(self, email_repository, sample_email_record):
        """Test creating a new email record"""
        mock_session = AsyncMock()
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.create(sample_email_record)
        
        assert result == sample_email_record
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_email_by_id_found(self, email_repository, sample_email_record):
        """Test getting an email record by ID when it exists"""
        mock_session = AsyncMock()
        mock_session.get.return_value = sample_email_record
        
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.get_by_id(sample_email_record.id)
        
        assert result == sample_email_record
        mock_session.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_email_by_id_not_found(self, email_repository):
        """Test getting an email record by ID when it doesn't exist"""
        mock_session = AsyncMock()
        mock_session.get.return_value = None
        
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.get_by_id(uuid4())
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_email_record(self, email_repository, sample_email_record):
        """Test updating an existing email record"""
        mock_session = AsyncMock()
        mock_session.merge.return_value = sample_email_record
        
        self.setup_mock_session(email_repository, mock_session)
        
        # Modify the email
        sample_email_record.subject = "Updated Subject"
        
        result = await email_repository.update(sample_email_record)
        
        assert result == sample_email_record
        assert result.subject == "Updated Subject"
        mock_session.merge.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_email_record_success(self, email_repository, sample_email_record):
        """Test deleting an email record successfully"""
        mock_session = AsyncMock()
        mock_session.get.return_value = sample_email_record
        
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.delete(sample_email_record.id)
        
        assert result is True
        mock_session.get.assert_called_once_with(
            EmailRecordORM, sample_email_record.id
        )
        mock_session.delete.assert_called_once_with(sample_email_record)
    
    @pytest.mark.asyncio
    async def test_delete_email_record_not_found(self, email_repository):
        """Test deleting an email record that doesn't exist"""
        mock_session = AsyncMock()
        mock_session.get.return_value = None
        
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.delete(uuid4())
        
        assert result is False
        mock_session.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_all_emails(self, email_repository, sample_email_record):
        """Test listing all email records"""
        email_list = [sample_email_record]
        
        mock_session = AsyncMock()
        mock_result = MagicMock()  # Use MagicMock instead of AsyncMock
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = email_list
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        self.setup_mock_session(email_repository, mock_session)
        
        result = await email_repository.list_all()
        
        assert result == email_list
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exists_email_record_true(self, email_repository, sample_email_record):
        """Test checking if email record exists - returns True"""
        mock_session = AsyncMock()
        mock_session.get.return_value = sample_email_record
        
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.exists(sample_email_record.id)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_exists_email_record_false(self, email_repository):
        """Test checking if email record exists - returns False"""
        mock_session = AsyncMock()
        mock_session.get.return_value = None
        
        email_repository._db_connection.get_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        email_repository._db_connection.get_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )
        
        result = await email_repository.exists(uuid4())
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_by_message_id(self, email_repository, sample_email_record):
        """Test getting email by message ID"""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_email_record
        mock_session.execute.return_value = mock_result
        
        self.setup_mock_session(email_repository, mock_session)
        
        result = await email_repository.get_by_message_id(sample_email_record.message_id)
        
        assert result == sample_email_record
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_status(self, email_repository, sample_email_record):
        """Test getting emails by status"""
        email_list = [sample_email_record]
        
        # Create a mock result that properly handles scalars().all()
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = email_list
        
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars_result
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        db_connection = email_repository._db_connection
        get_session_mock = db_connection.get_session.return_value
        get_session_mock.__aenter__ = AsyncMock(return_value=mock_session)
        get_session_mock.__aexit__ = AsyncMock(return_value=None)
        
        result = await email_repository.get_by_status(EmailStatus.RECEIVED)
        
        assert result == email_list
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_sender(self, email_repository, sample_email_record):
        """Test getting emails by sender"""
        email_list = [sample_email_record]
        
        # Create a mock result that properly handles scalars().all()
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = email_list
        
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars_result
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        db_connection = email_repository._db_connection
        get_session_mock = db_connection.get_session.return_value
        get_session_mock.__aenter__ = AsyncMock(return_value=mock_session)
        get_session_mock.__aexit__ = AsyncMock(return_value=None)
        
        result = await email_repository.get_by_sender(
            sample_email_record.sender
        )
        
        assert result == email_list
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_date_range(
        self, email_repository, sample_email_record
    ):
        """Test getting emails by date range"""
        email_list = [sample_email_record]
        start_date = datetime(2025, 7, 28, tzinfo=UTC)
        end_date = datetime(2025, 7, 30, tzinfo=UTC)
        
        # Create a mock result that properly handles scalars().all()
        mock_scalars_result = Mock()
        mock_scalars_result.all.return_value = email_list
        
        mock_result = Mock()
        mock_result.scalars.return_value = mock_scalars_result
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        db_connection = email_repository._db_connection
        get_session_mock = db_connection.get_session.return_value
        get_session_mock.__aenter__ = AsyncMock(return_value=mock_session)
        get_session_mock.__aexit__ = AsyncMock(return_value=None)
        
        result = await email_repository.get_by_date_range(start_date, end_date)
        
        assert result == email_list
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_by_status(self, email_repository):
        """Test counting emails by status"""
        expected_count = 5
        
        # Create a mock result that properly handles scalar()
        mock_result = Mock()
        mock_result.scalar.return_value = expected_count
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        db_connection = email_repository._db_connection
        get_session_mock = db_connection.get_session.return_value
        get_session_mock.__aenter__ = AsyncMock(return_value=mock_session)
        get_session_mock.__aexit__ = AsyncMock(return_value=None)
        
        result = await email_repository.count_by_status(EmailStatus.RECEIVED)
        
        assert result == expected_count
        mock_session.execute.assert_called_once()
