#!/usr / bin / env python3
"""Root Directory Cleanup Script
Organize and clean up the cluttered root directory structure
"""
import shutil
from pathlib import Path


def analyze_root_directory():
    """Analyze current root directory structure."""
    print("🔍 ANALYZING ROOT DIRECTORY STRUCTURE")
    print("=" * 60)

    rootdir = Path(".")
    categories = {
        "config_files": [],
        "documentation": [],
        "scripts": [],
        "debug_files": [],
        "deprecated_files": [],
        "demo_files": [],
        "setup_files": [],
        "architecture_docs": [],
        "migration_artifacts": [],
        "keep_in_root": [],
        "unknown": []
    }

    # Categorize files
    for item in root_dir.iterdir():
        if item.name.startswith('.'):
            continue  # Skip hidden files

        name = item.name.lower()

        # Configuration files
        if any(x in name for x in ['config', '.toml', '.env', 'requirements']):
            categories["config_files"].append(item.name)

        # Documentation
        elif name.endswith('.md') or 'readme' in name:
            if any(x in name for x in ['architecture', 'microservices', 'enterprise']):
                categories["architecture_docs"].append(item.name)
            else:
                categories["documentation"].append(item.name)

        # Scripts and tools
        elif name.endswith('.py') and any(x in name for x in ['setup', 'convert', 'activate']):
            categories["setup_files"].append(item.name)
        elif name.endswith('.py') and 'debug' in name:
            categories["debug_files"].append(item.name)
        elif name.endswith('.py') and ('demo' in name or 'fetch' in name or 'test' in name):
            categories["demo_files"].append(item.name)
        elif name.endswith('.py') and item.name not in ['run.py']:
            categories["scripts"].append(item.name)

        # Shell scripts
        elif name.endswith(('.bat', '.ps1', '.sh')):
            categories["setup_files"].append(item.name)

        # Migration artifacts
        elif any(x in name for x in ['migration', 'legacy', 'bridge']):
            categories["migration_artifacts"].append(item.name)

        # Directories and important files to keep in root
        elif item.is_dir() or item.name in ['run.py', 'pyproject.toml', 'pytest.ini', 'README.md']:
            categories["keep_in_root"].append(item.name)

        else:
            categories["unknown"].append(item.name)

    # Display analysis
    for category, files in categories.items():
        if files:
            print(f"\n📁 {category.replace('_', ' ').title()}: {len(files)} items")
            for file in sorted(files):
                print(f"  - {file}")

    return categories


def create_cleanup_plan():
    """Create a cleanup plan for reorganizing files."""
    cleanupplan = {
        # Create new directories for organization
        "create_directories": [
            "archive / deprecated",
            "archive / debug",
            "archive / demos",
            "archive / setup",
            "archive / migration",
            "docs / architecture",
            "tools / setup",
            "tools / development"
        ],

        # File movements
        "move_operations": {
            # Configuration files
            "config_example_rest_architecture.toml": "archive / deprecated/",
            "requirements - unified.txt": "archive / deprecated/",
            "windows_service_requirements.txt": "archive / deprecated/",

            # Debug files
            "debug_email_time.py": "archive / debug/",
            "debug_fetch_recent.py": "archive / debug/",
            "debug_mock.py": "archive / debug/",
            "debug_transformer.py": "archive / debug/",
            "test_pathlib_changes.py": "archive / debug/",

            # Demo files
            "demo_new_features.py": "archive / demos/",
            "fetch_csv_emails.py": "archive / demos/",
            "rest_email_fetcher.py": "archive / deprecated/",
            "windows_email_service.py": "archive / deprecated/",

            # Setup files
            "activate_env.bat": "tools / setup/",
            "activate_env.ps1": "tools / setup/",
            "activate_wsl2.sh": "tools / setup/",
            "convert_wsl2_to_windows.py": "tools / setup/",
            "setup_complete_wsl2_workflow.py": "tools / setup/",
            "setup_dev.py": "tools / development/",
            "setup_project_environment.py": "tools / setup/",
            "setup_wsl2_dev.sh": "tools / setup/",

            # Architecture documentation
            "common_service_architecture.md": "docs / architecture/",
            "email_service_design.md": "docs / architecture/",
            "enterprise_architecture.md": "docs / architecture/",
            "implementation_roadmap.md": "docs / architecture/",
            "microservices_architecture.md": "docs / architecture/",
            "project_structure.md": "docs / architecture/",
            "MULTI_REPO_STRUCTURE.md": "docs / architecture/",
            "PATHLIB_MIGRATION.md": "docs / architecture/",

            # Migration artifacts
            "legacy_bridge.py": "archive / migration/",
            "migration_report.md": "archive / migration/",
        },

        # Files to delete (deprecated / obsolete)
        "delete_files": [
            # Empty or redundant directories can be cleaned up later
        ],

        # Files to keep in root
        "keep_in_root": [
            "run.py",
            "pyproject.toml",
            "pytest.ini",
            "README.md",
            ".gitignore",
            "requirements.txt",
            ".env.linux",
            ".env"
        ]
    }

    return cleanup_plan


def execute_cleanup(plan, dry_run=True):
    """Execute the cleanup plan."""
    actionprefix = "🔍 [DRY RUN]" if dry_run else "🧹 [EXECUTING]"

    print(f"\n{action_prefix} CLEANUP OPERATIONS")
    print("=" * 60)

    # Create directories
    print("\n📁 Creating organization directories...")
    for directory in plan["create_directories"]:
        dir_path = Path(directory)
        print(f"  Creating: {directory}")
        if not dry_run:
            dir_path.mkdir(parents=True, exist_ok=True)

    # Move files
    print("\n📦 Moving files to organized locations...")
    for source, destination in plan["move_operations"].items():
        sourcepath = Path(source)
        destpath = Path(destination) / source

        if source_path.exists():
            print(f"  Moving: {source} → {destination}")
            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(dest_path))
        else:
            print(f"  ⚠️ Not found: {source}")

    # Delete files
    if plan["delete_files"]:
        print("\n🗑️ Deleting obsolete files...")
        for file_path in plan["delete_files"]:
            print(f"  Deleting: {file_path}")
            if not dry_run:
                Path(file_path).unlink(missing_ok=True)

    return True


def create_root_readme():
    """Create a clean root directory README."""
    readme_content = '''# Charlie Reporting System

A modern microservices - based reporting system for processing CSV data and generating Excel reports.

## 🚀 Quick Start

```bash  # Run the main application
python3 run.py

# Run tests across all services
python3 scripts / test_runner.py

# Start development services
python3 scripts / start_dev_services.py
```

## 📁 Project Structure

```
├── services/              # Microservices
│   ├── report_generator/   # CSV processing & Excel generation
│   ├── email - service/      # Email processing
│   ├── outlook - relay/      # Outlook integration
│   ├── database - service/   # Data persistence
│   └── scheduler - service/  # Task scheduling
│
├── shared/                # Shared utilities & libraries
│   ├── config_manager.py   # Configuration management
│   ├── logging_utils.py    # Logging utilities
│   └── tests/             # Shared test utilities
│
├── scripts/               # Management & utility scripts
│   ├── test_runner.py     # Service test runner
│   └── start_dev_services.py
│
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── architecture/     # System architecture docs
│   └── migration/        # Migration guides
│
├── tools/                 # Development & setup tools
│   ├── setup/            # Environment setup scripts
│   └── development/      # Development utilities
│
├── archive/               # Historical & deprecated files
│   ├── migration/        # Migration artifacts
│   ├── deprecated/       # Deprecated code
│   └── debug/           # Debug scripts
│
├── config/               # Configuration files
├── demo/                 # Demo data & scripts
├── logs/                 # Application logs
└── legacy_backup/        # Backup of migrated code
```

## 🏗️ Architecture

This system follows a modern microservices architecture:

- **Report Generator Service**: Core CSV processing and Excel generation
- **Email Service**: Email fetching and processing
- **Outlook Relay**: Outlook / Exchange integration
- **Database Service**: Data persistence and retrieval
- **Scheduler Service**: Task scheduling and automation

## 🧪 Testing

```bash  # Run all tests
python3 scripts / test_runner.py

# Run tests for specific service
python3 scripts / test_runner.py --service report_generator

# Run specific test types
python3 scripts / test_runner.py --type unit
python3 scripts / test_runner.py --type integration
```

## 📚 Documentation

- [API Documentation](docs / api/)
- [Architecture Overview](docs / architecture/)
- [Migration Guide](docs / migration/)
- [Development Setup](tools / setup/)

## 🛠️ Development

See [tools / development/](tools / development/) for development setup and utilities.

## 📈 Status

✅ Phase 2 Complete - Microservices architecture fully implemented
✅ Legacy code migration completed
✅ Test suite reorganized into service - specific tests
✅ Root directory cleanup completed
'''

    return readme_content


def main():
    """Main cleanup function."""
    print("🧹 ROOT DIRECTORY CLEANUP UTILITY")
    print("=" * 50)

    # Analyze current structure
    categories = analyze_root_directory()

    # Create cleanup plan
    plan = create_cleanup_plan()

    # Show what will be done
    print("\n📋 CLEANUP PLAN SUMMARY")
    print("=" * 40)
    print(f"  📁 Directories to create: {len(plan['create_directories'])}")
    print(f"  📦 Files to move: {len(plan['move_operations'])}")
    print(f"  🗑️ Files to delete: {len(plan['delete_files'])}")
    print(f"  ✅ Files to keep in root: {len(plan['keep_in_root'])}")

    # Dry run first
    print("\n🔍 DRY RUN - Showing what would be done...")
    execute_cleanup(plan, dry_run=True)

    # Ask for confirmation
    response = input("\n❓ Execute cleanup? (y / N): ").strip().lower()

    if response == 'y':
        print("\n🧹 EXECUTING CLEANUP...")
        execute_cleanup(plan, dry_run=False)

        # Create new README
        newreadme = create_root_readme()
        readmepath = Path("README.md")

        # Backup existing README
        if readme_path.exists():
            backuppath = Path("archive / migration / README_old.md")
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(readme_path, backup_path)
            print(f"📄 Backed up existing README to {backup_path}")

        # Write new README
        readme_path.write_text(new_readme)
        print("📄 Created new organized README.md")

        print("\n🎉 ROOT DIRECTORY CLEANUP COMPLETE!")
        print("✅ Files organized into logical directories")
        print("✅ Deprecated files archived")
        print("✅ Clean project structure established")
        print("✅ New README.md created")

        return 0
    else:
        print("\n❌ Cleanup cancelled")
        return 1


if __name__ == "__main__":
    exit(main())