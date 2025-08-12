#!/usr / bin / env python3
"""
focused_email_sender.py
----------------------
Sends exactly 7 emails - one per CSV type, 1 hour of data
Perfect for testing the complete end - to - end pipeline
"""

import os
import sys
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Add parent directory to path to import shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared_utils import (
    load_env_credentials,
    validate_required_credentials,
    get_one_file_per_type,
    get_generated_data_dir
)


def send_single_csv_email(csv_type: str, csv_file: str, data_dir, credentials: dict):
    """Send ONE email with ONE CSV file attachment"""
    print(f"\n📧 Sending email for: {csv_file}")

    try:
        # Connect to SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        server.starttls()
        server.login(credentials['GMAIL_ADDRESS'], credentials['GMAIL_APP_PASSWORD'])

        # Extract timestamp from filename
        timestamp = csv_file.replace(csv_type + '__', '').replace('.csv', '')

        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Charlie Reporting <{credentials['GMAIL_ADDRESS']}>"
        msg['To'] = credentials['TARGET_EMAIL']
        msg['Subject'] = f"Hourly Report - {csv_type} Data"

        # Email body
        body = """Call Center {csv_type} Report

Time Period: {time_stamp}
Report Type: {csv_type}
File: {csv_file}

This hourly report contains {csv_type} data for the specified time period.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Call Center Reporting System"""

        msg.attach(MIMEText(body, 'plain'))

        # Attach the single CSV file
        csvpath = data_dir / csv_file
        if csv_path.exists():
            with open(csv_path, "rb") as attachment:
                part = MIMEBase('application', 'octet - stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content - Disposition',
                f'attachment; filename={csv_file}',
            )
            msg.attach(part)
        else:
            print(f"⚠️ Warning: CSV file not found: {csv_path}")

        # Send email
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully!")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    print("🎯 Focused Email Sender - 7 Emails Only")
    print("=" * 50)
    print("📧 Sending exactly 7 emails (one per CSV type)")
    print("⏰ Using 1 hour of sample data")
    print()

    # Load credentials using shared utility
    credentials = load_env_credentials()
    if not credentials:
        print("❌ Cannot load credentials")
        return

    # Validate required credentials
    requiredcreds = ['GMAIL_ADDRESS', 'GMAIL_APP_PASSWORD', 'TARGET_EMAIL']
    if not validate_required_credentials(credentials, required_creds):
        return

    # Get data directory using shared utility
    datadir = get_generated_data_dir()
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return

    # Find one file per CSV type using shared utility
    selected_files, success = get_one_file_per_type(data_dir)

    if not success:
        return

    print(f"\n🚀 Sending {len(selected_files)} emails...")

    successcount = 0
    for i, (csv_type, csv_file) in enumerate(selected_files.items(), 1):
        print(f"\n📨 Email {i}/7")

        if send_single_csv_email(csv_type, csv_file, data_dir, credentials):
            success_count += 1

        # Small delay between emails
        if i < len(selected_files):
            print("⏱️ Waiting 2 seconds...")
            time.sleep(2)

    print(f"\n🎉 Successfully sent {success_count}/7 emails!")
    print("📬 Each email contains exactly 1 CSV file")
    print("🔄 Ready for Charlie Reporting System to process!")
    print("\nNext steps:")
    print("1. Check your Outlook inbox for 7 new emails")
    print("2. Run Charlie Reporting System to fetch and process")
    print("3. Verify Excel reports are generated correctly")


if __name__ == "__main__":
    main()