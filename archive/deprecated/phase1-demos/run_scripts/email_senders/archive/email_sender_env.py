"""
email_sender_env.py
------------------
Email sender using environment variables for secure credential storage.
This is a simpler alternative to OAuth that still avoids hardcoded passwords.

Set these environment variables:
- GMAIL_ADDRESS: Your Gmail address  
- GMAIL_APP_PASSWORD: Your Gmail app password
- TARGET_EMAIL: Where to send emails (optional, uses config default)

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import List, Dict
import random

class EnvEmailSender:
    def __init__(self, config_path: str = None):
        """Initialize email sender with environment variable authentication"""
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.toml')
        
        self.config = self.load_config(config_path)
        
        # Extract SMTP settings
        smtp_config = self.config.get('smtp', {})
        
        self.smtp_server = smtp_config.get('server', 'smtp.gmail.com')
        self.smtp_port = smtp_config.get('port', 587)
        self.sender_name = smtp_config.get('sender_name', 'Call Center Reports')
        
        # Get credentials from environment variables
        self.sender_email = os.getenv('GMAIL_ADDRESS')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        self.to_email = os.getenv('TARGET_EMAIL') or smtp_config.get('target_email', 'jontajon191@gmail.com')
        
        # Validate environment variables
        if not self.sender_email:
            print("❌ GMAIL_ADDRESS environment variable not set")
            print("   Set with: set GMAIL_ADDRESS=your-email@gmail.com")
            raise ValueError("Missing GMAIL_ADDRESS environment variable")
        
        if not self.sender_password:
            print("❌ GMAIL_APP_PASSWORD environment variable not set")
            print("   Set with: set GMAIL_APP_PASSWORD=your-app-password")
            print("   Get app password from: Google Account > Security > 2-Step Verification > App passwords")
            raise ValueError("Missing GMAIL_APP_PASSWORD environment variable")
        
        print(f"📧 Email sender configured:")
        print(f"   From: {self.sender_name} <{self.sender_email}>")
        print(f"   To: {self.to_email}")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
        print(f"   Auth: Environment variables (secure)")
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from TOML file"""
        try:
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
                'sender_name': 'Call Center Reports',
                'target_email': 'jontajon191@gmail.com'
            }
        }
    
    def create_smtp_connection(self):
        """Create and return SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            return server
        except Exception as e:
            print(f"❌ Failed to connect to SMTP server: {e}")
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
            msg['Subject'] = "Charlie Reporting System - Secure Test Email (Env Vars)"
            
            body = f"""This is a test email from the Charlie Reporting System using environment variable authentication.

Configuration:
- From: {self.sender_name} <{self.sender_email}>
- To: {self.to_email}
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- Auth Method: Environment Variables (secure)
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


def setup_environment_variables():
    """Helper to set up environment variables"""
    print("🔧 ENVIRONMENT VARIABLE SETUP")
    print("="*40)
    print()
    print("Set these environment variables:")
    print()
    print("Windows (PowerShell):")
    print('   $env:GMAIL_ADDRESS="your-email@gmail.com"')
    print('   $env:GMAIL_APP_PASSWORD="your-app-password"')
    print('   $env:TARGET_EMAIL="jontajon191@gmail.com"')
    print()
    print("Windows (CMD):")
    print('   set GMAIL_ADDRESS=your-email@gmail.com')
    print('   set GMAIL_APP_PASSWORD=your-app-password')
    print('   set TARGET_EMAIL=jontajon191@gmail.com')
    print()
    print("Linux/Mac:")
    print('   export GMAIL_ADDRESS="your-email@gmail.com"')
    print('   export GMAIL_APP_PASSWORD="your-app-password"')
    print('   export TARGET_EMAIL="jontajon191@gmail.com"')
    print()
    print("📋 To get Gmail App Password:")
    print("   1. Google Account > Security")
    print("   2. 2-Step Verification > App passwords")
    print("   3. Generate app password for 'Mail'")
    print()


if __name__ == "__main__":
    print("Environment Variable Email Sender Demo")
    print("="*50)
    
    try:
        # Create sender
        sender = EnvEmailSender()
        
        # Send test email
        if sender.send_test_email():
            print("\n✅ Email sender ready for batch operations!")
        else:
            print("\n❌ Test email failed. Check configuration.")
            
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        setup_environment_variables()
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
