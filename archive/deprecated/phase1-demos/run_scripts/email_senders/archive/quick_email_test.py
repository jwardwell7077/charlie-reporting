"""
quick_email_test.py
------------------
Quick test of the email configuration
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def load_env():
    """Load .env file"""
    envpath = "../.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded .env file")
    else:
        print("❌ .env file not found")


def test_email():
    """Quick email test"""
    print("🧪 Quick Email Test")
    print("=" * 30)

    # Load environment
    load_env()

    # Get credentials
    senderemail = os.getenv('GMAIL_ADDRESS')
    senderpassword = os.getenv('GMAIL_APP_PASSWORD')
    targetemail = os.getenv('TARGET_EMAIL')

    print(f"From: {sender_email}")
    print(f"To: {target_email}")
    print(f"Password: {'Set' if sender_password else 'NOT SET'}")

    if not sender_email or not sender_password:
        print("❌ Missing credentials in .env file")
        return False

    try:
        # Connect to Gmail
        print("\n📧 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        print("✅ Connected successfully!")

        # Create test message
        msg = MIMEMultipart()
        msg['From'] = f"Charlie Reporting <{sender_email}>"
        msg['To'] = target_email
        msg['Subject'] = "Charlie Reporting - Quick Test"

        body = """Quick test email from Charlie Reporting System!

This email confirms that:
✅ SMTP connection is working
✅ Authentication is successful
✅ Email can be sent from {sender_email}

Time: {__import__('datetime').datetime.now()}

Ready for demo operations!"""

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        print("📤 Sending test email...")
        text = msg.as_string()
        server.sendmail(sender_email, target_email, text)
        server.quit()

        print("✅ Test email sent successfully!")
        print(f"📧 Check {target_email} for the test message")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_email()