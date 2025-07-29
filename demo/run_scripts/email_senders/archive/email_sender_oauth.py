"""
email_sender_oauth.py
--------------------
Enhanced email sender with Google OAuth 2.0 and service account support for secure authentication.

This version supports:
1. OAuth 2.0 (most secure for user applications)
2. Service Account (for automated systems)
3. App Password fallback (least secure)

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import time
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import getpass
import base64

# Optional Google API imports - will fallback gracefully if not available
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.oauth2 import service_account
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("⚠️ Google Auth libraries not available. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2")

class SecureEmailSender:
    def __init__(self, config_path: str = None):
        """Initialize email sender with secure authentication from config file"""
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.toml')
        
        self.config = self.load_config(config_path)
        self.config_dir = os.path.dirname(config_path)
        
        # Extract SMTP settings
        smtp_config = self.config.get('smtp', {})
        
        self.smtp_server = smtp_config.get('server', 'smtp.gmail.com')
        self.smtp_port = smtp_config.get('port', 587)
        self.to_email = smtp_config.get('target_email', 'jontajon191@gmail.com')
        self.sender_name = smtp_config.get('sender_name', 'Call Center Reports')
        self.sender_email = smtp_config.get('sender_email', '')
        
        # Authentication settings
        self.auth_method = smtp_config.get('auth_method', 'oauth')
        self.credentials_file = smtp_config.get('credentials_file', 'credentials.json')
        self.token_file = smtp_config.get('token_file', 'token.json')
        
        # Make paths relative to config directory
        if not os.path.isabs(self.credentials_file):
            self.credentials_file = os.path.join(self.config_dir, self.credentials_file)
        if not os.path.isabs(self.token_file):
            self.token_file = os.path.join(self.config_dir, self.token_file)
        
        print(f"📧 Email sender configured:")
        print(f"   From: {self.sender_name} <{self.sender_email}>")
        print(f"   To: {self.to_email}")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
        print(f"   Auth Method: {self.auth_method}")
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from TOML file"""
        try:
            # Simple TOML parser for basic config
            return self.parse_simple_toml(config_path)
        except Exception as e:
            print(f"⚠️ Could not load config from {config_path}: {e}")
            return self.get_default_config()
    
    def parse_simple_toml(self, config_path: str) -> dict:
        """Simple TOML parser for basic configuration"""
        config = {}
        current_section = None
        
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        config[current_section] = {}
                    elif '=' in line and current_section:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        # Convert values
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        
                        config[current_section][key] = value
        except Exception as e:
            print(f"⚠️ Error parsing config: {e}")
            return self.get_default_config()
        
        return config
    
    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            'smtp': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'sender_email': '',
                'sender_name': 'Call Center Reports',
                'target_email': 'jontajon191@gmail.com',
                'auth_method': 'oauth',
                'credentials_file': 'credentials.json',
                'token_file': 'token.json'
            }
        }
    
    def get_oauth_credentials(self) -> Optional[Credentials]:
        """Get OAuth 2.0 credentials for Gmail API"""
        if not GOOGLE_AUTH_AVAILABLE:
            print("❌ Google Auth libraries not installed. Use: pip install google-auth google-auth-oauthlib")
            return None
        
        creds = None
        scopes = ['https://www.googleapis.com/auth/gmail.send']
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, scopes)
            except Exception as e:
                print(f"⚠️ Error loading existing token: {e}")
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ OAuth token refreshed")
                except Exception as e:
                    print(f"⚠️ Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Credentials file not found: {self.credentials_file}")
                    print("📋 To set up OAuth:")
                    print("   1. Go to https://console.cloud.google.com/")
                    print("   2. Create a project or select existing")
                    print("   3. Enable Gmail API")
                    print("   4. Create OAuth 2.0 credentials (Desktop application)")
                    print("   5. Download credentials.json to your demo folder")
                    return None
                
                try:
                    flow = Flow.from_client_secrets_file(
                        self.credentials_file, scopes)
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(f"🔐 Please visit this URL to authorize the application:")
                    print(f"   {auth_url}")
                    
                    auth_code = input("Enter the authorization code: ")
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    
                    # Save the credentials for the next run
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                    print("✅ OAuth credentials saved")
                    
                except Exception as e:
                    print(f"❌ OAuth setup failed: {e}")
                    return None
        
        return creds
    
    def get_service_account_credentials(self) -> Optional[service_account.Credentials]:
        """Get service account credentials"""
        if not GOOGLE_AUTH_AVAILABLE:
            print("❌ Google Auth libraries not installed")
            return None
        
        try:
            if not os.path.exists(self.credentials_file):
                print(f"❌ Service account file not found: {self.credentials_file}")
                print("📋 To set up service account:")
                print("   1. Go to https://console.cloud.google.com/")
                print("   2. IAM & Admin > Service Accounts")
                print("   3. Create service account")
                print("   4. Download JSON key file")
                return None
            
            scopes = ['https://www.googleapis.com/auth/gmail.send']
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes)
            
            # For service accounts, you need to impersonate the user
            delegated_credentials = credentials.with_subject(self.sender_email)
            return delegated_credentials
            
        except Exception as e:
            print(f"❌ Service account setup failed: {e}")
            return None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token based on auth method"""
        if self.auth_method == 'oauth':
            creds = self.get_oauth_credentials()
            if creds and creds.valid:
                return creds.token
        elif self.auth_method == 'service_account':
            creds = self.get_service_account_credentials()
            if creds:
                creds.refresh(Request())
                return creds.token
        
        return None
    
    def create_smtp_connection(self):
        """Create SMTP connection with appropriate authentication"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            if self.auth_method in ['oauth', 'service_account']:
                # Use OAuth/Service Account
                access_token = self.get_access_token()
                if access_token:
                    # OAuth XOAUTH2 authentication
                    auth_string = f'user={self.sender_email}\x01auth=Bearer {access_token}\x01\x01'
                    auth_string_b64 = base64.b64encode(auth_string.encode()).decode()
                    
                    server.docmd('AUTH', 'XOAUTH2 ' + auth_string_b64)
                    print("✅ OAuth authentication successful")
                else:
                    print("❌ Could not get access token, falling back to app password")
                    return self.create_smtp_connection_fallback(server)
            else:
                # Fallback to app password
                return self.create_smtp_connection_fallback(server)
            
            return server
            
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
            return None
    
    def create_smtp_connection_fallback(self, server=None):
        """Fallback to app password authentication"""
        try:
            if server is None:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            print("🔑 Using app password authentication")
            print("⚠️ For Gmail, use an App Password (not your regular password)")
            print("   Go to: Google Account > Security > 2-Step Verification > App passwords")
            
            password = getpass.getpass(f"Enter app password for {self.sender_email}: ")
            server.login(self.sender_email, password)
            print("✅ App password authentication successful")
            return server
            
        except Exception as e:
            print(f"❌ App password authentication failed: {e}")
            return None
    
    def get_email_signature(self) -> str:
        """Generate email signature"""
        return f"""Best regards,
{self.sender_name}
Automated Report Distribution System"""
    
    def send_single_csv_email(self, csv_file_path: str, report_type: str, 
                             timestamp: datetime, interval_type: str = "hourly") -> bool:
        """Send a single email with one CSV attachment"""
        
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV file not found: {csv_file_path}")
            return False
        
        try:
            # Create SMTP connection
            server = self.create_smtp_connection()
            if server is None:
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = self.to_email
            msg['Subject'] = f"{report_type} Report - {interval_type.title()} Data - {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            # Email body
            body = f"""Please find attached the {report_type} report for {interval_type} processing.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} {report_type} Data
File: {os.path.basename(csv_file_path)}

This automated report contains call center metrics and performance data.

{self.get_email_signature()}"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add CSV attachment
            with open(csv_file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(csv_file_path)}'
            )
            msg.attach(part)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, self.to_email, text)
            server.quit()
            
            print(f"   ✅ Sent {report_type} report")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to send {report_type}: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email to verify connection"""
        print("🧪 Sending test email...")
        
        try:
            # Create SMTP connection
            server = self.create_smtp_connection()
            if server is None:
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = self.to_email
            msg['Subject'] = "Charlie Reporting System - Secure Test Email"
            
            body = f"""This is a test email from the Charlie Reporting System using secure authentication.

Configuration:
- From: {self.sender_name} <{self.sender_email}>
- To: {self.to_email}
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- Auth Method: {self.auth_method}
- Time sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self.get_email_signature()}"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, self.to_email, text)
            server.quit()
            
            print("✅ Test email sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False


def setup_oauth_instructions():
    """Print detailed OAuth setup instructions"""
    print("📋 GOOGLE OAUTH 2.0 SETUP INSTRUCTIONS")
    print("=" * 50)
    print()
    print("1. 🌐 Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    print("2. 📁 Create or select a project")
    print()
    print("3. 🔧 Enable Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API'")
    print("   - Click 'Enable'")
    print()
    print("4. 🔑 Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("   - Choose 'Desktop application'")
    print("   - Name it 'Charlie Reporting System'")
    print("   - Download the JSON file")
    print()
    print("5. 📄 Save credentials:")
    print("   - Rename downloaded file to 'credentials.json'")
    print("   - Place it in your demo folder")
    print()
    print("6. 🚀 Run the email sender again!")


if __name__ == "__main__":
    print("Secure Email Sender Demo (OAuth 2.0)")
    print("=" * 50)
    
    # Check if Google Auth is available
    if not GOOGLE_AUTH_AVAILABLE:
        print("\n❌ Google Auth libraries not installed")
        print("📦 Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2")
        print("\nOr use app password method by changing auth_method to 'app_password' in config.toml")
        sys.exit(1)
    
    try:
        # Create sender
        sender = SecureEmailSender()
        
        # Send test email
        if sender.send_test_email():
            print("\n✅ Email sender ready for batch operations!")
        else:
            print("\n❌ Test email failed. Check configuration.")
            
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nFor detailed setup instructions, run:")
        print("python email_sender_oauth.py --help")
