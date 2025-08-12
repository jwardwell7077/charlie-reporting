"""
email_manager.py
----------------
SMTP email management for integration tests.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import smtplib
import os
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging


class IntegrationEmailManager:
    """
    Manages sending test emails via SMTP for integration testing.
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('integration_email_manager')
        self.smtpconfig = config.smtp
        self.testprefix = config.integration_tests.get('test_subject_prefix', 'INTEGRATION_TEST')

        # Get credentials from environment
        self.senderemail = os.getenv('GMAIL_ADDRESS', self.smtp_config.get('sender_email'))
        self.senderpassword = os.getenv('GMAIL_PASSWORD')
        self.targetemail = os.getenv('TARGET_EMAIL', self.smtp_config.get('target_email'))

        if not self.sender_password:
            raise ValueError("GMAIL_PASSWORD environment variable is required for integration tests")

    def generate_test_identifier(self) -> str:
        """Generate unique test identifier for email subjects."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uniqueid = str(uuid.uuid4())[:8]
        return f"{self.test_prefix}_{timestamp}_{unique_id}"

    def send_simple_email(self, subject_suffix: str = "Simple Test") -> str:
        """
        Send a simple text email for testing.

        Returns:
            str: The full subject line of the sent email
        """
        testid = self.generate_test_identifier()
        subject = f"{test_id}_{subject_suffix}"

        msg = MIMEText("""
This is a test email from the Charlie Reporting Integration Test Suite.

Test ID: {test_id}
Sent at: {datetime.now().isoformat()}
Purpose: Simple email send / receive test

This email should be automatically deleted by the test suite.
If you see this email, please check the integration test logs.
        """.strip())

        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.target_email

        self.send_email(msg)
        self.logger.info(f"Sent simple test email: {subject}")
        return subject

    def send_email_with_csv_attachment(self, csv_file_path: str, subject_suffix: str = "CSV Test") -> str:
        """
        Send email with CSV attachment for testing.

        Args:
            csv_file_path: Path to CSV file to attach
            subject_suffix: Additional text for subject

        Returns:
            str: The full subject line of the sent email
        """
        testid = self.generate_test_identifier()
        subject = f"{test_id}_{subject_suffix}"

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.target_email

        # Email body
        body = """
This is a test email with CSV attachment from the Charlie Reporting Integration Test Suite.

Test ID: {test_id}
Sent at: {datetime.now().isoformat()}
Purpose: Email attachment processing test
Attachment: {os.path.basename(csv_file_path)}

This email should be automatically deleted by the test suite.
        """.strip()

        msg.attach(MIMEText(body, 'plain'))

        # Attach CSV file
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet - stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content - Disposition',
                    f'attachment; filename= {os.path.basename(csv_file_path)}'
                )
                msg.attach(part)
        else:
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

        self.send_email(msg)
        self.logger.info(f"Sent email with CSV attachment: {subject}")
        return subject

    def send_email(self, msg):
        """Send email via SMTP."""
        try:
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                self.logger.debug("Email sent successfully via SMTP")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise

    def test_smtp_connection(self) -> bool:
        """
        Test SMTP connection and authentication.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                self.logger.info("SMTP connection test successful")
                return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False