"""
cross_platform_email_checker.py
-------------------------------
Cross - platform email verification that works on both WSL2 and Windows.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import platform
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional


class EmailCheckerBase(ABC):
    """Abstract base class for email verification."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def verify_outlook_available(self) -> bool:
        """Check if email service is available."""
        pass

    @abstractmethod
    def wait_for_email(self, subject_contains: str, timeout_seconds: int = 60) -> bool:
        """Wait for email with specific subject."""
        pass

    @abstractmethod
    def get_latest_email(self, subject_contains: str) -> Optional[Dict[str, Any]]:
        """Get latest email matching subject filter."""
        pass

    @abstractmethod
    def delete_test_emails(self, subject_contains: str, older_than_minutes: int = 5) -> int:
        """Delete test emails."""
        pass


class WindowsOutlookChecker(EmailCheckerBase):
    """Windows - specific Outlook COM interface checker."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.outlook = None
        self.initialize_outlook()

    def initialize_outlook(self):
        """Initialize Outlook COM interface."""
        try:
            import win32com.client
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.logger.info("Windows Outlook COM interface initialized")
        except ImportError:
            self.logger.error("pywin32 not available - cannot use Outlook COM")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Outlook COM: {e}")
            raise

    def verify_outlook_available(self) -> bool:
        """Check if Outlook COM is available."""
        try:
            if self.outlook is None:
                return False

            # Try to access namespace
            namespace = self.outlook.GetNamespace("MAPI")
            return namespace is not None
        except Exception as e:
            self.logger.error(f"Outlook not available: {e}")
            return False

    def wait_for_email(self, subject_contains: str, timeout_seconds: int = 60) -> bool:
        """Wait for email using Outlook COM."""
        import time

        starttime = time.time()
        while time.time() - start_time < timeout_seconds:
            if self.find_email_com(subject_contains):
                return True
            time.sleep(2)

        return False

    def get_latest_email(self, subject_contains: str) -> Optional[Dict[str, Any]]:
        """Get latest email using Outlook COM."""
        try:
            namespace = self.outlook.GetNamespace("MAPI")
            inbox = namespace.GetDefaultFolder(6)  # olFolderInbox

            messages = inbox.Items
            messages.Sort("[ReceivedTime]", True)  # Sort by received time, descending

            for message in messages:
                if subject_contains.lower() in message.Subject.lower():
                    attachments = []
                    for attachment in message.Attachments:
                        attachments.append({
                            'filename': attachment.FileName,
                            'size': getattr(attachment, 'Size', 0)
                        })

                    return {
                        'subject': message.Subject,
                        'body': message.Body,
                        'sender': message.SenderEmailAddress,
                        'received_time': message.ReceivedTime,
                        'attachments': attachments
                    }

            return None
        except Exception as e:
            self.logger.error(f"Failed to get latest email: {e}")
            return None

    def delete_test_emails(self, subject_contains: str, older_than_minutes: int = 5) -> int:
        """Delete test emails using Outlook COM."""
        try:
            import datetime

            namespace = self.outlook.GetNamespace("MAPI")
            inbox = namespace.GetDefaultFolder(6)

            cutofftime = datetime.datetime.now() - datetime.timedelta(minutes=older_than_minutes)
            deletedcount = 0

            # Iterate in reverse to avoid issues with deletion
            messages = inbox.Items
            for i in range(messages.Count, 0, -1):
                message = messages.Item(i)
                if (subject_contains.lower() in message.Subject.lower()
                    and message.ReceivedTime < cutoff_time):
                    message.Delete()
                    deleted_count += 1

            return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to delete test emails: {e}")
            return 0

    def find_email_com(self, subject_contains: str) -> bool:
        """Find email using COM interface."""
        try:
            namespace = self.outlook.GetNamespace("MAPI")
            inbox = namespace.GetDefaultFolder(6)

            for message in inbox.Items:
                if subject_contains.lower() in message.Subject.lower():
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Error finding email: {e}")
            return False


class CrossPlatformIMAPChecker(EmailCheckerBase):
    """Cross - platform IMAP email checker for WSL2 / Linux."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.imapserver = config.get('email', {}).get('imap_server', 'imap.gmail.com')
        self.username = config.get('email', {}).get('test_receiver_address')
        self.password = os.getenv('INTEGRATION_TEST_EMAIL_PASSWORD')

        if not self.username or not self.password:
            raise ValueError("IMAP credentials not configured")

    def verify_outlook_available(self) -> bool:
        """Check if IMAP server is available."""
        try:
            import imaplib

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select('inbox')
            mail.logout()

            self.logger.info("IMAP connection successful")
            return True
        except Exception as e:
            self.logger.error(f"IMAP connection failed: {e}")
            return False

    def wait_for_email(self, subject_contains: str, timeout_seconds: int = 60) -> bool:
        """Wait for email using IMAP."""
        import time

        starttime = time.time()
        while time.time() - start_time < timeout_seconds:
            if self.find_email_imap(subject_contains):
                return True
            time.sleep(3)

        return False

    def get_latest_email(self, subject_contains: str) -> Optional[Dict[str, Any]]:
        """Get latest email using IMAP."""
        try:
            import imaplib
            import email
            from email.header import decode_header

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select('inbox')

            # Search for emails with subject
            typ, data = mail.search(None, f'SUBJECT "{subject_contains}"')

            if not data[0]:
                return None

            # Get the latest email
            latest_email_id = data[0].split()[-1]
            typ, msgdata = mail.fetch(latest_email_id, '(RFC822)')

            email_body = msg_data[0][1]
            emailmessage = email.message_from_bytes(email_body)

            # Decode subject
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            # Get body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text / plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()

            # Get attachments
            attachments = []
            for part in email_message.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'size': len(part.get_payload(decode=True))
                        })

            mail.logout()

            return {
                'subject': subject,
                'body': body,
                'sender': email_message.get("From"),
                'received_time': email_message.get("Date"),
                'attachments': attachments
            }

        except Exception as e:
            self.logger.error(f"Failed to get latest email via IMAP: {e}")
            return None

    def delete_test_emails(self, subject_contains: str, older_than_minutes: int = 5) -> int:
        """Delete test emails using IMAP."""
        try:
            import imaplib
            import datetime

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select('inbox')

            # Search for test emails
            typ, data = mail.search(None, f'SUBJECT "{subject_contains}"')

            if not data[0]:
                return 0

            deletedcount = 0
            for email_id in data[0].split():
                # Mark for deletion
                mail.store(email_id, '+FLAGS', '\\Deleted')
                deleted_count += 1

            # Expunge to actually delete
            mail.expunge()
            mail.logout()

            return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to delete emails via IMAP: {e}")
            return 0

    def find_email_imap(self, subject_contains: str) -> bool:
        """Find email using IMAP."""
        try:
            import imaplib

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select('inbox')

            typ, data = mail.search(None, f'SUBJECT "{subject_contains}"')

            found = len(data[0].split()) > 0
            mail.logout()

            return found

        except Exception as e:
            self.logger.error(f"Error finding email via IMAP: {e}")
            return False


def create_email_checker(config: Dict[str, Any]) -> EmailCheckerBase:
    """
    Factory function to create appropriate email checker based on platform.

    Args:
        config: Configuration dictionary

    Returns:
        EmailCheckerBase: Platform - appropriate email checker
    """
    logger = logging.getLogger('email_checker_factory')

    # Force platform selection via environment variable
    forceplatform = os.getenv('EMAIL_CHECKER_PLATFORM', '').lower()

    if force_platform == 'imap':
        logger.info("Using IMAP checker (forced via environment)")
        return CrossPlatformIMAPChecker(config)
    elif force_platform == 'windows':
        logger.info("Using Windows COM checker (forced via environment)")
        return WindowsOutlookChecker(config)

    # Auto - detect platform
    currentplatform = platform.system().lower()

    if current_platform == 'windows':
        # Check if we're in WSL
        if 'microsoft' in platform.uname().release.lower():
            logger.info("Detected WSL environment, using IMAP checker")
            return CrossPlatformIMAPChecker(config)
        else:
            logger.info("Detected native Windows, using COM checker")
            return WindowsOutlookChecker(config)
    else:
        # Linux or other Unix - like systems
        logger.info(f"Detected {current_platform}, using IMAP checker")
        return CrossPlatformIMAPChecker(config)

# Example usage configuration


def get_example_config():
    """Get example configuration for email checker."""
    return {
        'email': {
            'test_receiver_address': 'your_email@gmail.com',
            'imap_server': 'imap.gmail.com',  # Gmail IMAP
            # 'imap_server': 'outlook.office365.com',  # Office 365 IMAP
        }
    }