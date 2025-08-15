"""
Manual SMTP Test
"""
import os
import sys

def main():
    print("🔧 Charlie Reporting - Manual SMTP Test")
    print("=" * 50)
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print()

    # Test basic imports
    try:
        import smtplib
        print("✅ smtplib imported successfully")
    except Exception as e:
        print(f"❌ smtplib error: {e}")
        return

    # Check .env file locations
    possible_env_paths = [
        "../.env",
        "../../demo/.env", 
        "c:/Users/jward/Documents/GitHub/charlie-reporting/demo/.env"
    ]
    
    env_found = False
    env_content = {}
    
    for env_path in possible_env_paths:
        if os.path.exists(env_path):
            print(f"✅ .env file found at: {env_path}")
            env_found = True
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()
                break
            except Exception as e:
                print(f"❌ Error reading .env file: {e}")
    
    if not env_found:
        print("❌ .env file not found in any of these locations:")
        for path in possible_env_paths:
            print(f"   {path}")
        return
    
    # Display credentials (hide password)
    gmail_address = env_content.get('GMAIL_ADDRESS', 'NOT SET')
    gmail_password = env_content.get('GMAIL_APP_PASSWORD', 'NOT SET')
    target_email = env_content.get('TARGET_EMAIL', 'NOT SET')
    
    print(f"Gmail Address: {gmail_address}")
    print(f"App Password: {'SET (hidden)' if gmail_password != 'NOT SET' else 'NOT SET'}")
    print(f"Target Email: {target_email}")
    print()
    
    if gmail_address == 'NOT SET' or gmail_password == 'NOT SET':
        print("❌ Missing required credentials in .env file")
        return
    
    # Test Gmail SMTP connection
    print("🧪 Testing Gmail SMTP connection...")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("✅ Connected to Gmail SMTP server")
        
        server.starttls()
        print("✅ TLS encryption enabled")
        
        server.login(gmail_address, gmail_password)
        print("✅ Gmail authentication successful!")
        
        # Send test email
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from datetime import datetime
        
        msg = MIMEMultipart()
        msg['From'] = f"Charlie Reporting <{gmail_address}>"
        msg['To'] = target_email
        msg['Subject'] = f"Charlie Reporting Test - {datetime.now().strftime('%H:%M:%S')}"
        
        body = f"""🎉 SUCCESS! Email system is working!

This test confirms:
✅ Python virtual environment is working
✅ SMTP connection established
✅ Gmail authentication successful
✅ Email sending functional

Configuration:
- From: {gmail_address}
- To: {target_email}
- Time: {datetime.now()}
- Python: {sys.executable}

Charlie Reporting System is ready for automated email operations!"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(gmail_address, target_email, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check {target_email} for the test message")
        print()
        print("🎉 ALL TESTS PASSED - Email system is ready!")
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        print()
        print("💡 Troubleshooting tips:")
        print("1. Make sure you're using Gmail App Password, not regular password")
        print("2. Enable 2-Step Verification in Google Account")
        print("3. Generate App Password: Google Account > Security > App passwords")
        print("4. App password should be 16 characters like: abcd efgh ijkl mnop")

if __name__ == "__main__":
    main()
    print("\nTest completed!")
