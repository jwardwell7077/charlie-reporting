"""
Simple Email Diagnostic - Check Outlook Status
"""

import win32com.client as win32
import time
from datetime import datetime

def main():
    print("🔍 Simple Outlook Diagnostic")
    print("=" * 40)
    
    try:
        # Connect to Outlook
        print("📧 Connecting to Outlook...")
        outlook = win32.Dispatch('Outlook.Application')
        print("✅ Connected to Outlook")
        
        # Get namespace
        namespace = outlook.GetNamespace("MAPI")
        
        # Check accounts
        print(f"\n📬 Email Accounts: {namespace.Accounts.Count}")
        for account in namespace.Accounts:
            print(f"   - {account.DisplayName}")
        
        # Check Outbox
        outbox = namespace.GetDefaultFolder(4)
        print(f"\n📤 Outbox: {outbox.Items.Count} items")
        
        # Check Sent Items (today)
        sent_folder = namespace.GetDefaultFolder(5)
        today_sent = 0
        for item in sent_folder.Items:
            try:
                if item.SentOn and item.SentOn.date() == datetime.now().date():
                    today_sent += 1
            except:
                pass
        print(f"📧 Sent today: {today_sent} items")
        
        # Send simple test
        print(f"\n🧪 Sending test email to jontajon191@gmail.com...")
        mail = outlook.CreateItem(0)
        mail.To = "jontajon191@gmail.com"
        mail.Subject = f"TEST - {datetime.now().strftime('%H:%M:%S')}"
        mail.Body = f"Test email sent at {datetime.now()}"
        
        mail.Send()
        print("✅ Email sent via Outlook")
        
        # Wait and check Outbox again
        print("\n⏱️ Waiting 3 seconds to check status...")
        time.sleep(3)
        
        outbox_after = namespace.GetDefaultFolder(4)
        print(f"📤 Outbox after sending: {outbox_after.Items.Count} items")
        
        if outbox_after.Items.Count > 0:
            print("⚠️ WARNING: Email may be stuck in Outbox!")
            print("   Try manually clicking Send/Receive in Outlook")
        else:
            print("✅ Email left Outbox successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
