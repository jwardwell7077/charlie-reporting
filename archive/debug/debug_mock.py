import sys
sys.path.insert(0, 'src')

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

def test_mock_setup():
    # Replicate the mock setup from the test
    mock_attachment = Mock()
    mock_attachment.FileName = 'IB_Calls.csv'
    mock_attachment.SaveAsFile = Mock()
    
    mock_attachments = Mock()
    mock_attachments.Count = 1
    mock_attachments.Item.return_value = mock_attachment
    
    msg_recent = Mock()
    msg_recent.SenderEmailAddress = 'reports@example.com'
    msg_recent.Subject = 'Daily Report Data'
    msg_recent.ReceivedTime = datetime(2025, 7, 27, 14, 30, 0)
    msg_recent.Attachments = mock_attachments
    msg_recent.SenderName = 'Report System'
    
    # Test the mock
    print(f"Attachments Count: {msg_recent.Attachments.Count}")
    print(f"Has Attachments: {hasattr(msg_recent, 'Attachments')}")
    print(f"Attachments object: {msg_recent.Attachments}")
    print(f"Has Count attr: {hasattr(msg_recent.Attachments, 'Count')}")
    
    # Test the Item call
    attachment = msg_recent.Attachments.Item(1)
    print(f"Retrieved attachment: {attachment}")
    print(f"Attachment filename: {attachment.FileName}")

if __name__ == "__main__":
    test_mock_setup()
