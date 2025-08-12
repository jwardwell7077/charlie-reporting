#!/usr / bin / env python3
"""
csv_email_sender.py
------------------
Direct CSV email sender - sends all 7 CSV types immediately
"""

import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


def load_env_credentials():
    """Load credentials from .env file"""
    envpath = os.path.join('..', '.env')
    credentials = {}

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
        print("✅ Loaded credentials from .env")
        return credentials
    else:
        print("❌ .env file not found")
        return None


def send_single_csv_email(csv_file, data_dir, credentials):
    """Send ONE email with ONE CSV file attachment"""
    print(f"📧 Sending email for: {csv_file}")

    try:
        # Connect to SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        server.starttls()
        server.login(credentials['GMAIL_ADDRESS'], credentials['GMAIL_APP_PASSWORD'])

        # Extract CSV type from filename
        csvtype = csv_file.split('__')[0]
        timestamp = csv_file.replace(csv_type + '__', '').replace('.csv', '')

        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Charlie Reporting <{credentials['GMAIL_ADDRESS']}>"
        msg['To'] = credentials['TARGET_EMAIL']
        msg['Subject'] = f"Hourly Report - {csv_type} Data {time_stamp}"

        # Email body
        body = """Call Center {csv_type} Report

Time Period: {time_stamp}
Report Type: {csv_type}
File: {csv_file}

This email contains one CSV file with {csv_type} data for the specified time period.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Call Center Reporting System"""

        msg.attach(MIMEText(body, 'plain'))

        # Attach the single CSV file
        csvpath = os.path.join(data_dir, csv_file)
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as attachment:
                part = MIMEBase('application', 'octet - stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content - Disposition',
                f'attachment; filename= {csv_file}',
            )
            msg.attach(part)

        # Send email
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent for {csv_file}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email for {csv_file}: {e}")
        return False


def main():
    print("📊 CSV Email Sender - One File Per Email")
    print("=" * 50)

    # Load credentials
    credentials = load_env_credentials()
    if not credentials:
        print("❌ Cannot load credentials")
        return

    # Check data directory
    datadir = '../data / generated'
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return

    print(f"📁 Scanning {data_dir} for CSV files...")

    # Get ALL CSV files (not grouped by type)
    allcsv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    if not all_csv_files:
        print("❌ No CSV files found!")
        return

    # Sort files by name for consistent ordering
    all_csv_files.sort()

    print(f"📊 Found {len(all_csv_files)} CSV files to send")
    print("🚀 Sending individual emails (1 CSV file per email)...")

    successcount = 0
    for i, csv_file in enumerate(all_csv_files, 1):
        print(f"\n📧 Email {i}/{len(all_csv_files)}: {csv_file}")

        if send_single_csv_email(csv_file, data_dir, credentials):
            success_count += 1

        # Small delay between emails to avoid rate limiting
        if i < len(all_csv_files):  # Don't delay after last email
            print("⏱️ Waiting 1 second...")
            time.sleep(1)

    print(f"\n🎉 Successfully sent {success_count}/{len(all_csv_files)} emails!")
    print("📬 Each email contains exactly 1 CSV file")
    print("� Check your inbox for all the individual CSV emails!")


if __name__ == "__main__":
    main()