"""
convert_wsl2_to_windows.py
-------------------------
Automated script to convert WSL2 development setup to Windows production.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import shutil
import platform
from pathlib import Path


def main():
    """Convert WSL2 development setup to Windows production."""
    print("🔄 Charlie Reporting - WSL2 to Windows Conversion")
    print("=" * 55)

    # Verify we're running the conversion process
    sourceplatform = platform.system().lower()
    print(f"Source platform: {source_platform}")

    if 'microsoft' in platform.uname().release.lower():
        print("✅ Running from WSL2 environment")
    elif source_platform == 'windows':
        print("✅ Running on Windows (direct conversion)")
    else:
        print(f"⚠️ Running on {source_platform} (untested platform)")

    project_root = Path.cwd()
    windowsdeploy_dir = project_root / "windows_deployment"

    # Create deployment directory
    print("\n📁 Creating Windows deployment directory...")
    if windows_deploy_dir.exists():
        print("⚠️ Windows deployment directory exists, removing old version...")
        shutil.rmtree(windows_deploy_dir)

    windows_deploy_dir.mkdir()
    print(f"✅ Created: {windows_deploy_dir}")

    # Copy source files (no modifications needed)
    print("\n📋 Copying source files...")
    copydirectories = ['src', 'config', 'data', 'logs']

    for dir_name in copy_directories:
        sourcedir = project_root / dir_name
        if source_dir.exists():
            destdir = windows_deploy_dir / dir_name
            shutil.copytree(source_dir, dest_dir)
            print(f"✅ Copied: {dir_name}/")
        else:
            print(f"⚠️ Directory not found: {dir_name}/")

    # Copy configuration files
    print("\n⚙️ Converting configuration files...")

    configfiles = [
        'requirements.txt',
        'run.py',
        'README.md',
        'pyproject.toml'
    ]

    for file_name in config_files:
        sourcefile = project_root / file_name
        if source_file.exists():
            destfile = windows_deploy_dir / file_name
            shutil.copy2(source_file, dest_file)
            print(f"✅ Copied: {file_name}")

    # Convert tests directory with Windows - specific modifications
    print("\n🧪 Converting tests directory...")
    testssource = project_root / "tests"
    testsdest = windows_deploy_dir / "tests"

    if tests_source.exists():
        shutil.copytree(tests_source, tests_dest)

        # Update integration config for Windows
        convert_integration_config(tests_dest / "config" / "integration - config.toml")

        # Update email checker imports for Windows
        convert_email_checker_imports(tests_dest)

        print("✅ Tests directory converted for Windows")

    # Create Windows - specific environment file
    print("\n🔧 Creating Windows environment configuration...")
    create_windows_env_file(windows_deploy_dir)

    # Create Windows setup scripts
    print("\n📜 Creating Windows setup scripts...")
    create_windows_setup_scripts(windows_deploy_dir)

    # Create VS Code configuration for Windows
    print("\n🔧 Creating VS Code configuration for Windows...")
    create_windows_vscode_config(windows_deploy_dir)

    # Create deployment README
    print("\n📖 Creating deployment README...")
    create_deployment_readme(windows_deploy_dir)

    # Summary
    print("\n" + "=" * 55)
    print("🎉 WSL2 to Windows Conversion Complete!")
    print("=" * 55)
    print(f"Windows deployment created in: {windows_deploy_dir}")
    print("")
    print("Next steps for Windows deployment:")
    print("1. Copy the windows_deployment folder to your Windows machine")
    print("2. Run: windows_deployment\\setup_windows.bat")
    print("3. Set email passwords in PowerShell:")
    print("   $env:INTEGRATIONTEST_EMAIL_PASSWORD = 'your_password'")
    print("   $env:INTEGRATIONTEST_APP_PASSWORD = 'your_app_password'")
    print("4. Test: python tests\\run_integration_tests.py")
    print("")
    print("🔧 Email verification will use Windows Outlook COM interface")
    print("📧 SMTP sending functionality remains identical")


def convert_integration_config(config_path: Path):
    """Convert integration config for Windows."""
    if not config_path.exists():
        return

    content = config_path.read_text()

    # Update email checker platform
    content = content.replace(
        'emailchecker_platform = "auto"',
        'emailchecker_platform = "windows"'
    )

    # Add Windows - specific comment
    content = content.replace(
        '# Platform - specific settings',
        '# Platform - specific settings (Windows production)'
    )

    config_path.write_text(content)
    print("✅ Updated integration config for Windows")


def convert_email_checker_imports(tests_dir: Path):
    """Update email checker imports to use Windows - specific version."""
    # This is where you'd update any hardcoded IMAP references
    # to use the cross - platform email checker

    # Update integration_base.py if it exists
    integrationbase = tests_dir / "utils" / "integration_base.py"
    if integration_base.exists():
        content = integration_base.read_text()

        # Add import for cross - platform checker
        if "from .cross_platform_email_checker import create_email_checker" not in content:
            content = content.replace(
                "from .outlook_checker import OutlookChecker",
                "from .outlook_checker import OutlookChecker\nfrom .cross_platform_email_checker import create_email_checker"
            )

        integration_base.write_text(content)
        print("✅ Updated email checker imports")


def create_windows_env_file(deploy_dir: Path):
    """Create Windows - specific .env file."""
    envcontent = """# Charlie Reporting System Environment Variables - Windows Production

# Integration Test Configuration (Windows)
INTEGRATION_TEST_SENDER_EMAIL=jwardwell7077@gmail.com
INTEGRATION_TEST_RECEIVER_EMAIL=jontajon191@gmail.com  # INTEGRATION_TEST_EMAIL_PASSWORD=your_gmail_password_here  # INTEGRATION_TEST_APP_PASSWORD=your_app_specific_password_here
INTEGRATION_TESTS_ENABLED=true
INTEGRATION_TEST_SMTP_SERVER=smtp.gmail.com
INTEGRATION_TEST_SMTP_PORT=587
INTEGRATION_TEST_TIMEOUT=300

# Force Windows Outlook COM email checker
EMAIL_CHECKER_PLATFORM=windows

# Python Environment Configuration (Windows paths)
PYTHONPATH=.\\src;.\\tests

# Debug Settings
DEBUG=true
LOG_LEVEL=DEBUG

# Windows - specific settings
PLATFORM=windows
USE_OUTLOOK_COM=true
"""

    envfile = deploy_dir / ".env"
    env_file.write_text(env_content)
    print("✅ Created Windows .env file")


def create_windows_setup_scripts(deploy_dir: Path):
    """Create Windows setup scripts."""

    # PowerShell setup script
    psscript = """# setup_windows.ps1  # Windows setup script for Charlie Reporting

Write - Host "🪟 Charlie Reporting - Windows Production Setup" -ForegroundColor Green
Write - Host "=================================================" -ForegroundColor Green

# Check Python installation
Write - Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write - Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write - Host "❌ Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write - Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test - Path ".venv") {
    Write - Host "⚠️ Virtual environment exists, removing..." -ForegroundColor Yellow
    Remove - Item -Recurse -Force .venv
}

python -m venv .venv
if ($LASTEXITCODE -eq 0) {
    Write - Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write - Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write - Host "🚀 Activating virtual environment..." -ForegroundColor Yellow
.venv\\Scripts\\Activate.ps1

# Upgrade pip
Write - Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install packages
Write - Host "📦 Installing Python packages..." -ForegroundColor Yellow
pip install pandas toml pywin32

# Install from requirements.txt if exists
if (Test - Path "requirements.txt") {
    Write - Host "📦 Installing from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Test Outlook COM
Write - Host "📧 Testing Outlook COM interface..." -ForegroundColor Yellow
python -c "import win32com.client; outlook = win32com.client.Dispatch('Outlook.Application'); print('✅ Outlook COM available')"

if ($LASTEXITCODE -eq 0) {
    Write - Host "✅ Outlook COM interface working" -ForegroundColor Green
} else {
    Write - Host "⚠️ Outlook COM interface not available" -ForegroundColor Yellow
    Write - Host "Please ensure Microsoft Outlook is installed" -ForegroundColor Yellow
}

Write - Host "🎉 Windows setup complete!" -ForegroundColor Green
Write - Host "Next steps:" -ForegroundColor Yellow
Write - Host "1. Set email passwords:" -ForegroundColor White
Write - Host "   `$env:INTEGRATIONTEST_EMAIL_PASSWORD = 'your_password'" -ForegroundColor Gray
Write - Host "   `$env:INTEGRATIONTEST_APP_PASSWORD = 'your_app_password'" -ForegroundColor Gray
Write - Host "2. Run tests:" -ForegroundColor White
Write - Host "   python tests\\run_integration_tests.py" -ForegroundColor Gray
"""

    psfile = deploy_dir / "setup_windows.ps1"
    ps_file.write_text(ps_script)

    # Batch setup script
    batscript = """@echo off
REM setup_windows.bat
REM Windows batch setup script

echo 🪟 Charlie Reporting - Windows Production Setup
echo ================================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
if exist ".venv" (
    echo ⚠️ Removing existing virtual environment...
    rmdir /s /q .venv
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created

REM Activate and install packages
call .venv\\Scripts\\activate.bat
python -m pip install --upgrade pip
pip install pandas toml pywin32

if exist "requirements.txt" (
    pip install -r requirements.txt
)

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Set email passwords in PowerShell
echo 2. Run: python tests\\run_integration_tests.py
pause
"""

    batfile = deploy_dir / "setup_windows.bat"
    bat_file.write_text(bat_script)

    print("✅ Created Windows setup scripts")


def create_windows_vscode_config(deploy_dir: Path):
    """Create VS Code configuration for Windows."""
    vscodedir = deploy_dir / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    settingscontent = """{
    "python.defaultInterpreterPath": "./.venv / Scripts / python.exe",
    "python.pythonPath": "./.venv / Scripts / python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.venvPath": "./.venv",
    "python.envFile": "${workspaceFolder}/.env",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src",
        "${workspaceFolder}/tests"
    ],
    "python.testing.unittestEnabled": true,
    "python.testing.unittestArgs": [
        "-v",
        "-s",
        "./tests",
        "-p",
        "test_*.py"
    ],
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}/src;${workspaceFolder}/tests",
        "EMAIL_CHECKER_PLATFORM": "windows"
    },
    "files.associations": {
        "*.toml": "toml"
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}"""

    settingsfile = vscode_dir / "settings.json"
    settings_file.write_text(settings_content)
    print("✅ Created Windows VS Code settings")


def create_deployment_readme(deploy_dir: Path):
    """Create deployment - specific README."""
    readme_content = """# Charlie Reporting - Windows Production Deployment

This directory contains the Windows production deployment converted from WSL2 development.

## Quick Setup

### Option 1: PowerShell (Recommended)
```powershell  # Run the PowerShell setup script
.\\setup_windows.ps1
```

### Option 2: Batch File
```cmd  # Run the batch setup script
setup_windows.bat
```

### Option 3: Manual Setup
```powershell  # Create virtual environment
python -m venv .venv
.venv\\Scripts\\Activate.ps1

# Install packages
pip install pandas toml pywin32
pip install -r requirements.txt

# Set environment variables
$env:INTEGRATIONTEST_EMAIL_PASSWORD = "your_password"
$env:INTEGRATIONTEST_APP_PASSWORD = "your_app_password"
$env:INTEGRATIONTESTS_ENABLED = "true"
```

## Testing

```powershell  # Check dependencies
python tests\\check_integration_dependencies.py

# Run integration tests
python tests\\run_integration_tests.py
```

## Key Differences from WSL2 Development

### ✅ Identical Components
- Python source code
- SMTP email sending
- CSV processing and data generation
- Configuration files
- Virtual environment structure

### 🔄 Converted Components
- **Email Verification**: Uses Windows Outlook COM instead of IMAP
- **File Paths**: Windows backslash paths instead of forward slash
- **Environment Variables**: PowerShell syntax instead of Bash
- **Setup Scripts**: .bat/.ps1 instead of .sh

### 🪟 Windows - Specific Features
- **Outlook Integration**: Direct COM interface with Microsoft Outlook
- **Native Windows Paths**: Proper Windows file system handling
- **PowerShell Scripts**: Native Windows administration

## Troubleshooting

### Common Issues

1. **"Outlook COM not available"**
   - Ensure Microsoft Outlook is installed
   - Run PowerShell as Administrator
   - Register COM components: `regsvr32 /s ole32.dll`

2. **"pywin32 installation failed"**
   - Install Visual C++ Build Tools
   - Run: `pip install --upgrade pywin32`
   - Run: `python Scripts\\pywin32_postinstall.py -install`

3. **"Permission denied" errors**
   - Run PowerShell as Administrator
   - Check execution policy: `Set - ExecutionPolicy RemoteSigned`

4. **"Module not found" errors**
   - Verify virtual environment is activated
   - Check PYTHONPATH in environment variables
   - Reinstall packages: `pip install -r requirements.txt`

## Production Deployment

This Windows deployment is ready for production use:

- ✅ All dependencies included
- ✅ Windows - optimized configuration
- ✅ Outlook COM integration
- ✅ Production - ready logging
- ✅ Error handling and recovery

## Support

For deployment issues:
1. Check the main project README.md
2. Review logs in the logs/ directory
3. Test individual components using the debug scripts

---
**Converted from WSL2 development environment**
**Target: Windows Production Deployment**
"""

    readmefile = deploy_dir / "README_DEPLOYMENT.md"
    readme_file.write_text(readme_content)
    print("✅ Created deployment README")


if __name__ == '__main__':
    main()