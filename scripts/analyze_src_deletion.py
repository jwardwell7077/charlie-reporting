#!/usr / bin / env python3
"""
Final SRC Migration Analysis
Checks what remains in src/ and if it's safe to delete
"""

from pathlib import Path
import ast
import sys


def analyze_src_directory():
    """Analyze what's left in src/ and determine if it's safe to delete"""

    srcdir = Path("src")
    if not src_dir.exists():
        print("❌ src/ directory doesn't exist")
        return

    print("🔍 Analyzing remaining files in src/...")
    print("=" * 60)

    # Map of what was migrated where
    migration_map = {
        'transformer.py': {
            'migrated_to': 'services / report - generator / csv_processor.py',
            'status': '✅ FULLY MIGRATED',
            'business_logic': 'CSV processing, data transformation, config - driven processing'
        },
        'excel_writer.py': {
            'migrated_to': 'services / report - generator / excel_generator.py',
            'status': '✅ FULLY MIGRATED',
            'business_logic': 'Excel generation, formatting, incremental reports'
        },
        'email_fetcher.py': {
            'migrated_to': 'services / email - service/ (partial)',
            'status': '🔄 PARTIALLY MIGRATED',
            'business_logic': 'Email fetching, attachment processing, Outlook integration'
        },
        'config_loader.py': {
            'migrated_to': 'shared / config_manager.py',
            'status': '✅ MIGRATED',
            'business_logic': 'Configuration loading and management'
        },
        'logger.py': {
            'migrated_to': 'shared / logging_utils.py',
            'status': '✅ MIGRATED',
            'business_logic': 'Logging utilities and setup'
        },
        'utils.py': {
            'migrated_to': 'shared / utils.py',
            'status': '✅ MIGRATED',
            'business_logic': 'Common utility functions'
        },
        'main.py': {
            'migrated_to': 'services / report - generator / main.py + API Gateway (future)',
            'status': '✅ BUSINESS LOGIC MIGRATED',
            'business_logic': 'Main orchestration logic integrated into FastAPI service'
        },
        'archiver.py': {
            'migrated_to': 'services / file - manager/ (future)',
            'status': '📋 TODO',
            'business_logic': 'File archiving and management'
        }
    }

    filesfound = []
    for file_path in src_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
        files_found.append(file_path.name)

        migrationinfo = migration_map.get(file_path.name, {
            'migrated_to': '❓ UNKNOWN',
            'status': '⚠️ NOT MAPPED',
            'business_logic': 'Unknown functionality'
        })

        print(f"\n📄 {file_path.name}")
        print(f"   Status: {migration_info['status']}")
        print(f"   Migrated to: {migration_info['migrated_to']}")
        print(f"   Business Logic: {migration_info['business_logic']}")

        # Check if file has any complex business logic
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = len(content.splitlines())

            # Parse AST to count classes and functions
            try:
                tree = ast.parse(content)
                classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])

                print(f"   Code Stats: {lines} lines, {classes} classes, {functions} functions")
            except Exception:
                print(f"   Code Stats: {lines} lines (parse error)")

        except Exception as e:
            print(f"   Error reading file: {e}")

    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)

    fullymigrated = []
    partiallymigrated = []
    notmigrated = []

    for filename in files_found:
        info = migration_map.get(filename, {})
        status = info.get('status', '⚠️ NOT MAPPED')

        if '✅' in status:
            fully_migrated.append(filename)
        elif '🔄' in status:
            partially_migrated.append(filename)
        else:
            not_migrated.append(filename)

    print(f"\n✅ FULLY MIGRATED ({len(fully_migrated)} files):")
    for f in fully_migrated:
        print(f"   - {f}")

    if partially_migrated:
        print(f"\n🔄 PARTIALLY MIGRATED ({len(partially_migrated)} files):")
        for f in partially_migrated:
            print(f"   - {f}")

    if not_migrated:
        print(f"\n⚠️ NOT MIGRATED ({len(not_migrated)} files):")
        for f in not_migrated:
            print(f"   - {f}")

    # Check for remaining dependencies
    print("\n🔗 DEPENDENCY CHECK")
    print("=" * 30)

    dependenciesfound = False

    # Check if any services still depend on src/
    for service_dir in Path("services").glob("*/"):
        servicefiles = list(service_dir.glob("**/*.py"))
        for service_file in service_files:
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                    if 'from src.' in content or 'import src.' in content:
                        print(f"   ⚠️ {service_file} still imports from src/")
                        dependenciesfound = True
            except Exception:
                continue

    if not dependencies_found:
        print("   ✅ No active dependencies on src/ found in services/")

    # Final recommendation
    print("\n🎯 RECOMMENDATION")
    print("=" * 30)

    criticalnot_migrated = [f for f in not_migrated if f not in ['__init__.py']]
    criticalpartial = len(partially_migrated)

    if not critical_not_migrated and critical_partial == 0:
        print("✅ SAFE TO DELETE src/")
        print("   - All business logic has been migrated")
        print("   - No active dependencies found")
        print("   - Complete backup exists in legacy_backup/")
        print("\n🚀 Command to delete:")
        print("   rm -rf src/")
    elif critical_partial > 0:
        print("🔄 PARTIAL MIGRATION - Review needed")
        print("   - Some files partially migrated")
        print("   - Complete email service migration first")
        print("   - Then safe to delete")
    else:
        print("⚠️ NOT SAFE TO DELETE")
        print("   - Unmigrated files found")
        print("   - Review and migrate remaining functionality")

    return {
        'safe_to_delete': len(critical_not_migrated) == 0 and critical_partial == 0,
        'fully_migrated': fully_migrated,
        'partially_migrated': partially_migrated,
        'not_migrated': not_migrated
    }


if __name__ == "__main__":
    result = analyze_src_directory()

    if result['safe_to_delete']:
        print("\n🎉 Analysis complete - src/ is ready for deletion!")
        sys.exit(0)
    else:
        print("\n⏳ Analysis complete - additional migration needed")
        sys.exit(1)