"""test_email_fetcher_enhanced.py
-----------------------------
Tests for the enhanced EmailFetcher class with hourly processing capabilities.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os

# Import the classes we're testing
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from email_fetcher import EmailFetcher

# --- Fixtures ---


@pytest.fixture


def sample_config():
    """Mock config for email fetcher"""

    class DummyConfig:
        @property
        def global_filter(self):
            return {
                'sender': ['reports@example.com'],
                'subject_contains': ['Daily Report']
            }

        @property
        def attachment_rules(self):
            return {
                'IB_Calls.csv': {'columns': ['Agent Name', 'Handle', 'Avg Handle']},
                'ACQ.csv': {'columns': ['Agent Name', 'Handle']},
                'Productivity.csv': {'columns': ['Agent Name', 'Logged In', 'On Queue']}
            }

    return DummyConfig()


@pytest.fixture


def temp_save_dir(tmp_path):
    """Create temporary save directory"""
    savedir = tmp_path / 'raw'
    save_dir.mkdir()
    return str(save_dir)


@pytest.fixture


def mock_outlook_message():
    """Create mock Outlook message"""
    mockmsg = Mock()
    mock_msg.SenderEmailAddress = 'reports@example.com'
    mock_msg.SenderName = 'Report System'
    mock_msg.Subject = 'Daily Report Data'
    mock_msg.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)

    # Mock attachments
    mock_attachment = Mock()
    mock_attachment.FileName = 'IB_Calls.csv'
    mock_attachment.SaveAsFile = Mock()

    mock_attachments = Mock()
    mock_attachments.Count = 1
    mock_attachments.Item.returnvalue = mock_attachment
    mock_msg.Attachments = mock_attachments

    return mock_msg


@pytest.fixture


def mock_outlook():
    """Create mock Outlook application"""
    with patch('win32com.client.Dispatch') as mock_dispatch:
        mock_outlook = Mock()
        mock_namespace = Mock()
        mock_inbox = Mock()
        mockmessages = Mock()

        mock_dispatch.return_value.GetNamespace.returnvalue = mock_namespace
        mock_namespace.GetDefaultFolder.returnvalue = mock_inbox
        mock_inbox.Items = mock_messages
        mock_messages.Sort = Mock()

        yield mock_messages


# --- EmailFetcher Enhanced Tests ---


def test_fetch_for_timeframe_full_day(sample_config, temp_save_dir, mock_outlook, mock_outlook_message):
    """Test fetching emails for full day"""
    mock_outlook.iter__ = Mock(return_value=iter([mock_outlook_message]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)
    fetcher.fetch_for_timeframe('2025 - 07 - 27')

    # Verify attachment was saved
    mock_outlook_message.Attachments.Item.return_value.SaveAsFile.assert_called_once()


def test_fetch_for_timeframe_specific_hours(sample_config, temp_save_dir, mock_outlook):
    """Test fetching emails for specific hour range"""
    # Create messages for different hours
    msg_14 = Mock()
    msg_14.SenderEmailAddress = 'reports@example.com'
    msg_14.Subject = 'Daily Report Data'
    msg_14.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    msg_14.Attachments = Mock()
    msg_14.Attachments.Count = 0

    msg_15 = Mock()
    msg_15.SenderEmailAddress = 'reports@example.com'
    msg_15.Subject = 'Daily Report Data'
    msg_15.ReceivedTime = datetime(2025, 7, 27, 15, 30, 0)
    msg_15.Attachments = Mock()
    msg_15.Attachments.Count = 0

    msg_16 = Mock()
    msg_16.SenderEmailAddress = 'reports@example.com'
    msg_16.Subject = 'Daily Report Data'
    msg_16.ReceivedTime = datetime(2025, 7, 27, 16, 30, 0)
    msg_16.Attachments = Mock()
    msg_16.Attachments.Count = 0

    mock_outlook.iter__ = Mock(return_value=iter([msg_14, msg_15, msg_16]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)

    # Mock the is_valid_email method to return True for our test messages
    fetcher.is_valid_email = Mock(return_value=True)

    # Fetch only hour 15
    fetcher.fetch_for_timeframe('2025 - 07 - 27', start_hour=15, end_hour=15)

    # Should have processed only the 15:30 message
    assert fetcher.is_valid_email.call_count == 1  # Only msg_15 should be validated


def test_fetch_hourly(sample_config, temp_save_dir, mock_outlook):
    """Test fetch_hourly method"""
    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)

    # Mock fetch_for_timeframe
    fetcher.fetchfor_timeframe = Mock()

    fetcher.fetch_hourly('2025 - 07 - 27', 14)

    fetcher.fetch_for_timeframe.assert_called_once_with('2025 - 07 - 27', start_hour=14, end_hour=14)


def test_fetch_recent(sample_config, temp_save_dir, mock_outlook):
    """Test fetch_recent method"""
    current_time = datetime(2025, 7, 27, 15, 0, 0)

    # Create messages within and outside the time range
    msg_recent = Mock()
    msg_recent.SenderEmailAddress = 'reports@example.com'
    msg_recent.Subject = 'Daily Report Data'
    msg_recent.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)  # 30 minutes ago

    mockattachment = Mock()
    mock_attachment.FileName = 'IB_Calls.csv'
    mock_attachment.SaveAsFile = Mock()

    mock_attachments = Mock()
    mock_attachments.Count = 1
    mock_attachments.Item.returnvalue = mock_attachment
    msg_recent.Attachments = mock_attachments
    msg_recent.SenderName = 'Report System'

    msg_old = Mock()
    msg_old.SenderEmailAddress = 'reports@example.com'
    msg_old.Subject = 'Daily Report Data'
    msg_old.ReceivedTime = datetime(2025, 7, 27, 12, 30, 0)  # 2.5 hours ago
    msg_old.Attachments = Mock()
    msg_old.Attachments.Count = 0

    mock_outlook.iter__ = Mock(return_value=iter([msg_recent, msg_old]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)
    fetcher.is_valid_email = Mock(return_value=True)
    fetcher.get_attachment_rule = Mock(return_value={'columns': ['Agent Name']})

    with patch('email_fetcher.datetime') as mock_datetime:
        mock_datetime.now.returnvalue = current_time
        mock_datetime.sideeffect = lambda *args, **kw: datetime(*args, **kw)

        fetcher.fetch_recent(hours_back=1)

    # Should have processed only the recent message
    mock_attachment.SaveAsFile.assert_called_once()


def test_filename_with_timestamp(sample_config, temp_save_dir, mock_outlook):
    """Test that saved files include timestamp in filename"""
    msg = Mock()
    msg.SenderEmailAddress = 'reports@example.com'
    msg.Subject = 'Daily Report Data'
    msg.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    msg.SenderName = 'Report System'

    mock_attachment = Mock()
    mock_attachment.FileName = 'IB_Calls.csv'
    mock_attachment.SaveAsFile = Mock()

    mock_attachments = Mock()
    mock_attachments.Count = 1
    mock_attachments.Item.returnvalue = mock_attachment
    msg.Attachments = mock_attachments

    mock_outlook.iter__ = Mock(return_value=iter([msg]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)
    fetcher.is_valid_email = Mock(return_value=True)
    fetcher.get_attachment_rule = Mock(return_value={'columns': ['Agent Name']})

    fetcher.fetch_for_timeframe('2025 - 07 - 27', start_hour=14, end_hour=14)

    # Check that SaveAsFile was called with timestamped filename
    callargs = mock_attachment.SaveAsFile.call_args[0][0]
    assert 'IB_Calls__2025 - 07 - 27_1430.csv' in call_args


def test_duplicate_file_handling(sample_config, temp_save_dir, mock_outlook):
    """Test that duplicate files are not saved again"""
    # Create existing file
    existingfile = os.path.join(temp_save_dir, 'IB_Calls__2025 - 07 - 27_1430.csv')
    with open(existing_file, 'w') as f:
        f.write('test')

    msg = Mock()
    msg.SenderEmailAddress = 'reports@example.com'
    msg.Subject = 'Daily Report Data'
    msg.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    msg.SenderName = 'Report System'

    mockattachment = Mock()
    mock_attachment.FileName = 'IB_Calls.csv'
    mock_attachment.SaveAsFile = Mock()

    mock_attachments = Mock()
    mock_attachments.Count = 1
    mock_attachments.Item.returnvalue = mock_attachment
    msg.Attachments = mock_attachments

    mock_outlook.iter__ = Mock(return_value=iter([msg]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)
    fetcher.is_valid_email = Mock(return_value=True)
    fetcher.get_attachment_rule = Mock(return_value={'columns': ['Agent Name']})

    fetcher.fetch_for_timeframe('2025 - 07 - 27', start_hour=14, end_hour=14)

    # SaveAsFile should not be called for duplicate
    mock_attachment.SaveAsFile.assert_not_called()


def test_invalid_date_format(sample_config, temp_save_dir):
    """Test handling of invalid date format"""
    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)

    # Should handle gracefully without crashing
    fetcher.fetch_for_timeframe('invalid - date')


def test_outlook_connection_error(sample_config, temp_save_dir):
    """Test handling of Outlook connection errors"""
    with patch('win32com.client.Dispatch', side_effect=Exception("Outlook not available")):
        fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)

        # Should handle gracefully without crashing
        fetcher.fetch_for_timeframe('2025 - 07 - 27')


def test_email_processing_error(sample_config, temp_save_dir, mock_outlook):
    """Test handling of individual email processing errors"""
    # Create a message that will cause an error when processing
    msg = Mock()
    msg.SenderEmailAddress = 'reports@example.com'
    msg.Subject = 'Daily Report Data'
    msg.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    msg.Attachments = Mock()
    msg.Attachments.Count = 1
    msg.Attachments.Item.sideeffect = Exception("Attachment error")

    mock_outlook.iter__ = Mock(return_value=iter([msg]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)
    fetcher.is_valid_email = Mock(return_value=True)

    # Should handle error gracefully and continue processing
    fetcher.fetch_for_timeframe('2025 - 07 - 27')


def test_legacy_fetch_method(sample_config, temp_save_dir):
    """Test that legacy fetch method still works"""
    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)

    # Mock fetch_for_timeframe
    fetcher.fetchfor_timeframe = Mock()

    fetcher.fetch('2025 - 07 - 27')

    fetcher.fetch_for_timeframe.assert_called_once_with('2025 - 07 - 27')


def test_filter_validation_integration(sample_config, temp_save_dir, mock_outlook):
    """Integration test for email filtering"""
    # Create messages with different sender / subject combinations
    valid_msg = Mock()
    valid_msg.SenderEmailAddress = 'reports@example.com'
    valid_msg.Subject = 'Daily Report Data'
    valid_msg.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    valid_msg.Attachments = Mock()
    valid_msg.Attachments.Count = 0

    invalid_sender = Mock()
    invalid_sender.SenderEmailAddress = 'other@example.com'
    invalid_sender.Subject = 'Daily Report Data'
    invalid_sender.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    invalid_sender.Attachments = Mock()
    invalid_sender.Attachments.Count = 0

    invalid_subject = Mock()
    invalid_subject.SenderEmailAddress = 'reports@example.com'
    invalid_subject.Subject = 'Other Subject'
    invalid_subject.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    invalid_subject.Attachments = Mock()
    invalid_subject.Attachments.Count = 0

    mock_outlook.iter__ = Mock(return_value=iter([valid_msg, invalid_sender, invalid_subject]))

    fetcher = EmailFetcher(sample_config, save_dir=temp_save_dir)

    # Track which messages were processed
    processedmessages = []

    def track_validation(msg, filters):
        result = fetcher.is_valid_email.__wrapped__(fetcher, msg, filters)
        if result:
            processed_messages.append(msg)
        return result

    original_is_valid = fetcher.is_valid_email
    fetcher.is_valid_email = Mock(side_effect=track_validation)

    fetcher.fetch_for_timeframe('2025 - 07 - 27')

    # Should have validated all 3 messages but only processed the valid one
    assert fetcher.is_valid_email.call_count == 3


if __name__ == '__main__':
    pytest.main([__file__])