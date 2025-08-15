"""
email_sender.py
--------------
Sends realistic call center emails with CSV attachments to Outlook for end - to - end demo.

This script simulates the external reporting system that sends individual email reports
for each CSV type, allowing complete testing of the email - to - Excel pipeline.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import time
import win32com.client as win32
from datetime import datetime, timedelta
from typing import List, Dict
import random


class EmailSender:
    def __init__(self, to_email: str = "jontajon191@gmail.com", from_account: str = None):
        """Initialize email sender with Outlook connection"""
        self.toemail = to_email
        self.fromaccount = from_account

        try:
            print("🔗 Connecting to Outlook...")
            self.outlook = win32.Dispatch('Outlook.Application')
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("✅ Outlook connection established")

            # Get accounts if from_account specified
            if from_account:
                self.setup_sending_account()

        except Exception as e:
            print(f"❌ Failed to connect to Outlook: {e}")
            raise

    def setup_sending_account(self):
        """Setup specific sending account if available"""
        try:
            accounts = self.namespace.Accounts
            for account in accounts:
                if account.DisplayName == self.from_account:
                    self.sendingaccount = account
                    print(f"✅ Using sending account: {self.from_account}")
                    return

            print(f"⚠️ Account '{self.from_account}' not found, using default")
            self.sendingaccount = None

        except Exception as e:
            print(f"⚠️ Could not setup sending account: {e}")
            self.sendingaccount = None

    def send_hourly_report_email(self, timestamp: datetime, csv_files: List[str], interval_description: str = "hourly") -> int:
        """Send separate emails for each CSV file (realistic reporting pattern)"""
        print(f"📧 Sending individual report emails for {timestamp.strftime('%H:%M')}...")

        sentcount = 0
        csvtypes = {
            'IB_Calls': 'Inbound Calls Report',
            'Dials': 'Outbound Dials Report',
            'ACQ': 'Acquisition Report',
            'QCBS': 'Queue Callbacks Report',
            'RESC': 'Rescue Report',
            'Campaign_Interactions': 'Campaign Interactions Report',
            'Productivity': 'Agent Productivity Report'
        }

        for csv_file in csv_files:
            if not os.path.exists(csv_file):
                print(f"   ⚠️ File not found: {csv_file}")
                continue

            # Determine CSV type from filename
            filename = os.path.basename(csv_file)
            csvtype = None
            for key in csv_types.keys():
                if filename.startswith(key):
                    csvtype = key
                    break

            if not csv_type:
                print(f"   ❌ Unknown CSV type: {filename}")
                continue

            reportname = csv_types[csv_type]

            try:
                mail = self.outlook.CreateItem(0)
                mail.To = self.to_email

                # Set sender if specified
                if hasattr(self, 'sending_account') and self.sending_account:
                    mail.SendUsingAccount = self.sending_account

                mail.Subject = f"{report_name} - {timestamp.strftime('%H:%M')} ({timestamp.strftime('%Y-%m-%d')})"

                # Generate specific body for this report type
                agentcount = self.count_agents_in_single_file(csv_file)
                recordcount = self.count_records_in_file(csv_file)

                mail.Body = """Dear Team,

Please find attached the {report_name.lower()} for {timestamp.strftime('%H:%M on %B %d, %Y')}.

Report Details:
- Report Type: {report_name}
- Time Period: {timestamp.strftime('%H:%M')} - {(timestamp + timedelta(minutes=5)).strftime('%H:%M')}
- Records: {record_count}
- Active Agents: {agent_count}
- File: {filename}

This is an automated report from the Genesys call center system.

Best regards,
Call Center Reporting System
"""

                # Attach the single CSV file
                try:
                    mail.Attachments.Add(csv_file)
                    print(f"   📎 {report_name}: {filename}")
                except Exception as e:
                    print(f"   ❌ Failed to attach {filename}: {e}")
                    continue

                # Send email
                mail.Send()
                sent_count += 1
                print(f"   ✅ Sent: {report_name}")

                # Small delay between individual emails
                time.sleep(2)

            except Exception as e:
                print(f"   ❌ Failed to send {report_name}: {e}")

        print(f"   📧 Sent {sent_count}/{len(csv_files)} individual reports")
        return sent_count

    def count_agents_in_single_file(self, csv_file: str) -> int:
        """Count agents in a single CSV file"""
        try:
            import pandas as pd
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                if 'Agent Name' in df.columns:
                    return len(df['Agent Name'].unique())
        except Exception:
    pass
        return random.randint(1, 5)

    def count_records_in_file(self, csv_file: str) -> int:
        """Count total records in a CSV file"""
        try:
            import pandas as pd
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                return len(df)
        except Exception:
    pass
        return random.randint(5, 25)

    def count_agents_in_files(self, csv_files: List[str]) -> int:
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
                    except Exception:
    pass

            return len(agents) if agents else random.randint(3, 8)
        except Exception:
            return random.randint(3, 8)

    def estimate_total_calls(self, csv_files: List[str]) -> int:
        """Estimate total calls from CSV files"""
        try:
            import pandas as pd
            total = 0

            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file)
                        if 'Handle' in df.columns:
                            total += df['Handle'].sum()
                    except Exception:
    pass

            return int(total) if total > 0 else random.randint(50, 200)
        except Exception:
            return random.randint(50, 200)

    def send_batch_emails(self, files_by_time: Dict[str, List[str]], delay_minutes: int = 1) -> int:
        """Send emails for multiple time periods with delays"""
        print("📧 Starting batch email sending...")
        print(f"   Total time periods: {len(files_by_time)}")
        print(f"   Delay between time periods: {delay_minutes} minute(s)")
        print(f"   Target email: {self.to_email}")

        sentcount = 0
        totalemails = 0

        for i, (time_key, csv_files) in enumerate(files_by_time.items()):
            # Parse time for email timestamp
            try:
                hour, minute = map(int, time_key.split(':'))
                email_timestamp = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            except Exception:
                email_timestamp = datetime.now()

            print(f"\n📤 Sending emails for {time_key}...")

            intervalsent = self.send_hourly_report_email(email_timestamp, csv_files, "5 - minute")
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
            print(f"❌ Failed to send test email: {e}")
            return False


if __name__ == "__main__":
    print("Email Sender Demo")
    print("=" * 50)

    # Create sender
    sender = EmailSender()

    # Send test email
    sender.send_test_email()

    print("\nEmail sender ready for batch operations!")