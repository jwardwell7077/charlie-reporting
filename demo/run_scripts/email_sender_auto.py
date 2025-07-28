"""
email_sender_auto.py
-------------------
Automatic email sender that reads credentials from .env file - no password prompts!

This version automatically loads credentials from a .env file, so you never 
have to type passwords or deal with prompts.

Setup:
1. Copy .env.template to .env
2. Fill in your Gmail app password in .env
3. Run this script - it will send emails automatically!

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

class AutoEmailSender:
    def __init__(self, config_path: str = None):
        """Initialize email sender with automatic credential loading"""
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.toml')
        
        self.config = self.load_config(config_path)
        self.config_dir = os.path.dirname(config_path)
        
        # Load environment variables from .env file
        self.load_env_file()
        
        # Extract SMTP settings
        smtp_config = self.config.get('smtp', {})
        
        self.smtp_server = os.getenv('SMTP_SERVER') or smtp_config.get('server', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', smtp_config.get('port', 587)))
        self.sender_name = smtp_config.get('sender_name', 'Call Center Reports')
        
        # Get credentials from environment (.env file)
        self.sender_email = os.getenv('GMAIL_ADDRESS') or smtp_config.get('sender_email', '')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        self.to_email = os.getenv('TARGET_EMAIL') or smtp_config.get('target_email', 'jontajon191@gmail.com')
        
        # Validate credentials
        if not self.sender_email:
            self.print_setup_instructions()
            raise ValueError("Gmail address not configured")
        
        if not self.sender_password:
            self.print_setup_instructions()
            raise ValueError("Gmail app password not configured")
        
        print(f"📧 Email sender configured automatically:")
        print(f"   From: {self.sender_name} <{self.sender_email}>")
        print(f"   To: {self.to_email}")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
        print(f"   Auth: Automatic (.env file)")
    
    def load_env_file(self):
        """Load environment variables from .env file"""
        env_path = os.path.join(self.config_dir, '.env')
        
        if not os.path.exists(env_path):
            print(f"⚠️ .env file not found at {env_path}")
            print("   Creating from template...")
            self.create_env_from_template()
            return
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            
            print("✅ Loaded credentials from .env file")
            
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
    
    def create_env_from_template(self):
        """Create .env file from template"""
        template_path = os.path.join(self.config_dir, '.env.template')
        env_path = os.path.join(self.config_dir, '.env')
        
        if os.path.exists(template_path):
            try:
                import shutil
                shutil.copy(template_path, env_path)
                print(f"✅ Created .env file from template")
                print(f"   Edit {env_path} and add your Gmail app password")
            except Exception as e:
                print(f"❌ Error creating .env file: {e}")
        else:
            # Create basic .env file
            env_content = f"""# Charlie Reporting System - Email Credentials
GMAIL_ADDRESS={self.config.get('smtp', {}).get('sender_email', 'your-email@gmail.com')}
GMAIL_APP_PASSWORD=your-gmail-app-password-here
TARGET_EMAIL={self.config.get('smtp', {}).get('target_email', 'jontajon191@gmail.com')}
"""
            try:
                with open(env_path, 'w') as f:
                    f.write(env_content)
                print(f"✅ Created .env file at {env_path}")
            except Exception as e:
                print(f"❌ Error creating .env file: {e}")
    
    def print_setup_instructions(self):
        """Print setup instructions"""
        print("\n" + "="*60)
        print("🔧 AUTOMATIC EMAIL SETUP INSTRUCTIONS")
        print("="*60)
        print()
        print("1. 📄 Edit the .env file:")
        env_path = os.path.join(self.config_dir, '.env')
        print(f"   {env_path}")
        print()
        print("2. 🔑 Get Gmail App Password:")
        print("   - Go to Google Account > Security")
        print("   - Enable 2-Step Verification")
        print("   - Go to 2-Step Verification > App passwords")
        print("   - Generate app password for 'Mail'")
        print("   - Copy the 16-character password")
        print()
        print("3. ✏️ Update .env file:")
        print("   GMAIL_ADDRESS=jwardwell7077@gmail.com")
        print("   GMAIL_APP_PASSWORD=your-16-char-app-password")
        print("   TARGET_EMAIL=jontajon191@gmail.com")
        print()
        print("4. 🚀 Run again - no more prompts!")
        print()
        print("="*60)
    
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
                'sender_email': 'jwardwell7077@gmail.com',
                'sender_name': 'Genesys Call Center Reports',
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
            print(f"   Check your credentials in .env file")
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
    
    def send_hourly_report_email(self, timestamp: datetime, csv_files: List[str], 
                                interval_type: str = "hourly") -> int:
        """Send individual emails for each CSV file in the hourly report"""
        
        print(f"📧 Sending {interval_type} reports for {timestamp.strftime('%H:%M')}...")
        print(f"   Found {len(csv_files)} CSV files to send")
        
        sent_count = 0
        
        for csv_file in csv_files:
            if not os.path.exists(csv_file):
                print(f"   ⚠️ Skipping missing file: {os.path.basename(csv_file)}")
                continue
            
            # Extract report type from filename
            filename = os.path.basename(csv_file)
            report_type = filename.split('_')[0]  # Get first part before underscore
            
            # Send individual email
            if self.send_single_csv_email(csv_file, report_type, timestamp, interval_type):
                sent_count += 1
                # Small delay between emails to avoid rate limiting
                time.sleep(2)
            
        print(f"   📊 Sent {sent_count}/{len(csv_files)} reports successfully")
        return sent_count
    
    def send_batch_emails(self, files_by_time: Dict[str, List[str]], delay_minutes: int = 1) -> int:
        """Send emails for multiple time periods with delays"""
        print(f"📧 Starting batch email sending...")
        print(f"   Total time periods: {len(files_by_time)}")
        print(f"   Delay between time periods: {delay_minutes} minute(s)")
        print(f"   Target email: {self.to_email}")
        
        sent_count = 0
        total_emails = 0
        
        for i, (time_key, csv_files) in enumerate(files_by_time.items()):
            # Parse time for email timestamp
            try:
                hour, minute = map(int, time_key.split(':'))
                email_timestamp = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            except:
                email_timestamp = datetime.now()
            
            print(f"\n📤 Sending emails for {time_key}...")
            
            interval_sent = self.send_hourly_report_email(email_timestamp, csv_files, "5-minute")
            sent_count += interval_sent
            total_emails += len(csv_files)  # Expected emails
            
            # Delay before next time period (except for last one)
            if i < len(files_by_time) - 1:
                print(f"   ⏱️ Waiting {delay_minutes} minute(s) before next time period...")
                time.sleep(delay_minutes * 60)
        
        print(f"\n✅ Batch sending complete: {sent_count}/{total_emails} emails sent successfully")
        return sent_count
    
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
            msg['Subject'] = "Charlie Reporting System - Automatic Test Email"
            
            body = f"""This is a test email from the Charlie Reporting System using automatic authentication.

✅ No password prompts required!
✅ Credentials loaded automatically from .env file
✅ Ready for batch email operations

Configuration:
- From: {self.sender_name} <{self.sender_email}>
- To: {self.to_email}
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- Auth Method: Automatic (.env file)
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


if __name__ == "__main__":
    print("🤖 Charlie Reporting - Automatic Email Sender")
    print("="*50)
    print("📧 No password prompts - fully automated!")
    print()
    
    try:
        # Create sender
        sender = AutoEmailSender()
        
        # Send test email
        if sender.send_test_email():
            print("\n🎉 Success! Email sender ready for automated batch operations!")
            print("🔄 No more password prompts needed for future runs")
        else:
            print("\n❌ Test email failed. Check your .env configuration.")
            
    except ValueError as e:
        print(f"\n⚠️ Setup needed: {e}")
        print("\n💡 Follow the instructions above to complete setup")
    except Exception as e:
        print(f"\n❌ Error: {e}")
