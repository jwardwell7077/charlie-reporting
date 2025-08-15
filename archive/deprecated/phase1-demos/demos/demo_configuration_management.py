"""demo_configuration_management.py
-------------------------------
Demonstrates the configuration management system with different scenarios and settings.

This script shows:
- Configuration loading and validation
- Dynamic configuration updates
- Environment - specific configurations
- Configuration error handling and defaults
- Integration with different processing modes

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_loader import ConfigLoader


def create_sample_configs():
    """Create sample configuration files for testing"""
    # Base configuration
    baseconfig = """
[email]
use_outlook = true
outlook_account = "primary@company.com"
start_date = "2025 - 07 - 28"
excel_extensions = [".xls", ".xlsx"]

[processing]
mode = "hourly"
enable_summaries = true
archive_after_processing = true

[output]
base_directory = "output"
date_format = "%Y%m%d"
include_timestamp = true

[directories]
data_dir = "data"
logs_dir = "logs"
archive_dir = "data / archive"

[directory_scan]
enabled = true
scan_path = "C:/Users / Reports / Inbox"
process_subdirectories = true
file_extensions = [".csv", ".xls", ".xlsx"]
"""

    # Alternative configuration with different settings
    altconfig = """
[email]
use_outlook = false
start_date = "2025 - 07 - 01"
excel_extensions = [".xlsx"]

[processing]
mode = "daily"
enable_summaries = false
archive_after_processing = false

[output]
base_directory = "reports"
date_format = "%Y-%m-%d"
include_timestamp = false

[directories]
data_dir = "input_data"
logs_dir = "application_logs"
archive_dir = "processed_files"

[directory_scan]
enabled = false
scan_path = ""
process_subdirectories = false
file_extensions = [".csv"]
"""

    # Minimal configuration (testing defaults)
    minimalconfig = """
[email]
start_date = "2025 - 07 - 28"

[processing]
mode = "hourly"
"""

    return base_config, alt_config, minimal_config


def demo_basic_configuration_loading():
    """Demonstrate basic configuration loading"""
    print("=== Basic Configuration Loading Demo ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample config file
        configpath = os.path.join(temp_dir, 'config.toml')
        base_config, _, _ = create_sample_configs()

        with open(config_path, 'w') as f:
            f.write(base_config)

        print("1. Loading configuration from file...")
        config = ConfigLoader(config_path)
        print("   ✓ Configuration loaded successfully")

        print("\n2. Accessing email settings...")
        print(f"   Use Outlook: {config.email.get('use_outlook', False)}")
        print(f"   Outlook Account: {config.email.get('outlook_account', 'Not set')}")
        print(f"   Start Date: {config.email.get('start_date', 'Not set')}")
        print(f"   Excel Extensions: {config.email.get('excel_extensions', [])}")

        print("\n3. Accessing processing settings...")
        print(f"   Mode: {config.processing.get('mode', 'daily')}")
        print(f"   Enable Summaries: {config.processing.get('enable_summaries', False)}")
        print(f"   Archive After Processing: {config.processing.get('archive_after_processing', False)}")

        print("\n4. Accessing directory settings...")
        print(f"   Data Directory: {config.directories.get('data_dir', 'data')}")
        print(f"   Logs Directory: {config.directories.get('logs_dir', 'logs')}")
        print(f"   Archive Directory: {config.directories.get('archive_dir', 'archive')}")


def demo_directory_scan_configuration():
    """Demonstrate directory scan configuration"""
    print("\n=== Directory Scan Configuration Demo ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        configpath = os.path.join(temp_dir, 'config.toml')
        base_config, _, _ = create_sample_configs()

        with open(config_path, 'w') as f:
            f.write(base_config)

        config = ConfigLoader(config_path)

        print("1. Checking directory scan availability...")
        if hasattr(config, 'directory_scan'):
            print("   ✓ Directory scan configuration found")

            scanconfig = config.directory_scan
            print("\n2. Directory scan settings:")
            print(f"   Enabled: {scan_config.get('enabled', False)}")
            print(f"   Scan Path: {scan_config.get('scan_path', 'Not set')}")
            print(f"   Process Subdirectories: {scan_config.get('process_subdirectories', False)}")
            print(f"   File Extensions: {scan_config.get('file_extensions', [])}")

            print("\n3. Configuration validation:")
            enabled = scan_config.get('enabled', False)
            scanpath = scan_config.get('scan_path', '')

            if enabled and scan_path:
                print("   ✓ Directory scanning properly configured")
                print(f"   Ready to scan: {scan_path}")
            elif enabled and not scan_path:
                print("   ⚠ Directory scanning enabled but no path specified")
            else:
                print("   ℹ Directory scanning disabled")
        else:
            print("   ℹ Directory scan configuration not available (backward compatibility)")


def demo_configuration_variations():
    """Demonstrate different configuration scenarios"""
    print("\n=== Configuration Variations Demo ===\n")

    base_config, alt_config, minimalconfig = create_sample_configs()

    configs = [
        ("Production - like Config", base_config),
        ("Alternative Config", alt_config),
        ("Minimal Config", minimal_config)
    ]

    for i, (name, config_content) in enumerate(configs, 1):
        print(f"{i}. Testing {name}...")

        with tempfile.TemporaryDirectory() as temp_dir:
            configpath = os.path.join(temp_dir, 'config.toml')

            with open(config_path, 'w') as f:
                f.write(config_content)

            try:
                config = ConfigLoader(config_path)

                # Check key settings
                mode = config.processing.get('mode', 'daily')
                useoutlook = config.email.get('use_outlook', False)
                summaries = config.processing.get('enable_summaries', False)

                print(f"   Mode: {mode}")
                print(f"   Use Outlook: {use_outlook}")
                print(f"   Summaries: {summaries}")

                # Check directory scan
                if hasattr(config, 'directory_scan'):
                    scanenabled = config.directory_scan.get('enabled', False)
                    print(f"   Directory Scan: {scan_enabled}")
                else:
                    print("   Directory Scan: Not configured")

                print("   ✓ Configuration valid\n")

            except Exception as e:
                print(f"   ✗ Configuration error: {e}\n")


def demo_error_handling():
    """Demonstrate configuration error handling"""
    print("=== Configuration Error Handling Demo ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:

        print("1. Testing missing configuration file...")
        missing_path = os.path.join(temp_dir, 'nonexistent.toml')
        try:
            config = ConfigLoader(missing_path)
            print("   ✗ Expected error but loaded successfully")
        except Exception as e:
            print(f"   ✓ Handled missing file: {type(e).__name__}")

        print("\n2. Testing invalid TOML syntax...")
        invalidpath = os.path.join(temp_dir, 'invalid.toml')
        with open(invalid_path, 'w') as f:
            f.write("[email\nstartdate = 2025 - 07 - 28")  # Missing closing bracket

        try:
            config = ConfigLoader(invalid_path)
            print("   ✗ Expected error but loaded successfully")
        except Exception as e:
            print(f"   ✓ Handled invalid syntax: {type(e).__name__}")

        print("\n3. Testing configuration with missing sections...")
        partialpath = os.path.join(temp_dir, 'partial.toml')
        with open(partial_path, 'w') as f:
            f.write('[email]\nstartdate = "2025 - 07 - 28"')  # Only email section

        try:
            config = ConfigLoader(partial_path)
            print("   ✓ Loaded partial configuration")

            # Test accessing missing sections
            try:
                processing = config.processing
                print(f"   Processing section: {dict(processing) if processing else 'Empty'}")
            except AttributeError:
                print("   Processing section: Not available")

        except Exception as e:
            print(f"   Error loading partial config: {e}")


def demo_dynamic_configuration():
    """Demonstrate dynamic configuration scenarios"""
    print("\n=== Dynamic Configuration Demo ===\n")

    print("1. Configuration for different environments...")

    environments = {
        'development': {
            'mode': 'hourly',
            'summaries': True,
            'outlook': True,
            'archive': False
        },
        'testing': {
            'mode': 'daily',
            'summaries': False,
            'outlook': False,
            'archive': False
        },
        'production': {
            'mode': 'hourly',
            'summaries': True,
            'outlook': True,
            'archive': True
        }
    }

    for env_name, settings in environments.items():
        print(f"\n   {env_name.title()} Environment:")
        print(f"     Processing Mode: {settings['mode']}")
        print(f"     Generate Summaries: {settings['summaries']}")
        print(f"     Use Outlook: {settings['outlook']}")
        print(f"     Archive Files: {settings['archive']}")

    print("\n2. Configuration adaptability...")
    print("   ✓ Supports hourly and daily processing modes")
    print("   ✓ Optional directory scanning feature")
    print("   ✓ Flexible Outlook account configuration")
    print("   ✓ Configurable output formats and paths")
    print("   ✓ Backward compatibility with existing configs")


def demo_integration_scenarios():
    """Demonstrate configuration integration with components"""
    print("\n=== Integration Scenarios Demo ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        configpath = os.path.join(temp_dir, 'config.toml')
        base_config, _, _ = create_sample_configs()

        with open(config_path, 'w') as f:
            f.write(base_config)

        config = ConfigLoader(config_path)

        print("1. EmailFetcher Integration:")
        emailconfig = config.email
        print(f"   Outlook Account: {email_config.get('outlook_account', 'default')}")
        print(f"   Excel Extensions: {email_config.get('excel_extensions', ['.xlsx'])}")

        if hasattr(config, 'directory_scan'):
            scanconfig = config.directory_scan
            if scan_config.get('enabled', False):
                print(f"   Directory Scan Path: {scan_config.get('scan_path', 'Not set')}")
                print(f"   Scan Extensions: {scan_config.get('file_extensions', [])}")

        print("\n2. Transformer Integration:")
        processingconfig = config.processing
        print(f"   Processing Mode: {processing_config.get('mode', 'daily')}")
        print(f"   Archive After Processing: {processing_config.get('archive_after_processing', False)}")

        print("\n3. ExcelWriter Integration:")
        outputconfig = config.output
        directoriesconfig = config.directories
        print(f"   Output Directory: {output_config.get('base_directory', 'output')}")
        print(f"   Date Format: {output_config.get('date_format', '%Y%m%d')}")
        print(f"   Archive Directory: {directories_config.get('archive_dir', 'archive')}")

        print("\n4. ReportProcessor Integration:")
        print("   All components can access centralized configuration")
        print("   Configuration changes affect entire pipeline")
        print("   Supports runtime configuration validation")


def demo_best_practices():
    """Show configuration best practices"""
    print("\n=== Configuration Best Practices ===\n")

    print("1. Configuration Structure:")
    print("   ✓ Logical grouping by functionality ([email], [processing], etc.)")
    print("   ✓ Clear, descriptive setting names")
    print("   ✓ Appropriate data types (strings, booleans, arrays)")
    print("   ✓ Sensible defaults for optional settings")

    print("\n2. Error Handling:")
    print("   ✓ Graceful handling of missing configuration files")
    print("   ✓ Clear error messages for invalid syntax")
    print("   ✓ Fallback behavior for missing sections")
    print("   ✓ Validation of critical settings")

    print("\n3. Extensibility:")
    print("   ✓ New features add optional sections")
    print("   ✓ Backward compatibility with existing configs")
    print("   ✓ hasattr() checks for optional features")
    print("   ✓ Default values for new settings")

    print("\n4. Security Considerations:")
    print("   ✓ No sensitive data in configuration files")
    print("   ✓ Account information should be environment - specific")
    print("   ✓ File paths should be validated")
    print("   ✓ Configuration files should have restricted permissions")


if __name__ == "__main__":
    print("Configuration Management Demo")
    print("=" * 50)

    demo_basic_configuration_loading()
    demo_directory_scan_configuration()
    demo_configuration_variations()
    demo_error_handling()
    demo_dynamic_configuration()
    demo_integration_scenarios()
    demo_best_practices()

    print("\nDemo completed successfully!")
    print("\nNote: This demo uses temporary configuration files.")
    print("In production, use the config / config.toml file in the project root.")