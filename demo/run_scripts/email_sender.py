"""
email_sender.py
--------------
Sends realistic call center emails with CSV attachments to Outlook for end-to-end demo.

This script simulates the external reporting system that sends hourly call center
data via email, allowing complete testing of the email-to-Excel pipeline.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import time
import win32com.client as win32
from datetime import datetime, timedelta
from typing import List, Dict
import random

class EmailSender:
    def __init__(self, to_email: str = "jontajon191@gmail.com", from_account: str = None):
        """Initialize email sender with Outlook connection"""
        self.to_email = to_email
        self.from_account = from_account
        
        try:
            print("🔗 Connecting to Outlook...")
            self.outlook = win32.Dispatch('Outlook.Application')
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("✅ Outlook connection established")
            
            # Get accounts if from_account specified
            if from_account:
                self._setup_sending_account()
                
        except Exception as e:
            print(f"❌ Failed to connect to Outlook: {e}")
            raise
    
    def _setup_sending_account(self):
        """Setup specific sending account if available"""
        try:
            accounts = self.namespace.Accounts
            for account in accounts:
                if account.DisplayName == self.from_account:
                    self.sending_account = account
                    print(f"✅ Using sending account: {self.from_account}")
                    return
            
            print(f"⚠️ Account '{self.from_account}' not found, using default")
            self.sending_account = None
            
        except Exception as e:
            print(f"⚠️ Could not setup sending account: {e}")
            self.sending_account = None
    
    def send_hourly_report_email(self, timestamp: datetime, csv_files: List[str], interval_description: str = "hourly") -> bool:
        """Send an email with CSV attachments for a specific time interval"""
        
        try:
            # Create email
            mail = self.outlook.CreateItem(0)  # 0 = Mail item
            
            # Set recipients
            mail.To = self.to_email
            
            # Set sender if specified
            if hasattr(self, 'sending_account') and self.sending_account:
                mail.SendUsingAccount = self.sending_account
            
            # Generate realistic subject
            subjects = [
                f"Call Center {interval_description.title()} Report - {timestamp.strftime('%H:%M')}",
                f"Genesys {interval_description.title()} Data Export - {timestamp.strftime('%Y-%m-%d %H:%M')}",
                f"Hourly Call Center Metrics - {timestamp.strftime('%B %d, %Y %H:%M')}",
                f"Automated Report: Call Data {timestamp.strftime('%H:%M')}"
            ]
            mail.Subject = random.choice(subjects)
            
            # Generate realistic body
            agent_count = self._count_agents_in_files(csv_files)
            total_calls = self._estimate_total_calls(csv_files)
            
            body_templates = [
                f"""Dear Team,

Please find attached the {interval_description} call center report for {timestamp.strftime('%H:%M on %B %d, %Y')}.

Report Summary:
- Time Period: {timestamp.strftime('%H:%M')} - {(timestamp + timedelta(minutes=5)).strftime('%H:%M')}
- Active Agents: {agent_count}
- Estimated Total Interactions: {total_calls}
- Data Files: {len(csv_files)} attachments

Files included:
{chr(10).join(f"- {os.path.basename(f)}" for f in csv_files)}

This is an automated report from the Genesys system.

Best regards,
Call Center Reporting System
""",
                f"""Automated Call Center Data Export

Report Details:
Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Interval: {interval_description.title()}
Agents: {agent_count}
Files: {len(csv_files)}

Data attachments ready for processing.

-- Genesys Reporting System
""",
                f"""📊 Call Center {interval_description.title()} Report

Time: {timestamp.strftime('%I:%M %p')}
Date: {timestamp.strftime('%A, %B %d, %Y')}

📈 Quick Stats:
• Active Agents: {agent_count}
• Data Files: {len(csv_files)}
• Report Type: {interval_description.title()}

Files attached:
{chr(10).join(f"• {os.path.basename(f)}" for f in csv_files)}

Automated delivery from genesysreports@genesysdev.com
"""
            ]
            
            mail.Body = random.choice(body_templates)
            
            # Attach CSV files
            attachments_added = 0
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    try:
                        mail.Attachments.Add(csv_file)
                        attachments_added += 1
                        print(f"   📎 Attached: {os.path.basename(csv_file)}")
                    except Exception as e:
                        print(f"   ❌ Failed to attach {csv_file}: {e}")
                else:
                    print(f"   ⚠️ File not found: {csv_file}")
            
            if attachments_added == 0:
                print("   ❌ No attachments added, skipping email")
                return False
            
            # Send email
            mail.Send()
            print(f"   ✅ Email sent successfully with {attachments_added} attachments")
            
            # Add small delay to prevent overwhelming Outlook
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to send email: {e}")
            return False
    
    def _count_agents_in_files(self, csv_files: List[str]) -> int:
        """Estimate number of unique agents from CSV files"""
        try:
            import pandas as pd
            agents = set()
            
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        if 'Agent Name' in df.columns:
                            agents.update(df['Agent Name'].unique())
                    except:
                        pass
            
            return len(agents) if agents else random.randint(3, 8)
            
        except:
            return random.randint(3, 8)
    
    def _estimate_total_calls(self, csv_files: List[str]) -> int:
        """Estimate total calls from CSV files"""
        try:
            import pandas as pd
            total = 0
            
            for csv_file in csv_files:
                if os.path.exists(csv_file) and 'IB_Calls' in csv_file:
                    try:
                        df = pd.read_csv(csv_file)
                        if 'Handle' in df.columns:
                            total += df['Handle'].sum()
                    except:
                        pass
            
            return total if total > 0 else random.randint(50, 200)
            
        except:
            return random.randint(50, 200)
    
    def send_batch_emails(self, files_by_time: Dict[str, List[str]], delay_minutes: int = 1) -> int:
        """Send multiple emails with specified delays"""
        print(f"📧 Starting batch email sending...")
        print(f"   Total time periods: {len(files_by_time)}")
        print(f"   Delay between emails: {delay_minutes} minute(s)")
        print(f"   Target email: {self.to_email}")
        
        sent_count = 0
        
        for i, (time_key, csv_files) in enumerate(files_by_time.items()):
            # Parse time for email timestamp
            try:
                hour, minute = map(int, time_key.split(':'))
                email_timestamp = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            except:
                email_timestamp = datetime.now()
            
            print(f"\n📤 Sending email {i+1}/{len(files_by_time)} for {time_key}...")
            
            if self.send_hourly_report_email(email_timestamp, csv_files, "5-minute"):
                sent_count += 1
            
            # Delay before next email (except for last one)
            if i < len(files_by_time) - 1:
                print(f"   ⏱️ Waiting {delay_minutes} minute(s) before next email...")
                time.sleep(delay_minutes * 60)
        
        print(f"\n✅ Batch sending complete: {sent_count}/{len(files_by_time)} emails sent")
        return sent_count
    
    def send_test_email(self) -> bool:
        """Send a test email to verify connection"""
        print("🧪 Sending test email...")
        
        try:
            mail = self.outlook.CreateItem(0)
            mail.To = self.to_email
            mail.Subject = "Charlie Reporting System - Test Email"
            mail.Body = """This is a test email from the Charlie Reporting System.

If you receive this email, the Outlook integration is working correctly.

Time sent: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            mail.Send()
            print("✅ Test email sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Test email failed: {e}")
            return False


if __name__ == "__main__":
    print("Email Sender Demo")
    print("=" * 50)
    
    # Test connection
    sender = EmailSender(to_email="jontajon191@gmail.com")
    
    # Send test email
    if sender.send_test_email():
        print("\n🎉 Email sender is ready for the full demo!")
    else:
        print("\n❌ Email sender setup failed. Please check Outlook configuration.")
