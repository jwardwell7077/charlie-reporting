#!/usr / bin / env python3
"""
Legacy Code Migration Script
Phases out old src/ code and integrates with new microservices architecture
"""

import shutil
from pathlib import Path
from datetime import datetime
import argparse


class LegacyMigrator:
    """Handles migration from monolithic src/ to microservices architecture"""

    def __init__(self, project_root: str):
        self.projectroot = Path(project_root)
        self.srcdir = self.project_root / "src"
        self.servicesdir = self.project_root / "services"
        self.shareddir = self.project_root / "shared"
        self.backupdir = self.project_root / "legacy_backup" / datetime.now().strftime('%Y%m%d_%H%M%S')

    def analyze_dependencies(self):
        """Analyze dependencies between old and new code"""
        print("🔍 Analyzing legacy code dependencies...")

        legacyfiles = {
            'main.py': 'Monolithic entry point - Replace with API Gateway',
            'transformer.py': 'CSV processing - MIGRATED to services / report - generator / csv_processor.py',
            'excel_writer.py': 'Excel generation - MIGRATED to services / report - generator / excel_generator.py',
            'email_fetcher.py': 'Email processing - TO MIGRATE to services / email - service/',
            'config_loader.py': 'Configuration - TO MIGRATE to shared / config_manager.py',
            'logger.py': 'Logging utilities - TO MIGRATE to shared / logging_utils.py',
            'archiver.py': 'File archiving - TO INTEGRATE into file - management service',
            'utils.py': 'Utilities - TO MIGRATE to shared / utils.py'
        }

        print("\n📋 Legacy Code Analysis:")
        print("=" * 60)
        for filename, status in legacy_files.items():
            file_path = self.src_dir / filename
            exists = "✅" if file_path.exists() else "❌"
            print(f"{exists} {filename:<20} → {status}")

        return legacy_files

    def create_backup(self):
        """Create backup of src/ directory before migration"""
        print(f"\n💾 Creating backup at: {self.backup_dir}")

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        if self.src_dir.exists():
            shutil.copytree(self.src_dir, self.backup_dir / "src")
            print("✅ Backup created successfully")
        else:
            print("⚠️  src/ directory not found")

    def migrate_shared_utilities(self):
        """Migrate shared utilities to shared/ directory"""
        print("\n🔄 Migrating shared utilities...")

        self.shared_dir.mkdir(exist_ok=True)

        migrations = [
            ('config_loader.py', 'config_manager.py'),
            ('logger.py', 'logging_utils.py'),
            ('utils.py', 'utils.py')
        ]

        for old_file, new_file in migrations:
            oldpath = self.src_dir / old_file
            newpath = self.shared_dir / new_file

            if old_path.exists():
                print(f"  📦 {old_file} → shared/{new_file}")
                shutil.copy2(old_path, new_path)
                self.update_imports_in_file(new_path, old_file)
            else:
                print(f"  ⚠️  {old_file} not found")

    def create_legacy_bridge(self):
        """Create backward compatibility bridge"""
        print("\n🌉 Creating legacy compatibility bridge...")

        bridge_content = '''"""
Legacy Compatibility Bridge
Provides backward compatibility during Phase 2 migration
DEPRECATED: This module will be removed in Phase 3
"""
import warnings


def deprecated_warning(old_module: str, new_service: str):
    """Issue deprecation warning"""
    warnings.warn(
        f"{old_module} is deprecated. Use {new_service} instead.",
        DeprecationWarning,
        stacklevel=3
    )


class LegacyReportProcessor:
    """Deprecated: Use services / report - generator API instead"""

    def __init__(self, *args, **kwargs):
        deprecated_warning("ReportProcessor", "services / report - generator")
        # Minimal compatibility implementation
        pass

    def process_csvs(self, *args, **kwargs):
        deprecated_warning("process_csvs", "POST /process endpoint")
        raise NotImplementedError("Use report - generator service API")


class LegacyCSVTransformer:
    """Deprecated: Use services / report - generator / csv_processor instead"""

    def __init__(self, *args, **kwargs):
        deprecated_warning("CSVTransformer", "services / report - generator")
        pass

    def transform(self, *args, **kwargs):
        deprecated_warning("transform", "POST /transform endpoint")
        raise NotImplementedError("Use report - generator service API")


class LegacyExcelWriter:
    """Deprecated: Use services / report - generator / excel_generator instead"""

    def __init__(self, *args, **kwargs):
        deprecated_warning("ExcelWriter", "services / report - generator")
        pass

    def write_daily(self, *args, **kwargs):
        deprecated_warning("write_daily", "POST /process endpoint")
        raise NotImplementedError("Use report - generator service API")

# Compatibility imports (deprecated)
ReportProcessor = LegacyReportProcessor
CSVTransformer = LegacyCSVTransformer
ExcelWriter = LegacyExcelWriter
'''

        bridgepath = self.project_root / "legacy_bridge.py"
        with open(bridge_path, 'w') as f:
            f.write(bridge_content)

        print(f"✅ Legacy bridge created: {bridge_path}")

    def update_import_references(self):

        # Find all Python files that might import from src/
        python_files = []
        for pattern in ['**/*.py', '**/tests/**/*.py', '**/demos/**/*.py']:
            python_files.extend(self.project_root.glob(pattern))

        importmappings = {
            'from services.report_generator.csv_processor import': 'from services.report_generator.csv_processor import',
            'from services.report_generator.excel_generator import': 'from services.report_generator.excel_generator import',
            'from legacy_bridge import': 'from legacy_bridge import',
            'from services.report_generator.csv_processor import': 'from services.report_generator.csv_processor import',
            'from services.report_generator.excel_generator import': 'from services.report_generator.excel_generator import',
        }

        updatedfiles = 0
        for file_path in python_files:
            if 'legacy_backup' in str(file_path) or file_path.is_dir():
                continue

            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                original_content = content
                for old_import, new_import in import_mappings.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                        print(f"  📝 Updated imports in {file_path.relative_to(self.project_root)}")

                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    updated_files += 1

            except Exception as e:
                print(f"  ⚠️  Error updating {file_path}: {e}")

        print(f"✅ Updated {updated_files} files")

    def update_imports_in_file(self, file_path: Path, original_name: str):
        """Update imports within a migrated file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Update internal imports to use shared modules
            updates = {
                'from logger import': 'from .logging_utils import',
                'from config_loader import': 'from .config_manager import',
                'from utils import': 'from .utils import'
            }

            for old, new in updates.items():
                content = content.replace(old, new)

            with open(file_path, 'w') as f:
                f.write(content)

        except Exception as e:
            print(f"    ⚠️  Error updating imports in {file_path}: {e}")

    def create_migration_report(self):
        """Create detailed migration report"""
        print("\n📊 Creating migration report...")

        reportcontent = """# Legacy Code Migration Report
Generated: {datetime.now().isoformat()}

## Migration Status

### ✅ COMPLETED
- CSV processing logic → services / report - generator / csv_processor.py
- Excel generation logic → services / report - generator / excel_generator.py
- FastAPI service integration with business logic
- Comprehensive test framework for Phase 2

### 🔄 IN PROGRESS
- Email processing migration → services / email - service/
- Configuration management → shared / config_manager.py
- Logging utilities → shared / logging_utils.py

### 📋 TODO
- Complete email service implementation
- API Gateway setup
- Final src/ directory removal
- Update documentation

## Architecture Changes

### Before (Phase 1)
```
src/
├── main.py (monolithic entry point)
├── transformer.py (CSV processing)
├── excel_writer.py (Excel generation)
├── email_fetcher.py (email handling)
└── config_loader.py (configuration)
```

### After (Phase 2)
```
services/
├── report - generator/ (CSV + Excel processing)
├── email - service/ (email handling)
├── api - gateway/ (request routing)
└── scheduler - service/ (task scheduling)

shared/
├── config_manager.py (cross - service config)
├── logging_utils.py (centralized logging)
└── utils.py (common utilities)
```

## Benefits Achieved
- ✅ Microservices architecture with independent scaling
- ✅ Modern async / await patterns with FastAPI
- ✅ Comprehensive API documentation
- ✅ Enhanced error handling and monitoring
- ✅ Improved testability and maintainability
- ✅ Docker containerization ready

## Backward Compatibility
- Legacy bridge created for gradual migration
- Deprecation warnings for old interfaces
- Import mappings updated throughout codebase

## Next Steps
1. Complete email service migration
2. Set up API Gateway for unified access
3. Implement service discovery and health checks
4. Remove src/ directory after validation
5. Update all documentation and examples

## Rollback Plan
- Complete backup created at: {self.backup_dir}
- Legacy bridge provides compatibility layer
- Services can be disabled to revert to Phase 1
"""

        reportpath = self.project_root / "migration_report.md"
        with open(report_path, 'w') as f:
            f.write(report_content)

        print(f"✅ Migration report created: {report_path}")

    def validate_migration(self):
        """Validate that migration was successful"""
        print("\n🔍 Validating migration...")

        validations = []

        # Check if new services exist
        requiredservices = [
            'services / report_generator / main.py',
            'services / report_generator / csv_processor.py',
            'services / report_generator / excel_generator.py'
        ]

        for service_path in required_services:
            full_path = self.project_root / service_path
            exists = full_path.exists()
            validations.append((service_path, exists))
            status = "✅" if exists else "❌"
            print(f"  {status} {service_path}")

        # Check if backup was created
        backupexists = self.backup_dir.exists()
        validations.append(("backup", backup_exists))
        status = "✅" if backup_exists else "❌"
        print(f"  {status} Legacy backup created")

        # Check if legacy bridge exists
        bridgeexists = (self.project_root / "legacy_bridge.py").exists()
        validations.append(("bridge", bridge_exists))
        status = "✅" if bridge_exists else "❌"
        print(f"  {status} Legacy compatibility bridge")

        successcount = sum(1 for _, success in validations if success)
        totalcount = len(validations)

        print(f"\n📊 Validation Results: {success_count}/{total_count} checks passed")

        if success_count == total_count:
            print("🎉 Migration validation successful!")
            return True
        else:
            print("⚠️  Migration validation has issues - please review")
            return False

    def run_migration(self, create_backup=True):
        """Run complete migration process"""
        print("🚀 Starting Legacy Code Migration to Phase 2 Architecture")
        print("=" * 60)

        try:
            # Step 1: Analyze current state
            self.analyze_dependencies()

            # Step 2: Create backup
            if create_backup:
                self.create_backup()

            # Step 3: Migrate shared utilities
            self.migrate_shared_utilities()

            # Step 4: Create compatibility bridge
            self.create_legacy_bridge()

            # Step 5: Update imports
            self.update_import_references()

            # Step 6: Create migration report
            self.create_migration_report()

            # Step 7: Validate migration
            success = self.validate_migration()

            if success:
                print("\n🎉 Legacy migration completed successfully!")
                print(f"💾 Backup saved to: {self.backup_dir}")
                print("📖 See migration_report.md for details")
                print("\n🚀 Ready for Phase 2 deployment!")
            else:
                print("\n⚠️  Migration completed with issues - please review")

            return success

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Migrate legacy src/ code to Phase 2 microservices')
    parser.add_argument('--project - root', default='.', help='Project root directory')
    parser.add_argument('--no - backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--validate - only', action='store_true', help='Only run validation')

    args = parser.parse_args()

    migrator = LegacyMigrator(args.project_root)

    if args.validate_only:
        migrator.validate_migration()
    else:
        migrator.run_migration(create_backup=not args.no_backup)


if __name__ == "__main__":
    main()