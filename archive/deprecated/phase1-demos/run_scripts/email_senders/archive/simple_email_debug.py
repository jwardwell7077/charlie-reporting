#!/usr/bin/env python3
"""
Simple email debug script to test Gmail SMTP connection
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def test_email_connection():
    # Load environment variables
    env_path = os.path.join('..', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("✅ Loaded .env file")
    else:
        print("❌ .env file not found")
        return False
    
    # Get credentials
    gmail_address = os.getenv('GMAIL_ADDRESS')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    target_email = os.getenv('TARGET_EMAIL')
    
    print(f"📧 From: {gmail_address}")
    print(f"📧 To: {target_email}")
    print(f"🔑 Password: {'*' * len(gmail_password) if gmail_password else 'None'}")
    
    if not all([gmail_address, gmail_password, target_email]):
        print("❌ Missing credentials")
        return False
    
    try:
        print("🔌 Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("🔐 Starting TLS encryption...")
        
        print("🔑 Authenticating...")
        server.login(gmail_address, gmail_password)
        print("✅ Authentication successful!")
        
        # Create simple test message
        msg = MIMEMultipart()
        msg['From'] = f"Charlie Reporting Test <{gmail_address}>"
        msg['To'] = target_email
        msg['Subject'] = "Simple Email Test - Debug"
        
        body = "This is a simple test email to verify SMTP connection is working."
        msg.attach(MIMEText(body, 'plain'))
        
        print("📤 Sending test email...")
        server.send_message(msg)
        print("✅ Email sent successfully!")
        
        server.quit()
        print("🔚 Connection closed")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Email Debug Test")
    print("=" * 40)
    success = test_email_connection()
    if success:
        print("\n✅ Email test completed successfully!")
    else:
        print("\n❌ Email test failed!")
