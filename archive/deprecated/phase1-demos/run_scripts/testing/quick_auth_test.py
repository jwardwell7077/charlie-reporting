"""
quick_auth_test.py
-----------------
Quick test of the new Gmail app password

Author: Jonathan Wardwell, Copilot, GPT - 4o
"""

import smtplib
import os


def test_quick_auth():
    """Quick authentication test"""

    # Load .env file
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

    gmailaddress = os.getenv('GMAIL_ADDRESS')
    gmailpassword = os.getenv('GMAIL_APP_PASSWORD')

    print("🔐 Testing authentication...")
    print(f"📧 Email: {gmail_address}")
    print(f"🔑 Password: {'*' * len(gmail_password)} ({len(gmail_password)} chars)")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, gmail_password)
        server.quit()

        print("✅ Authentication SUCCESS!")
        print("🎉 Your new app password works perfectly!")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


if __name__ == "__main__":
    test_quick_auth()