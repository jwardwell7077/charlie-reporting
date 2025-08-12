import sys
sys.path.insert(0, 'src')

from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import os

# Mock win32com before importing email_fetcher
with patch.dict('sys.modules', {'win32com': Mock(), 'win32com.client': Mock()}):
    from email_fetcher import EmailFetcher


def debug_fetch_recent():
    """Debug the fetch_recent method step by step"""
    print("=== Debug fetch_recent ===")

    # Create config

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
            }

    config = DummyConfig()

    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Temp directory: {temp_dir}")

        # Create fetcher
        fetcher = EmailFetcher(config, save_dir=temp_dir)

        # Create mock message
        current_time = datetime(2025, 7, 27, 15, 0, 0)
        msg_recent = Mock()
        msg_recent.SenderEmailAddress = 'reports@example.com'
        msg_recent.Subject = 'Daily Report Data'
        msg_recent.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
        msg_recent.SenderName = 'Report System'

        # Create mock attachment
        mockattachment = Mock()
        mock_attachment.FileName = 'IB_Calls.csv'
        mock_attachment.SaveAsFile = Mock()

        mock_attachments = Mock()
        mock_attachments.Count = 1
        mock_attachments.Item.returnvalue = mock_attachment
        msg_recent.Attachments = mock_attachments

        # Mock Outlook
        with patch('win32com.client.Dispatch') as mock_dispatch:
            mock_outlook = Mock()
            mock_namespace = Mock()
            mock_inbox = Mock()
            mock_messages = Mock()

            mock_dispatch.return_value.GetNamespace.returnvalue = mock_namespace
            mock_namespace.GetDefaultFolder.returnvalue = mock_inbox
            mock_inbox.Items = mock_messages
            mock_messages.Sort = Mock()
            mock_messages.iter__ = Mock(return_value=iter([msg_recent]))

            # Mock datetime.now
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.returnvalue = current_time
                mock_datetime.sideeffect = lambda *args, **kw: datetime(*args, **kw)

                # Call fetch_recent
                print("Calling fetch_recent...")
                fetcher.fetch_recent(hours_back=1)

                # Check results
                print(f"SaveAsFile called: {mock_attachment.SaveAsFile.called}")
                if mock_attachment.SaveAsFile.called:
                    print(f"SaveAsFile call args: {mock_attachment.SaveAsFile.call_args}")

                # Check if file exists in temp directory
                files = os.listdir(temp_dir)
                print(f"Files in temp directory: {files}")


if __name__ == "__main__":
    debug_fetch_recent()