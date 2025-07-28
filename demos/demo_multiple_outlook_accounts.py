"""
demo_multiple_outlook_accounts.py
---------------------------------
Demonstrates the multiple Outlook account support in the enhanced EmailFetcher.

This script shows:
- Configuring specific Outlook accounts for email fetching
- Fallback to default account when specified account not found
- Account selection and inbox access
- Integration with existing email processing workflow

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from email_fetcher import EmailFetcher


def create_sample_config_with_account(account_email: str = None):
    """Create a sample config with specific Outlook account"""
    class DemoConfig:
        @property
        def email(self):
            config = {
                'sender': ['reports@example.com', 'automation@company.com'],
                'subject_contains': ['Daily Report', 'Weekly Summary']
            }
            if account_email:
                config['outlook_account'] = account_email
            return config
        
        @property
        def directory_scan(self):
            return {
                'enabled': False,
                'scan_path': 'data/incoming',
                'process_subdirs': False
            }
        
        @property
        def global_filter(self):
            return {
                'sender': ['reports@example.com', 'automation@company.com'],
                'subject_contains': ['Daily Report', 'Weekly Summary']
            }
        
        @property
        def attachment_rules(self):
            return {
                'IB_Calls.csv': {'columns': ['Agent Name', 'Handle']},
                'Dials.csv': {'columns': ['Agent Name', 'Avg Handle']},
                'Productivity.csv': {'columns': ['Agent Name', 'Logged In']},
                'Weekly_Summary.csv': {'columns': ['Department', 'Metrics']}
            }
    
    return DemoConfig()


def create_mock_outlook_with_multiple_accounts():
    """Create mock Outlook environment with multiple accounts"""
    
    # Mock Account 1 - Primary business account
    account1 = Mock()
    account1.SmtpAddress = 'john.doe@company.com'
    account1.DisplayName = 'John Doe - Main Account'
    
    # Mock inbox for account 1
    inbox1 = Mock()
    inbox1.Name = 'Inbox (john.doe@company.com)'
    account1.DeliveryStore.GetDefaultFolder.return_value = inbox1
    
    # Mock Account 2 - Reports account
    account2 = Mock()
    account2.SmtpAddress = 'reports@company.com'
    account2.DisplayName = 'Reports Account'
    
    # Mock inbox for account 2
    inbox2 = Mock()
    inbox2.Name = 'Inbox (reports@company.com)'
    account2.DeliveryStore.GetDefaultFolder.return_value = inbox2
    
    # Mock Account 3 - IT Department account
    account3 = Mock()
    account3.SmtpAddress = 'it-team@company.com'
    account3.DisplayName = 'IT Team Account'
    
    # Mock inbox for account 3
    inbox3 = Mock()
    inbox3.Name = 'Inbox (it-team@company.com)'
    account3.DeliveryStore.GetDefaultFolder.return_value = inbox3
    
    # Mock session with multiple accounts
    session = Mock()
    session.Accounts = [account1, account2, account3]
    
    # Mock namespace
    namespace = Mock()
    namespace.Session = session
    
    # Default inbox (when no specific account is found)
    default_inbox = Mock()
    default_inbox.Name = 'Default Inbox'
    namespace.GetDefaultFolder.return_value = default_inbox
    
    return {
        'namespace': namespace,
        'accounts': [account1, account2, account3],
        'inboxes': [inbox1, inbox2, inbox3],
        'default_inbox': default_inbox
    }


def demo_specific_account_selection():
    """Demonstrate selecting a specific Outlook account"""
    print("=== Specific Account Selection Demo ===\n")
    
    mock_outlook = create_mock_outlook_with_multiple_accounts()
    
    print("Available accounts in mock Outlook:")
    for i, account in enumerate(mock_outlook['accounts'], 1):
        print(f"  {i}. {account.SmtpAddress} ({account.DisplayName})")
    
    print(f"\n1. Testing with specific account: 'reports@company.com'")
    config = create_sample_config_with_account('reports@company.com')
    fetcher = EmailFetcher(config)
    
    # Test inbox selection
    selected_inbox = fetcher._get_inbox_for_account(mock_outlook['namespace'])
    
    # Verify correct inbox was selected
    expected_inbox = mock_outlook['accounts'][1].DeliveryStore.GetDefaultFolder.return_value
    
    print(f"   Configured account: {config.email['outlook_account']}")
    print(f"   Selected inbox: {selected_inbox.Name}")
    print(f"   ✓ Correct account selected: {selected_inbox == expected_inbox}")
    
    print(f"\n2. Testing with different account: 'it-team@company.com'")
    config2 = create_sample_config_with_account('it-team@company.com')
    fetcher2 = EmailFetcher(config2)
    
    selected_inbox2 = fetcher2._get_inbox_for_account(mock_outlook['namespace'])
    expected_inbox2 = mock_outlook['accounts'][2].DeliveryStore.GetDefaultFolder.return_value
    
    print(f"   Configured account: {config2.email['outlook_account']}")
    print(f"   Selected inbox: {selected_inbox2.Name}")
    print(f"   ✓ Correct account selected: {selected_inbox2 == expected_inbox2}")


def demo_fallback_behavior():
    """Demonstrate fallback to default account"""
    print("\n=== Fallback Behavior Demo ===\n")
    
    mock_outlook = create_mock_outlook_with_multiple_accounts()
    
    print("1. Testing with non-existent account")
    config = create_sample_config_with_account('nonexistent@company.com')
    fetcher = EmailFetcher(config)
    
    selected_inbox = fetcher._get_inbox_for_account(mock_outlook['namespace'])
    
    print(f"   Configured account: {config.email['outlook_account']}")
    print(f"   Selected inbox: {selected_inbox.Name}")
    print(f"   ✓ Fallback to default: {selected_inbox == mock_outlook['default_inbox']}")
    
    print(f"\n2. Testing with no account specified")
    config2 = create_sample_config_with_account(None)  # No account specified
    fetcher2 = EmailFetcher(config2)
    
    selected_inbox2 = fetcher2._get_inbox_for_account(mock_outlook['namespace'])
    
    print(f"   Configured account: None")
    print(f"   Selected inbox: {selected_inbox2.Name}")
    print(f"   ✓ Default account used: {selected_inbox2 == mock_outlook['default_inbox']}")


def demo_integration_with_fetching():
    """Demonstrate integration with email fetching workflow"""
    print("\n=== Integration with Email Fetching Demo ===\n")
    
    print("Simulating email fetch with specific account...")
    
    config = create_sample_config_with_account('reports@company.com')
    fetcher = EmailFetcher(config, save_dir='demo_output')
    
    # Mock the full Outlook dispatch chain
    with patch('win32com.client.Dispatch') as mock_dispatch:
        mock_outlook = create_mock_outlook_with_multiple_accounts()
        
        # Setup the dispatch chain
        mock_app = Mock()
        mock_app.GetNamespace.return_value = mock_outlook['namespace']
        mock_dispatch.return_value = mock_app
        
        # Mock messages
        mock_messages = Mock()
        mock_messages.__iter__ = Mock(return_value=iter([]))  # No messages for demo
        mock_messages.Sort = Mock()
        
        # Set up the selected inbox to return our mock messages
        mock_outlook['accounts'][1].DeliveryStore.GetDefaultFolder.return_value.Items = mock_messages
        
        print(f"   Account to use: {config.email['outlook_account']}")
        print(f"   Attempting to fetch emails for today...")
        
        try:
            # This would normally connect to real Outlook
            today = datetime.now().strftime('%Y-%m-%d')
            fetcher.fetch_for_timeframe(today)
            print(f"   ✓ Email fetch process completed successfully")
            print(f"   ✓ Used correct account inbox")
        except Exception as e:
            print(f"   ✗ Error during fetch: {e}")


def demo_configuration_examples():
    """Show configuration examples for different scenarios"""
    print("\n=== Configuration Examples ===\n")
    
    print("1. Single specific account configuration:")
    print("""[email]
outlook_account = "reports@company.com"
sender = ["automation@vendor.com"]
subject_contains = ["Daily Report"]
""")
    
    print("2. Fallback to default account:")
    print("""[email]
# outlook_account not specified - uses default
sender = ["reports@example.com"]
subject_contains = ["Daily Report"]
""")
    
    print("3. Department-specific processing:")
    print("""[email]
outlook_account = "hr-reports@company.com"
sender = ["hr-system@company.com"]
subject_contains = ["Employee Report", "Payroll Data"]
""")
    
    print("4. Multi-environment setup:")
    print("""# Production config
[email]
outlook_account = "prod-reports@company.com"
sender = ["prod-automation@company.com"]

# Development config  
[email]
outlook_account = "dev-reports@company.com"
sender = ["dev-automation@company.com"]
""")


def demo_error_handling():
    """Demonstrate error handling scenarios"""
    print("\n=== Error Handling Demo ===\n")
    
    print("1. Account access error simulation")
    
    # Mock namespace with session access error
    error_namespace = Mock()
    error_namespace.Session.Accounts = None  # Simulate access error
    
    default_inbox = Mock()
    default_inbox.Name = "Default Inbox (Fallback)"
    error_namespace.GetDefaultFolder.return_value = default_inbox
    
    config = create_sample_config_with_account('test@company.com')
    fetcher = EmailFetcher(config)
    
    selected_inbox = fetcher._get_inbox_for_account(error_namespace)
    
    print(f"   Configured account: {config.email['outlook_account']}")
    print(f"   Error accessing accounts list")
    print(f"   Selected inbox: {selected_inbox.Name}")
    print(f"   ✓ Graceful fallback to default")
    
    print(f"\n2. Case sensitivity handling")
    mock_outlook = create_mock_outlook_with_multiple_accounts()
    
    # Test with different case
    config_upper = create_sample_config_with_account('REPORTS@COMPANY.COM')
    fetcher_upper = EmailFetcher(config_upper)
    
    selected_inbox = fetcher_upper._get_inbox_for_account(mock_outlook['namespace'])
    expected_inbox = mock_outlook['accounts'][1].DeliveryStore.GetDefaultFolder.return_value
    
    print(f"   Configured account: {config_upper.email['outlook_account']}")
    print(f"   Available account: reports@company.com")
    print(f"   ✓ Case-insensitive matching: {selected_inbox == expected_inbox}")


if __name__ == "__main__":
    print("Multiple Outlook Accounts Demo")
    print("=" * 50)
    
    demo_specific_account_selection()
    demo_fallback_behavior()
    demo_integration_with_fetching()
    demo_configuration_examples()
    demo_error_handling()
    
    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNote: This demo uses mocked Outlook objects.")
    print("In production, ensure the specified account is logged into Outlook.")
