"""outlook_checker.py
------------------
Outlook email verification and cleanup for integration tests.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import logging
import time
from datetime import datetime, timedelta

import win32com.client


class IntegrationOutlookChecker:
    """Checks and manages emails in Outlook for integration testing.
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('integration_outlook_checker')
        self.testprefix = config.integration_tests.get('test_subject_prefix', 'INTEGRATION_TEST')
        self.outlookaccount = config.email.get('outlook_account')

    def wait_for_email(self, subject: str, timeout_seconds: int = 60) -> Any | None:
        """Wait for email with specific subject to arrive.

        Args:
            subject: Email subject to search for
            timeout_seconds: Maximum time to wait

        Returns:
            Email object if found, None if timeout
        """
        self.logger.info(f"Waiting for email with subject: {subject}")
        starttime = time.time()

        while time.time() - start_time < timeout_seconds:
            try:
                outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
                inbox = self.get_inbox_for_account(outlook)
                messages = inbox.Items
                messages.Sort('[ReceivedTime]', True)  # Most recent first

                # Check last 50 messages (should be sufficient for tests)
                for i, msg in enumerate(messages):
                    if i >= 50:  # Limit search to avoid performance issues
                        break

                    try:
                        msgsubject = getattr(msg, 'Subject', '')
                        if subject in msg_subject:
                            self.logger.info(f"Found email: {msg_subject}")
                            return msg
                    except Exception as e:
                        self.logger.debug(f"Error checking message {i}: {e}")
                        continue

                time.sleep(2)  # Wait before checking again

            except Exception as e:
                self.logger.error(f"Error checking for email: {e}")
                time.sleep(5)

        self.logger.warning(f"Email not found after {timeout_seconds} seconds: {subject}")
        return None

    def delete_test_emails(self, max_age_hours: int = 1) -> int:
        """Delete all test emails (identified by test prefix) from inbox.

        Args:
            max_age_hours: Only delete emails newer than this many hours

        Returns:
            int: Number of emails deleted
        """
        deletedcount = 0
        cutofftime = datetime.now() - timedelta(hours=max_age_hours)

        try:
            outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
            inbox = self.get_inbox_for_account(outlook)
            messages = inbox.Items
            messages.Sort('[ReceivedTime]', True)

            # Build list of messages to delete (to avoid modification during iteration)
            messagesto_delete = []

            for msg in messages:
                try:
                    msgsubject = getattr(msg, 'Subject', '')
                    receivedtime = getattr(msg, 'ReceivedTime', None)

                    if self.test_prefix in msg_subject:
                        if received_time and received_time >= cutoff_time:
                            messages_to_delete.append(msg)
                        elif not received_time:
                            # Delete if we can't determine received time (safer)
                            messages_to_delete.append(msg)

                except Exception as e:
                    self.logger.debug(f"Error checking message for deletion: {e}")
                    continue

            # Delete the messages
            for msg in messages_to_delete:
                try:
                    subject = getattr(msg, 'Subject', 'Unknown')
                    msg.Delete()
                    deleted_count += 1
                    self.logger.info(f"Deleted test email: {subject}")
                except Exception as e:
                    self.logger.error(f"Error deleting message: {e}")

        except Exception as e:
            self.logger.error(f"Error during email cleanup: {e}")

        self.logger.info(f"Deleted {deleted_count} test emails")
        return deleted_count

    def verify_email_received(self, subject: str, timeout_seconds: int = 60) -> bool:
        """Verify that an email with the given subject was received.

        Args:
            subject: Email subject to search for
            timeout_seconds: Maximum time to wait

        Returns:
            bool: True if email was found, False otherwise
        """
        email = self.wait_for_email(subject, timeout_seconds)
        return email is not None

    def get_email_with_attachment(self, subject: str, timeout_seconds: int = 60) -> dict[str, Any] | None:
        """Get email with subject and return attachment info.

        Args:
            subject: Email subject to search for
            timeout_seconds: Maximum time to wait

        Returns:
            Dict with email and attachment info, or None
        """
        email = self.wait_for_email(subject, timeout_seconds)
        if not email:
            return None

        result = {
            'email': email,
            'attachments': []
        }

        try:
            attachments = getattr(email, 'Attachments', None)
            if attachments:
                for i in range(1, attachments.Count + 1):
                    attachment = attachments.Item(i)
                    attinfo = {
                        'filename': getattr(attachment, 'FileName', ''),
                        'size': getattr(attachment, 'Size', 0),
                        'attachment_obj': attachment
                    }
                    result['attachments'].append(att_info)

        except Exception as e:
            self.logger.error(f"Error processing attachments: {e}")

        return result

    def delete_specific_email(self, email) -> bool:
        """Delete a specific email object.

        Args:
            email: Email object to delete

        Returns:
            bool: True if deletion successful
        """
        try:
            subject = getattr(email, 'Subject', 'Unknown')
            email.Delete()
            self.logger.info(f"Deleted specific email: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting specific email: {e}")
            return False

    def get_inbox_for_account(self, outlook_namespace):
        """Get inbox for specific account or default inbox."""
        if not self.outlook_account:
            return outlook_namespace.GetDefaultFolder(6)  # Default inbox

        try:
            session = outlook_namespace.Session
            accounts = getattr(session, 'Accounts', None)

            if accounts:
                for account in accounts:
                    if getattr(account, 'SmtpAddress', '').lower() == self.outlook_account.lower():
                        return account.DeliveryStore.GetDefaultFolder(6)

            self.logger.warning(f"Account {self.outlook_account} not found, using default inbox")

        except Exception as e:
            self.logger.error(f"Error accessing account {self.outlook_account}: {e}")

        return outlook_namespace.GetDefaultFolder(6)