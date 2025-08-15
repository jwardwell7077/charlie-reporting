"""email_debug.py
--------------
Debug email sending issues for the Charlie Reporting demo
"""

import time
from datetime import datetime

import win32com.client as win32


def check_outlook_folders():
    """Check Outlook folders for emails"""
    try:
        outlook = win32.Dispatch('Outlook.Application')
        namespace = outlook.GetNamespace("MAPI")

        print("📁 Checking Outlook folders...")

        # Check Outbox
        outbox = namespace.GetDefaultFolder(4)  # Outbox
        print(f"📤 Outbox items: {outbox.Items.Count}")
        if outbox.Items.Count > 0:
            print("   ⚠️ Items stuck in Outbox - they may not be sending!")
            for i, item in enumerate(outbox.Items):
                if i < 5:  # Show first 5
                    print(f"   - {item.Subject}")

        # Check Sent Items
        sent = namespace.GetDefaultFolder(5)  # Sent Items
        recentsent = []
        for item in sent.Items:
            if item.SentOn and (datetime.now() - item.SentOn.date()).days < 1:
                recent_sent.append(item)

        print(f"📧 Recent sent items (today): {len(recent_sent)}")
        for item in recent_sent[-5:]:  # Show last 5
            print(f"   - {item.Subject} -> {item.To}")

        # Check Drafts
        drafts = namespace.GetDefaultFolder(16)  # Drafts
        print(f"📝 Drafts: {drafts.Items.Count}")

        return True

    except Exception as e:
        print(f"❌ Error checking folders: {e}")
        return False


def send_diagnostic_email():
    """Send a diagnostic email with more details"""
    try:
        outlook = win32.Dispatch('Outlook.Application')

        # Get accounts info
        namespace = outlook.GetNamespace("MAPI")
        accounts = namespace.Accounts
        print(f"📧 Available accounts: {accounts.Count}")
        for account in accounts:
            print(f"   - {account.DisplayName} ({account.SmtpAddress})")

        # Create test email
        mail = outlook.CreateItem(0)
        mail.To = "jontajon191@gmail.com"
        mail.Subject = f"DIAGNOSTIC EMAIL - {datetime.now().strftime('%H:%M:%S')}"
        mail.Body = """This is a diagnostic email from Charlie Reporting System.

Timestamp: {datetime.now()}
From Application: Outlook COM Interface
Test ID: {random.randint(1000, 9999)}

If you receive this email, the basic sending is working.
Check your spam / junk folder if you don't see it in inbox.

This email was sent directly via Outlook automation.
"""

        print("📤 Sending diagnostic email...")
        mail.Send()
        print("✅ Diagnostic email dispatched")

        # Wait a moment then check Outbox
        time.sleep(2)
        check_outlook_folders()

        return True

    except Exception as e:
        print(f"❌ Failed to send diagnostic email: {e}")
        return False


def check_outlook_send_receive():
    """Force Outlook to send / receive"""
    try:
        outlook = win32.Dispatch('Outlook.Application')

        print("🔄 Forcing Outlook Send / Receive...")

        # Try to force send / receive
        namespace = outlook.GetNamespace("MAPI")
        namespace.SendAndReceive(False)  # False = send / receive all accounts

        print("✅ Send / Receive initiated")
        return True

    except Exception as e:
        print(f"❌ Error with Send / Receive: {e}")
        return False


if __name__ == "__main__":
    print("🔍 OUTLOOK EMAIL DIAGNOSTICS")
    print("=" * 50)

    # Check folders first
    check_outlook_folders()

    print("\n" + "=" * 50)

    # Send diagnostic email
    send_diagnostic_email()

    print("\n" + "=" * 50)

    # Force send / receive
    check_outlook_send_receive()

    print("\n🔍 DIAGNOSTIC COMPLETE")
    print("Check your jontajon191@gmail.com inbox and spam folder!")
    print("If emails are stuck in Outbox, try manually clicking Send / Receive in Outlook.")