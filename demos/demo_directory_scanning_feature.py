"""
demo_directory_scanning_feature.py
----------------------------------
Demonstrates the directory scanning capabilities of the enhanced EmailFetcher.

This script shows:
- Scanning directories for CSV files alongside Outlook
- Timestamped file processing from directories
- Configurable scan paths and subdirectory handling
- Integration with existing email fetching workflow

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from email_fetcher import EmailFetcher
from config_loader import ConfigLoader


def create_sample_config_with_directory_scan(scan_path: str):
    """Create a sample config with directory scanning enabled"""
    class DemoConfig:
        @property
        def email(self):
            return {
                'sender': ['reports@example.com'],
                'subject_contains': ['Daily Report'],
                'outlook_account': 'demo@company.com'
            }
        
        @property
        def directory_scan(self):
            return {
                'enabled': True,
                'scan_path': scan_path,
                'process_subdirs': True
            }
        
        @property
        def global_filter(self):
            return {
                'sender': ['reports@example.com'],
                'subject_contains': ['Daily Report']
            }
        
        @property
        def attachment_rules(self):
            return {
                'IB_Calls.csv': {'columns': ['Agent Name', 'Handle']},
                'Dials.csv': {'columns': ['Agent Name', 'Avg Handle']},
                'Productivity.csv': {'columns': ['Agent Name', 'Logged In']},
                'Test_Report.csv': {'columns': ['Data', 'Value']}
            }
    
    return DemoConfig()


def create_sample_csv_files(directory: str):
    """Create sample CSV files in the directory with different timestamps"""
    print(f"Creating sample CSV files in: {directory}")
    
    current_time = datetime.now()
    
    # Create main directory files
    files_data = [
        ('IB_Calls.csv', current_time - timedelta(hours=1), 'Agent Name,Handle,Avg Handle\nJohn Doe,150,00:02:30\nJane Smith,120,00:03:15'),
        ('Dials.csv', current_time - timedelta(minutes=30), 'Agent Name,Handle,Avg Handle,Avg Talk\nJohn Doe,75,00:01:45,00:04:20\nJane Smith,88,00:02:10,00:03:50'),
        ('Productivity.csv', current_time - timedelta(hours=2), 'Agent Name,Logged In,On Queue,Idle\nJohn Doe,08:00:00,07:30:00,00:15:00\nJane Smith,08:15:00,07:45:00,00:10:00'),
        ('Test_Report.csv', current_time - timedelta(minutes=15), 'Data,Value,Timestamp\nMetric1,100,2025-07-28 14:00\nMetric2,85,2025-07-28 14:15'),
        ('Ignored_File.txt', current_time, 'This file should be ignored (not CSV)'),
        ('Unknown_Report.csv', current_time, 'Unknown,Data\n1,2')  # Should be ignored (no matching rule)
    ]
    
    # Create subdirectory
    subdir = os.path.join(directory, 'archive')
    os.makedirs(subdir, exist_ok=True)
    
    created_files = []
    
    for filename, mod_time, content in files_data:
        file_path = os.path.join(directory, filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Set modification time
        timestamp = mod_time.timestamp()
        os.utime(file_path, (timestamp, timestamp))
        
        created_files.append((filename, mod_time))
        print(f"  Created: {filename} (modified: {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    # Create file in subdirectory
    sub_file = os.path.join(subdir, 'IB_Calls_Archive.csv')
    with open(sub_file, 'w') as f:
        f.write('Agent Name,Handle\nArchived Agent,50')
    
    sub_mod_time = current_time - timedelta(hours=3)
    timestamp = sub_mod_time.timestamp()
    os.utime(sub_file, (timestamp, timestamp))
    
    created_files.append((f'archive/IB_Calls_Archive.csv', sub_mod_time))
    print(f"  Created: archive/IB_Calls_Archive.csv (modified: {sub_mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    return created_files


def demo_directory_scanning():
    """Demonstrate directory scanning functionality"""
    print("=== Directory Scanning Feature Demo ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create scan and save directories
        scan_dir = os.path.join(temp_dir, 'incoming')
        save_dir = os.path.join(temp_dir, 'processed')
        os.makedirs(scan_dir)
        os.makedirs(save_dir)
        
        print("1. Setting up demo environment...")
        created_files = create_sample_csv_files(scan_dir)
        
        print(f"\n2. Configuring EmailFetcher with directory scanning...")
        config = create_sample_config_with_directory_scan(scan_dir)
        fetcher = EmailFetcher(config, save_dir=save_dir)
        
        print(f"   Directory scan path: {scan_dir}")
        print(f"   Save directory: {save_dir}")
        print(f"   Subdirectory processing: {config.directory_scan['process_subdirs']}")
        
        print(f"\n3. Scanning for files modified today...")
        today = datetime.now().strftime('%Y-%m-%d')
        fetcher._scan_directory_for_date(today)
        
        # Check results
        processed_files = os.listdir(save_dir)
        print(f"\n4. Results:")
        print(f"   Files found in scan directory: {len(created_files)}")
        print(f"   Files processed and copied: {len(processed_files)}")
        
        if processed_files:
            print(f"   Processed files:")
            for file in sorted(processed_files):
                print(f"     - {file}")
        
        print(f"\n5. Demonstrating hourly scanning...")
        current_hour = datetime.now().hour
        fetcher._scan_directory_for_hour(today, current_hour)
        
        print(f"\n6. Demonstrating recent file scanning (last 2 hours)...")
        fetcher._scan_directory_for_recent(2)
        
        # Show final results
        final_files = os.listdir(save_dir)
        print(f"\n7. Final results:")
        print(f"   Total files in save directory: {len(final_files)}")
        
        # Demonstrate file naming convention
        print(f"\n8. Timestamped filename examples:")
        for file in sorted(final_files)[:3]:  # Show first 3
            print(f"     {file}")
            if '__' in file:
                base, timestamp_ext = file.split('__', 1)
                timestamp_part = timestamp_ext.split('.')[0]
                print(f"       Base name: {base}")
                print(f"       Timestamp: {timestamp_part}")


def demo_configuration_options():
    """Demonstrate configuration options for directory scanning"""
    print("\n=== Directory Scanning Configuration Options ===\n")
    
    print("Configuration in config.toml:")
    print("""
[directory_scan]
enabled = true                    # Enable/disable directory scanning
scan_path = "data/incoming"       # Directory to scan for CSV files
process_subdirs = false           # Whether to scan subdirectories recursively

# Optional: Integration with email fetching
[email]
outlook_account = "user@company.com"  # Specific Outlook account to use
sender = ["reports@example.com"]
subject_contains = ["Daily Report"]
""")
    
    print("Integration points:")
    print("- fetch() - Scans directory after processing Outlook emails")
    print("- fetch_hourly() - Scans for files modified in specific hour")
    print("- fetch_recent() - Scans for files modified in recent hours")
    print("- Automatic timestamping matches email attachment format")
    print("- Same rule matching system applies to directory files")


def demo_use_cases():
    """Demonstrate common use cases for directory scanning"""
    print("\n=== Common Use Cases ===\n")
    
    print("1. Automated File Drop Processing:")
    print("   - External systems drop CSV files in monitored directory")
    print("   - EmailFetcher processes both email attachments and dropped files")
    print("   - Unified workflow for all data sources")
    
    print("\n2. Backup Data Source:")
    print("   - Primary: Email attachments from automated reports")
    print("   - Backup: Manual file drops when email system is down")
    print("   - Seamless processing regardless of data source")
    
    print("\n3. Historical Data Processing:")
    print("   - Process old files from archive directories")
    print("   - Subdirectory scanning for organized file structures")
    print("   - Timestamp-based filtering for specific time periods")
    
    print("\n4. Multi-source Integration:")
    print("   - Multiple Outlook accounts (different departments)")
    print("   - File shares from different systems")
    print("   - Unified processing and reporting")


if __name__ == "__main__":
    print("Directory Scanning Feature Demo")
    print("=" * 50)
    
    demo_directory_scanning()
    demo_configuration_options()
    demo_use_cases()
    
    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNote: This demo uses temporary directories and mock data.")
    print("In production, configure the actual scan paths in config.toml")
