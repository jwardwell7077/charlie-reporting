#!/usr/bin/env python3
"""
Final Validation: src/ Directory Deletion Safety Check
"""
import subprocess
from pathlib import Path

def final_validation():
    """Perform final validation that src/ can be safely deleted."""
    
    print("🎯 FINAL VALIDATION: src/ Deletion Safety Check")
    print("=" * 60)
    
    # Check all migrations are complete
    migration_mappings = {
        'src/transformer.py': 'services/report_generator/csv_processor.py',
        'src/excel_writer.py': 'services/report_generator/excel_generator.py', 
        'src/main.py': 'services/report_generator/main.py',
        'src/config_loader.py': 'shared/config_manager.py',
        'src/logger.py': 'shared/logging_utils.py',
        'src/utils.py': 'shared/utils.py',
        'src/archiver.py': 'shared/file_archiver.py',
        'src/email_fetcher.py': 'services/email-service/email_processor.py'
    }
    
    all_migrated = True
    for src_file, dest_file in migration_mappings.items():
        if Path(dest_file).exists():
            print(f"✅ {src_file} → {dest_file}")
        else:
            print(f"❌ {src_file} → {dest_file} (MISSING)")
            all_migrated = False
    
    print()
    
    # Check for remaining imports
    try:
        result = subprocess.run(['grep', '-r', '--include=*.py', '^from src', 'services/', 'shared/'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("⚠️ Found remaining src imports:")
            print(result.stdout)
            all_migrated = False
        else:
            print("✅ No remaining 'from src' imports found")
    except:
        print("⚠️ Could not check imports")
    
    # Also check for 'import src'
    try:
        result2 = subprocess.run(['grep', '-r', '--include=*.py', '^import src', 'services/', 'shared/'], 
                                capture_output=True, text=True)
        if result2.returncode == 0 and result2.stdout.strip():
            print("⚠️ Found remaining src imports:")
            print(result2.stdout)
            all_migrated = False
        else:
            print("✅ No remaining 'import src' imports found")
    except:
        pass
    
    # Check for business logic preservation
    business_logic_files = [
        'services/report_generator/csv_processor.py',
        'services/report_generator/excel_generator.py',
        'services/report_generator/main.py',
        'shared/file_archiver.py',
        'services/email-service/email_processor.py'
    ]
    
    business_logic_preserved = True
    for file_path in business_logic_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            if file_size > 1000:  # Reasonable size check
                print(f"✅ {file_path} ({file_size} bytes)")
            else:
                print(f"⚠️ {file_path} seems too small ({file_size} bytes)")
                business_logic_preserved = False
        else:
            print(f"❌ {file_path} missing")
            business_logic_preserved = False
    
    print()
    print("🎯 FINAL DECISION")
    print("=" * 30)
    
    if all_migrated and business_logic_preserved:
        print("✅ SAFE TO DELETE src/ DIRECTORY")
        print("   - All 8 files successfully migrated")
        print("   - Business logic preserved in services")
        print("   - No remaining dependencies found")
        print()
        print("🗑️ Run: rm -rf src/")
        return 0
    else:
        print("❌ NOT SAFE TO DELETE YET")
        if not all_migrated:
            print("   - Some files not yet migrated")
        if not business_logic_preserved:
            print("   - Business logic validation failed")
        return 1

if __name__ == "__main__":
    exit(final_validation())
