#!/usr/bin/env python3
"""
Development runner for Outlook-Relay Service
"""

import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

shared_dir = current_dir / "shared"
if shared_dir.exists():
    sys.path.insert(0, str(shared_dir))

def main():
    """Run the service in development mode"""
    print("🚀 Starting Outlook-Relay Service (Development Mode)")
    print("=" * 50)
    
    if not shared_dir.exists():
        print("⚠️  Shared components not found. Creating symlink...")
        try:
            shared_source = current_dir.parent.parent / "shared"
            if shared_source.exists():
                shared_dir.symlink_to(shared_source)
                print("✅ Created shared components symlink")
            else:
                print("❌ Shared components source not found")
                return 1
        except Exception as e:
            print(f"❌ Failed to create symlink: {e}")
            return 1
    
    try:
        from src.main import main as service_main
        import asyncio
        asyncio.run(service_main())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Service error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
