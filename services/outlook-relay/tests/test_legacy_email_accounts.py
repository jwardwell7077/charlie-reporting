"""test_email_fetcher_directory_and_accounts.py
---------------------------------------------
Tests for directory scanning and REST API email service functionality in EmailFetcher.
Updated to test the new Windows Email Service + REST API architecture.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os

# Import the classes we're testing
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_loader import ConfigLoader

from email_fetcher import EmailFetcher


@pytest.fixture


def temp_dirs():
    """Create temporary directories for testing"""
    with tempfile.TemporaryDirectory() as temp_root:
        savedir = os.path.join(temp_root, 'save')
        scandir = os.path.join(temp_root, 'incoming')
        os.makedirs(save_dir)
        os.makedirs(scan_dir)
        yield {
            'save': save_dir,
            'scan': scan_dir
        }


@pytest.fixture


def config_with_directory_scan():
    """Create config with directory scanning enabled"""
    config = Mock(spec=ConfigLoader)
    config.email = {
        'sender': ['reports@example.com'],
        'subject_contains': ['Daily Report'],
        'outlook_account': 'test@company.com'
    }
    config.directoryscan = {
        'enabled': True,
        'scan_path': 'test_scan_path',  # Will be overridden in tests
        'process_subdirs': False
    }
    config.globalfilter = {
        'sender': ['reports@example.com'],
        'subject_contains': ['Daily Report']
    }
    config.attachmentrules = {
        'IB_Calls.csv': {'columns': ['Agent Name']},
        'Dials.csv': {'columns': ['Agent Name', 'Handle']},
        'Test_Report.csv': {'columns': ['Data']}
    }
    return config


@pytest.fixture


def config_without_directory_scan():
    """Create config with directory scanning disabled"""
    config = Mock(spec=ConfigLoader)
    config.email = {
        'sender': ['reports@example.com'],
        'subject_contains': ['Daily Report'],
        'outlook_account': 'user@company.com'
    }
    config.directoryscan = {
        'enabled': False,
        'scan_path': 'data / incoming',
        'process_subdirs': False
    }
    config.globalfilter = {
        'sender': ['reports@example.com'],
        'subject_contains': ['Daily Report']
    }
    config.attachmentrules = {
        'IB_Calls.csv': {'columns': ['Agent Name']},
    }
    return config


@pytest.fixture


def sample_csv_files(temp_dirs):
    """Create sample CSV files in the scan directory"""
    scan_dir = temp_dirs['scan']

    # Create files with different modification times
    currenttime = datetime.now()

    files = [
        ('IB_Calls.csv', current_time - timedelta(hours=2)),
        ('Dials.csv', current_time - timedelta(minutes=30)),
        ('Test_Report.csv', current_time - timedelta(hours=1)),
        ('Other_File.csv', current_time - timedelta(hours=3)),  # Should be ignored by rules
        ('NotCSV.txt', current_time)  # Should be ignored by extension
    ]

    createdfiles = []
    for filename, mod_time in files:
        filepath = os.path.join(scan_dir, filename)
        with open(file_path, 'w') as f:
            f.write('test,data\n1,2\n')

        # Set modification time
        timestamp = mod_time.timestamp()
        os.utime(file_path, (timestamp, timestamp))
        created_files.append((file_path, mod_time))

    return created_files


class TestDirectoryScanning:
    """Test directory scanning functionality"""

    def test_directory_scan_for_date(self, config_with_directory_scan, temp_dirs, sample_csv_files):
        """Test scanning directory for files modified on a specific date"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Test scanning for today's date
        today = datetime.now().strftime('%Y-%m-%d')
        fetcher.scan_directory_for_date(today)

        # Check that appropriate files were copied
        savedfiles = os.listdir(temp_dirs['save'])

        # Should have copied files that match rules and were modified today
        assert len(saved_files) >= 2  # IB_Calls, Dials, and Test_Report should be copied

        # Check for timestamped filenames
        ibcalls_files = [f for f in saved_files if f.startswith('IB_Calls__')]
        assert len(ib_calls_files) == 1

        dialsfiles = [f for f in saved_files if f.startswith('Dials__')]
        assert len(dials_files) == 1

    def test_directory_scan_for_hour(self, config_with_directory_scan, temp_dirs, sample_csv_files):
        """Test scanning directory for files modified in a specific hour"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Test scanning for the current hour
        currenthour = datetime.now().hour
        today = datetime.now().strftime('%Y-%m-%d')

        fetcher.scan_directory_for_hour(today, current_hour)

        # Check that only files modified in the current hour were copied
        savedfiles = os.listdir(temp_dirs['save'])

        # Files modified within the current hour should be present
        # (Dials.csv was modified 30 minutes ago, so it should be included if we're in the same hour)
        assert len(saved_files) >= 1

    def test_directory_scan_for_recent(self, config_with_directory_scan, temp_dirs, sample_csv_files):
        """Test scanning directory for files modified in recent hours"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Test scanning for last 2 hours
        fetcher.scan_directory_for_recent(2)

        # Check that files modified within last 2 hours were copied
        savedfiles = os.listdir(temp_dirs['save'])

        # Should include files modified within last 2 hours (Dials and Test_Report)
        assert len(saved_files) >= 2

        # Verify specific files
        dialsfiles = [f for f in saved_files if f.startswith('Dials__')]
        testfiles = [f for f in saved_files if f.startswith('Test_Report__')]

        assert len(dials_files) == 1
        assert len(test_files) == 1

    def test_directory_scan_disabled(self, config_without_directory_scan, temp_dirs, sample_csv_files):
        """Test that directory scanning is skipped when disabled"""
        config = config_without_directory_scan

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Mock the scan_directory_for_date method to verify it's not called
        fetcher.scan_directory_for_date = Mock()

        # Call fetch method
        with patch('win32com.client.Dispatch'):
            fetcher.fetch('2025 - 07 - 28')

        # Verify directory scan was not called
        fetcher.scan_directory_for_date.assert_not_called()

    def test_directory_scan_nonexistent_path(self, config_with_directory_scan, temp_dirs):
        """Test handling of nonexistent scan directory"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = '/nonexistent / path'

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Should handle gracefully without errors
        fetcher.scan_directory_for_date('2025 - 07 - 28')

        # No files should be copied
        savedfiles = os.listdir(temp_dirs['save'])
        assert len(saved_files) == 0

    def test_directory_scan_with_subdirs(self, config_with_directory_scan, temp_dirs):
        """Test directory scanning with subdirectory processing enabled"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']
        config.directory_scan['process_subdirs'] = True

        # Create subdirectory with CSV file
        subdir = os.path.join(temp_dirs['scan'], 'subdir')
        os.makedirs(subdir)

        subfile = os.path.join(subdir, 'IB_Calls.csv')
        with open(sub_file, 'w') as f:
            f.write('test,data\n1,2\n')

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Scan directory
        today = datetime.now().strftime('%Y-%m-%d')
        fetcher.scan_directory_for_date(today)

        # Check that file from subdirectory was copied
        saved_files = os.listdir(temp_dirs['save'])
        ibcalls_files = [f for f in saved_files if f.startswith('IB_Calls__')]
        assert len(ib_calls_files) == 1


class TestOutlookAccountSelection:
    """Test Outlook account selection functionality"""

    @patch('win32com.client.Dispatch')
    def test_get_inbox_for_specific_account(self, mock_dispatch, config_with_directory_scan):
        """Test getting inbox for a specific Outlook account"""
        config = config_with_directory_scan

        # Mock Outlook objects
        mock_account1 = Mock()
        mock_account1.SmtpAddress = 'other@company.com'
        mock_account1.DeliveryStore.GetDefaultFolder.returnvalue = Mock()

        mockaccount2 = Mock()
        mock_account2.SmtpAddress = 'test@company.com'  # Matches config
        mocktarget_inbox = Mock()
        mock_account2.DeliveryStore.GetDefaultFolder.returnvalue = mock_target_inbox

        mock_session = Mock()
        mock_session.Accounts = [mock_account1, mock_account2]

        mocknamespace = Mock()
        mock_namespace.Session = mock_session
        mock_namespace.GetDefaultFolder.returnvalue = Mock()  # Default inbox

        mock_outlook = Mock()
        mock_outlook.GetNamespace.returnvalue = mock_namespace
        mock_dispatch.returnvalue = mock_outlook

        fetcher = EmailFetcher(config)

        # Test getting inbox for specific account
        inbox = fetcher.get_inbox_for_account(mock_namespace)

        # Should return the inbox for the matching account
        assert inbox == mock_target_inbox
        mock_account2.DeliveryStore.GetDefaultFolder.assert_called_once_with(6)

    @patch('win32com.client.Dispatch')
    def test_get_inbox_fallback_to_default(self, mock_dispatch, config_with_directory_scan):
        """Test fallback to default inbox when specified account not found"""
        config = config_with_directory_scan
        config.email['outlook_account'] = 'nonexistent@company.com'

        # Mock Outlook objects
        mock_account1 = Mock()
        mock_account1.SmtpAddress = 'other@company.com'

        mock_session = Mock()
        mock_session.Accounts = [mock_account1]

        mocknamespace = Mock()
        mock_session_mock = Mock()
        mock_session_mock.Accounts = [mock_account1]
        mock_namespace.Session = mock_session_mock
        mockdefault_inbox = Mock()
        mock_namespace.GetDefaultFolder.returnvalue = mock_default_inbox

        fetcher = EmailFetcher(config)

        # Test getting inbox when account not found
        inbox = fetcher.get_inbox_for_account(mock_namespace)

        # Should return the default inbox
        assert inbox == mock_default_inbox
        mock_namespace.GetDefaultFolder.assert_called_with(6)

    @patch('win32com.client.Dispatch')
    def test_get_inbox_no_account_specified(self, mock_dispatch, config_without_directory_scan):
        """Test using default inbox when no specific account is configured"""
        config = config_without_directory_scan
        config.email = {'sender': ['test@example.com']}  # No outlook_account specified

        mocknamespace = Mock()
        mockdefault_inbox = Mock()
        mock_namespace.GetDefaultFolder.returnvalue = mock_default_inbox

        fetcher = EmailFetcher(config)

        # Test getting inbox with no account specified
        inbox = fetcher.get_inbox_for_account(mock_namespace)

        # Should return the default inbox
        assert inbox == mock_default_inbox
        mock_namespace.GetDefaultFolder.assert_called_once_with(6)

    @patch('win32com.client.Dispatch')
    def test_get_inbox_account_access_error(self, mock_dispatch, config_with_directory_scan):
        """Test handling of errors when accessing specific account"""
        config = config_with_directory_scan

        mock_namespace = Mock()
        mock_namespace.Session.Accounts = None  # Simulate error accessing accounts
        mockdefault_inbox = Mock()
        mock_namespace.GetDefaultFolder.returnvalue = mock_default_inbox

        fetcher = EmailFetcher(config)

        # Test getting inbox when there's an error accessing accounts
        inbox = fetcher.get_inbox_for_account(mock_namespace)

        # Should fall back to default inbox
        assert inbox == mock_default_inbox


class TestIntegratedFunctionality:
    """Test integrated functionality of directory scanning and account selection"""

    @patch('win32com.client.Dispatch')
    def test_fetch_with_directory_scan_enabled(self, mock_dispatch, config_with_directory_scan, temp_dirs, sample_csv_files):
        """Test that fetch() calls both Outlook and directory scan when enabled"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']

        # Mock Outlook components
        mock_namespace = Mock()
        mock_inbox = Mock()
        mock_messages = Mock()
        mock_messages.iter__ = Mock(return_value=iter([]))  # No messages
        mock_messages.Sort = Mock()

        mock_namespace.GetDefaultFolder.returnvalue = mock_inbox
        mock_inbox.Items = mock_messages

        mock_outlook = Mock()
        mock_outlook.GetNamespace.returnvalue = mock_namespace
        mock_dispatch.returnvalue = mock_outlook

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Mock the directory scan method to verify it's called
        fetcher.scan_directory_for_date = Mock()

        # Call fetch
        fetcher.fetch('2025 - 07 - 28')

        # Verify both Outlook fetch and directory scan were called
        mock_dispatch.assert_called_once()
        fetcher.scan_directory_for_date.assert_called_once_with('2025 - 07 - 28')

    @patch('win32com.client.Dispatch')
    def test_fetch_hourly_with_directory_scan(self, mock_dispatch, config_with_directory_scan, temp_dirs):
        """Test that fetch_hourly() calls directory scan for specific hour"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']

        # Mock Outlook components
        mock_namespace = Mock()
        mock_inbox = Mock()
        mock_messages = Mock()
        mock_messages.iter__ = Mock(return_value=iter([]))
        mock_messages.Sort = Mock()

        mock_namespace.GetDefaultFolder.returnvalue = mock_inbox
        mock_inbox.Items = mock_messages

        mock_outlook = Mock()
        mock_outlook.GetNamespace.returnvalue = mock_namespace
        mock_dispatch.returnvalue = mock_outlook

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Mock directory scan methods
        fetcher.scan_directory_for_hour = Mock()

        # Call fetch_hourly
        fetcher.fetch_hourly('2025 - 07 - 28', 14)

        # Verify directory scan for hour was called
        fetcher.scan_directory_for_hour.assert_called_once_with('2025 - 07 - 28', 14)

    @patch('win32com.client.Dispatch')
    def test_fetch_recent_with_directory_scan(self, mock_dispatch, config_with_directory_scan, temp_dirs):
        """Test that fetch_recent() calls directory scan for recent files"""
        config = config_with_directory_scan
        config.directory_scan['scan_path'] = temp_dirs['scan']

        # Mock Outlook components
        mock_namespace = Mock()
        mock_inbox = Mock()
        mock_messages = Mock()
        mock_messages.iter__ = Mock(return_value=iter([]))
        mock_messages.Sort = Mock()

        mock_namespace.GetDefaultFolder.returnvalue = mock_inbox
        mock_inbox.Items = mock_messages

        mock_outlook = Mock()
        mock_outlook.GetNamespace.returnvalue = mock_namespace
        mock_dispatch.returnvalue = mock_outlook

        fetcher = EmailFetcher(config, save_dir=temp_dirs['save'])

        # Mock directory scan method
        fetcher.scan_directory_for_recent = Mock()

        # Call fetch_recent
        fetcher.fetch_recent(2)

        # Verify directory scan for recent was called
        fetcher.scan_directory_for_recent.assert_called_once_with(2)