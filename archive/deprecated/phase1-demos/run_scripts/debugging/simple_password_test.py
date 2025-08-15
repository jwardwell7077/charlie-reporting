"""simple_password_test.py
----------------------
Test Gmail authentication with just username and password (app password)

This demonstrates the simplest possible Gmail authentication - just username and password!
No OAuth, no tokens, no complexity.

Author: Jonathan Wardwell, Copilot, GPT - 4o
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_env_file():
    """Load credentials from .env file"""
    envpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def test_simple_gmail_auth():
    """Test Gmail authentication with just username and password"""
    # Load credentials
    load_env_file()

    # Get credentials
    gmailaddress = os.getenv('GMAIL_ADDRESS')
    gmailpassword = os.getenv('GMAIL_APP_PASSWORD')
    targetemail = os.getenv('TARGET_EMAIL')

    print("🔐 Simple Gmail Authentication Test")
    print("=" * 40)
    print(f"📧 Gmail Address: {gmail_address}")
    print(f"🎯 Target Email: {target_email}")
    print(f"🔑 Password Length: {len(gmail_password) if gmail_password else 0} characters")
    print()

    if not gmail_address or not gmail_password:
        print("❌ Missing credentials in .env file")
        return False

    try:
        # Connect to Gmail SMTP server
        print("🌐 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable encryption

        # Login with just username and password
        print("🔐 Authenticating with username and password...")
        server.login(gmail_address, gmail_password)

        print("✅ Authentication successful!")

        # Create a simple test email
        print("📝 Creating test email...")
        msg = MIMEMultipart()
        msg['From'] = f"Charlie Reporting Test <{gmail_address}>"
        msg['To'] = target_email
        msg['Subject'] = "Simple Password Authentication Test - Charlie Reporting"

        body = """
This is a test email from the Charlie Reporting System!

🎉 Authentication Method: Simple Gmail App Password
🔐 No OAuth required
🚀 Just username + password authentication

This proves that simple password authentication is working perfectly!

Best regards,
Charlie Reporting System
        """

        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        print("📤 Sending test email...")
        text = msg.as_string()
        server.sendmail(gmail_address, target_email, text)
        server.quit()

        print("✅ Test email sent successfully!")
        print(f"📬 Check {target_email} for the test message")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


if __name__ == "__main__":
    success = test_simple_gmail_auth()
    if success:
        print("\n🎉 Simple password authentication is working perfectly!")
        print("   You can use this method for all your email sending needs.")
    else:
        print("\n❌ Authentication test failed.")
        print("   Check your .env file credentials.")