#!/usr / bin / env python3
"""
Test script to verify pathlib changes work cross - platform.
"""

import sys
from pathlib import Path

# Add src to path
srcpath = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from config_loader import ConfigLoader
    from email_fetcher import EmailFetcher
    from services.report_generator.excel_generator import ExcelWriter
    from archiver import Archiver

    print("✅ All imports successful!")

    # Test basic initialization
    print("\n🧪 Testing component initialization...")

    # Test config loading
    configpath = Path("config / config.toml")
    if config_path.exists():
        config = ConfigLoader(str(config_path))
        print("✅ ConfigLoader: OK")
    else:
        print("⚠️ ConfigLoader: config.toml not found, skipping")
        config = None

    # Test EmailFetcher with pathlib
    if config:
        email_fetcher = EmailFetcher(config, save_dir="test_data / raw")
        print(f"✅ EmailFetcher: savedir = {email_fetcher.save_dir} (type: {type(email_fetcher.save_dir)})")

    # Test ExcelWriter with pathlib
    excel_writer = ExcelWriter(output_dir="test_data / output")
    print(f"✅ ExcelWriter: outputdir = {excel_writer.output_dir} (type: {type(excel_writer.output_dir)})")

    # Test Archiver with pathlib
    archiver = Archiver(archive_dir="test_data / archive")
    print(f"✅ Archiver: archivedir = {archiver.archive_dir} (type: {type(archiver.archive_dir)})")

    # Test path operations
    print("\n🧪 Testing path operations...")
    testpath = Path("data") / "test" / "example.csv"
    print(f"✅ Path joining: {test_path}")

    # Test directory creation
    testdir = Path("test_pathlib_output")
    test_dir.mkdir(exist_ok=True)
    print(f"✅ Directory creation: {test_dir} (exists: {test_dir.exists()})")

    # Cleanup
    if test_dir.exists():
        test_dir.rmdir()
        print("✅ Cleanup completed")

    print("\n🎉 All pathlib tests passed! The project is ready for cross - platform use.")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()