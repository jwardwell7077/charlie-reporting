"""
test_single_csv.py
-----------------
Test sending a single CSV file as an email attachment

This will test:
1. CSV file generation
2. Email creation with attachment
3. SMTP sending with simple password auth
4. Attachment handling

Author: Jonathan Wardwell, Copilot, GPT - 4o
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import csv
import random


def load_env_file():
    """Load credentials from .env file"""
    envpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def create_test_csv():
    """Create a sample CSV file for testing"""

    # Create test data directory
    testdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    os.makedirs(test_dir, exist_ok=True)

    # Generate timestamp for the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csvfilename = f"IB_Calls_{timestamp}.csv"
    csvpath = os.path.join(test_dir, csv_filename)

    # Sample agent names
    agents = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Emma Brown']

    # Create CSV data
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['Agent Name', 'Handle', 'Avg Handle'])

        # Write sample data
        for agent in agents:
            handlecount = random.randint(15, 45)
            avghandle = round(random.uniform(180, 420), 1)  # 3 - 7 minutes in seconds
            writer.writerow([agent, handle_count, avg_handle])

    print(f"✅ Created test CSV: {csv_filename}")
    print(f"📁 Location: {csv_path}")

    return csv_path, csv_filename


def send_test_email_with_csv():
    """Send test email with CSV attachment"""

    # Load credentials
    load_env_file()

    gmailaddress = os.getenv('GMAIL_ADDRESS')
    gmailpassword = os.getenv('GMAIL_APP_PASSWORD')
    targetemail = os.getenv('TARGET_EMAIL')

    print("📧 Single CSV Attachment Test")
    print("=" * 40)
    print(f"📤 From: {gmail_address}")
    print(f"📥 To: {target_email}")
    print()

    # Create test CSV
    csv_path, csvfilename = create_test_csv()

    try:
        # Connect to Gmail
        print("🌐 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, gmail_password)

        # Create email message
        print("📝 Creating email with CSV attachment...")
        msg = MIMEMultipart()
        msg['From'] = f"Genesys Call Center Reports <{gmail_address}>"
        msg['To'] = target_email
        msg['Subject'] = f"Test CSV Attachment - {csv_filename}"

        # Email body
        body = """
Test Email with CSV Attachment - Charlie Reporting System

📊 Attached File: {csv_filename}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🧪 Test Type: Single CSV Attachment Test

This email contains a sample IB_Calls.csv file to verify:
✅ CSV file generation
✅ Email attachment handling
✅ SMTP delivery with app password authentication

If you receive this email with the CSV attachment, the system is working perfectly!

Best regards,
Charlie Reporting Test System
        """

        msg.attach(MIMEText(body, 'plain'))

        # Add CSV attachment
        print(f"📎 Attaching CSV file: {csv_filename}")
        with open(csv_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet - stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content - Disposition',
            f'attachment; filename= {csv_filename}'
        )
        msg.attach(part)

        # Send email
        print("📤 Sending email with attachment...")
        text = msg.as_string()
        server.sendmail(gmail_address, target_email, text)
        server.quit()

        print("✅ Test email sent successfully!")
        print(f"📬 Check {target_email} for:")
        print(f"   📧 Email subject: Test CSV Attachment - {csv_filename}")
        print(f"   📎 Attachment: {csv_filename}")
        print()
        print("🔍 Verify that:")
        print("   ✅ Email arrives in your inbox")
        print("   ✅ CSV attachment is present")
        print("   ✅ CSV file can be downloaded and opened")

        return True

    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Starting single CSV attachment test...")
    print()

    success = send_test_email_with_csv()

    print()
    if success:
        print("🎉 Single CSV test completed successfully!")
        print("   Ready for full demo with all 7 CSV types!")
    else:
        print("❌ Test failed - check error messages above")