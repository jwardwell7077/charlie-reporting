#!/usr/bin/env python3
"""
cleanup_email_senders.py
------------------------
Clean up duplicate and obsolete email sender files

Keeps only the essential files:
- focused_email_sender.py (main production sender)
- simple_email_test.py (quick tests)
- setup_secure_email.py (setup utility)

Moves obsolete files to an archive folder
"""

import os
import shutil
from pathlib import Path

def cleanup_email_senders():
    """Clean up email_senders directory"""
    email_dir = Path(__file__).parent
    archive_dir = email_dir / "archive"
    
    # Create archive directory
    archive_dir.mkdir(exist_ok=True)
    
    # Files to keep (essential only)
    keep_files = {
        'focused_email_sender.py',    # Main production sender
        'simple_email_test.py',       # Quick test utility
        'setup_secure_email.py',      # Setup utility
        'archive'                     # Archive directory
    }
    
    # Files to archive (obsolete/duplicate)
    archive_files = [
        'csv_email_sender.py',
        'email_debug.py', 
        'email_sender.py',
        'email_sender_auto.py',
        'email_sender_env.py',
        'email_sender_fixed.py',
        'email_sender_oauth.py',
        'email_sender_smtp.py',
        'quick_email_test.py',
        'simple_email_debug.py'
    ]
    
    print("🧹 Cleaning up email_senders directory...")
    print(f"📁 Email dir: {email_dir}")
    print(f"📦 Archive dir: {archive_dir}")
    print()
    
    moved_count = 0
    for file_name in archive_files:
        file_path = email_dir / file_name
        if file_path.exists():
            dest_path = archive_dir / file_name
            try:
                shutil.move(str(file_path), str(dest_path))
                print(f"📦 Moved: {file_name}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move {file_name}: {e}")
    
    print(f"\n✅ Cleanup complete! Moved {moved_count} files to archive.")
    print(f"📋 Kept essential files:")
    for file_name in sorted(keep_files):
        if file_name != 'archive':
            file_path = email_dir / file_name
            if file_path.exists():
                print(f"   ✅ {file_name}")
            else:
                print(f"   ❓ {file_name} (not found)")

if __name__ == "__main__":
    cleanup_email_senders()
