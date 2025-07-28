"""
email_sender.py
--------------
Sends realistic call center emails with CSV attachments using native Python SMTP.

This script simulates the external reporting system that sends individual email reports
for each CSV type, allowing complete testing of the email-to-Excel pipeline.

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
import getpass
import toml

class EmailSender:
    def __init__(self, config_path: str = None):
        """Initialize email sender with SMTP configuration from config file"""
        
        # Load configuration
        if config_path is None:
            # Look for config in parent directory
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.toml')
        
        self.config = self.load_config(config_path)
        
        # Extract SMTP settings
        smtp_config = self.config.get('smtp', {})
        
        self.smtp_server = smtp_config.get('server', 'smtp.gmail.com')
        self.smtp_port = smtp_config.get('port', 587)
        self.to_email = smtp_config.get('target_email', 'jontajon191@gmail.com')
        self.sender_name = smtp_config.get('sender_name', 'Call Center Reports')
        
        # Get sender email from config or prompt
        config_sender = smtp_config.get('sender_email', '')
        if config_sender and config_sender != 'your-email@gmail.com':
            self.sender_email = config_sender
        else:
            self.sender_email = input("Enter your Gmail address: ")
        
        # Get password
        if smtp_config.get('use_app_password', True):
            print("⚠️ For Gmail, use an App Password (not your regular password)")
            print("   Go to: Google Account > Security > 2-Step Verification > App passwords")
        
        self.sender_password = getpass.getpass("Enter your Gmail App Password: ")
        
        print(f"📧 Email sender configured:")
        print(f"   From: {self.sender_name} <{self.sender_email}>")
        print(f"   To: {self.to_email}")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from TOML file"""
        try:
            # Try to import toml
            try:
                import toml
                with open(config_path, 'r') as f:
                    return toml.load(f)
            except ImportError:
                # Fallback: simple TOML parser for basic config
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
    
    def get_email_signature(self) -> str:
        """Generate email signature"""
        return f"""Best regards,
{self.sender_name}
Automated Report Distribution System"""
    
    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            'smtp': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'sender_email': '',
                'sender_name': 'Call Center Reports',
                'target_email': 'jontajon191@gmail.com',
                'use_app_password': True
            }
        }
    
    def create_smtp_connection(self):
        """Create and return SMTP connection"""
        try:
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.sender_email, self.sender_password)
            return server
        except Exception as e:
            print(f"❌ Failed to connect to SMTP server: {e}")
            return None
    
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
            
            # Dynamic subject and body based on report type
            subject_templates = {
                "ACQ": f"Acquisition Report - {interval_type.title()} Data",
                "Campaign_Interactions": f"Campaign Interactions Report - {interval_type.title()} Data", 
                "Dials": f"Dialing Activity Report - {interval_type.title()} Data",
                "IB_Calls": f"Inbound Calls Report - {interval_type.title()} Data",
                "Productivity": f"Agent Productivity Report - {interval_type.title()} Data",
                "QCBS": f"Quality & Compliance Report - {interval_type.title()} Data",
                "RESC": f"Resource Utilization Report - {interval_type.title()} Data"
            }
            
            body_templates = {
                "ACQ": f"""Please find attached the latest acquisition metrics report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Acquisition Data
File: {os.path.basename(csv_file_path)}

This report contains customer acquisition data including lead sources, 
conversion rates, and acquisition costs.

Best regards,
Call Center Reporting System""",
                
                "Campaign_Interactions": f"""Please find attached the campaign interactions report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Campaign Data
File: {os.path.basename(csv_file_path)}

This report includes campaign performance metrics, customer interactions,
and engagement statistics.

Best regards,
Call Center Reporting System""",
                
                "Dials": f"""Please find attached the dialing activity report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Dialing Data
File: {os.path.basename(csv_file_path)}

This report contains outbound dialing metrics including call attempts,
connection rates, and agent dialing performance.

Best regards,
Call Center Reporting System""",
                
                "IB_Calls": f"""Please find attached the inbound calls report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Inbound Call Data
File: {os.path.basename(csv_file_path)}

This report includes inbound call volumes, wait times, and
customer service metrics.

Best regards,
Call Center Reporting System""",
                
                "Productivity": f"""Please find attached the agent productivity report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Productivity Data
File: {os.path.basename(csv_file_path)}

This report contains agent performance metrics including call handling
times, break durations, and productivity scores.

Best regards,
Call Center Reporting System""",
                
                "QCBS": f"""Please find attached the quality & compliance report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Quality Data
File: {os.path.basename(csv_file_path)}

This report includes quality scores, compliance metrics, and
call monitoring results.

Best regards,
Call Center Reporting System""",
                
                "RESC": f"""Please find attached the resource utilization report.
                
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
Report Type: {interval_type.title()} Resource Data
File: {os.path.basename(csv_file_path)}

This report contains resource allocation data, system utilization,
and capacity planning metrics.

Best regards,
Call Center Reporting System"""
            }
            
            msg['Subject'] = subject_templates.get(report_type, f"{report_type} Report - {interval_type.title()} Data")
            
            # Add body
            body = body_templates.get(report_type, f"""Please find attached the {report_type} report.
            
Report Period: {timestamp.strftime('%Y-%m-%d %H:%M')}
File: {os.path.basename(csv_file_path)}

Best regards,
Call Center Reporting System""")
            
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
    
    def get_random_call_volume(self, csv_file: str) -> int:
        """Extract or generate realistic call volume for email context"""
        try:
            with open(csv_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    data_lines = lines[1:]  # Skip header
                    total = 0
                    for line in data_lines:
                        parts = line.strip().split(',')
                        for part in parts:
                            try:
                                num = float(part)
                                if 10 <= num <= 500:  # Reasonable call volume range
                                    total += num
                            except:
                                pass
            
            return int(total) if total > 0 else random.randint(50, 200)
        except:
            return random.randint(50, 200)
    
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
            msg['Subject'] = "Charlie Reporting System - Test Email"
            
            body = f"""This is a test email from the Charlie Reporting System.

If you receive this email, the SMTP integration is working correctly.

Configuration:
- From: {self.sender_email}
- To: {self.to_email}
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- Time sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The system is ready to send CSV report emails!"""
            
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
    print("Email Sender Demo (SMTP Version)")
    print("=" * 50)
    
    # Create sender
    sender = EmailSender()
    
    # Send test email
    sender.send_test_email()
    
    print("\nEmail sender ready for batch operations!")
