"""
setup_complete_wsl2_workflow.py
-------------------------------
Complete automation for WSL2 development with Windows production conversion.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List

def main():
    """Setup complete WSL2 development workflow."""
    print("🐧 Charlie Reporting - Complete WSL2 Development Setup")
    print("=" * 60)
    
    # Detect environment
    if 'microsoft' in platform.uname().release.lower():
        print("✅ WSL2 environment detected")
        setup_wsl2_development()
    elif platform.system().lower() == 'windows':
        print("🪟 Windows environment detected")
        setup_windows_production()
    else:
        print(f"⚠️ Unknown environment: {platform.system()}")
        print("This script is designed for WSL2 and Windows")
        sys.exit(1)

def setup_wsl2_development():
    """Complete WSL2 development environment setup."""
    print("\n🔧 Setting up WSL2 development environment...")
    
    project_root = Path.cwd()
    
    # Run the WSL2 setup script
    wsl_setup_script = project_root / "setup_wsl2_dev.sh"
    if wsl_setup_script.exists():
        print("📜 Running WSL2 setup script...")
        result = subprocess.run(['bash', str(wsl_setup_script)], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ WSL2 setup script completed successfully")
        else:
            print(f"❌ WSL2 setup script failed: {result.stderr}")
            return
    else:
        print("⚠️ WSL2 setup script not found, performing manual setup...")
        manual_wsl2_setup(project_root)
    
    # Configure VS Code for WSL2
    setup_wsl2_vscode(project_root)
    
    # Test the environment
    test_wsl2_environment(project_root)
    
    # Show WSL2 development guide
    show_wsl2_guide()

def manual_wsl2_setup(project_root: Path):
    """Manual WSL2 setup if script is not available."""
    print("🔧 Performing manual WSL2 setup...")
    
    # Update system
    subprocess.run(['sudo', 'apt', 'update'], check=False)
    
    # Install Python 3.11
    subprocess.run(['sudo', 'apt', 'install', '-y', 'python3.11', 'python3.11-venv', 'python3-pip'], check=False)
    
    # Create virtual environment
    venv_path = project_root / ".venv"
    if venv_path.exists():
        subprocess.run(['rm', '-rf', str(venv_path)], check=False)
    
    subprocess.run(['python3.11', '-m', 'venv', str(venv_path)], check=True)
    
    # Install packages
    pip_path = venv_path / "bin" / "pip"
    subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([str(pip_path), 'install', 'pandas', 'toml'], check=True)
    
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], check=True)
    
    print("✅ Manual WSL2 setup completed")

def setup_wsl2_vscode(project_root: Path):
    """Setup VS Code configuration for WSL2."""
    print("🔧 Configuring VS Code for WSL2...")
    
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    # WSL2-specific settings
    settings_content = """{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.pythonPath": "./.venv/bin/python",
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
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}/src:${workspaceFolder}/tests",
        "EMAIL_CHECKER_PLATFORM": "imap"
    },
    "files.associations": {
        "*.toml": "toml"
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "remote.WSL.fileWatcher.polling": true,
    "files.watcherExclude": {
        "**/.git/**": true,
        "**/node_modules/**": true,
        "**/.venv/**": true,
        "**/venv/**": true
    }
}"""
    
    settings_file = vscode_dir / "settings.json"
    settings_file.write_text(settings_content)
    
    # Create tasks for WSL2
    tasks_content = """{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Integration Tests (WSL2)",
            "type": "shell",
            "command": "${workspaceFolder}/.venv/bin/python",
            "args": ["tests/run_integration_tests.py"],
            "group": {
                "kind": "test",
                "isDefault": true
            },
            "options": {
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}/src:${workspaceFolder}/tests",
                    "EMAIL_CHECKER_PLATFORM": "imap"
                }
            }
        },
        {
            "label": "Check Dependencies (WSL2)",
            "type": "shell", 
            "command": "${workspaceFolder}/.venv/bin/python",
            "args": ["tests/check_integration_dependencies.py"],
            "group": "test",
            "options": {
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}/src:${workspaceFolder}/tests"
                }
            }
        },
        {
            "label": "Run Application (WSL2)",
            "type": "shell",
            "command": "${workspaceFolder}/.venv/bin/python", 
            "args": ["run.py"],
            "group": "build",
            "options": {
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}/src"
                }
            }
        },
        {
            "label": "Convert to Windows",
            "type": "shell",
            "command": "${workspaceFolder}/.venv/bin/python",
            "args": ["convert_wsl2_to_windows.py"],
            "group": "build",
            "options": {
                "cwd": "${workspaceFolder}"
            }
        }
    ]
}"""
    
    tasks_file = vscode_dir / "tasks.json"
    tasks_file.write_text(tasks_content)
    
    print("✅ VS Code configured for WSL2")

def test_wsl2_environment(project_root: Path):
    """Test WSL2 development environment."""
    print("🧪 Testing WSL2 environment...")
    
    python_path = project_root / ".venv" / "bin" / "python"
    
    if not python_path.exists():
        print("❌ Virtual environment not found")
        return
    
    # Test Python version
    result = subprocess.run([str(python_path), '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Python: {result.stdout.strip()}")
    else:
        print("❌ Python test failed")
        return
    
    # Test package imports
    test_imports = ['pandas', 'toml', 'email', 'smtplib', 'imaplib']
    for package in test_imports:
        result = subprocess.run([str(python_path), '-c', f'import {package}; print("✅ {package}")'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ {package} import failed")
    
    # Test dependency checker
    dep_check_script = project_root / "tests" / "check_integration_dependencies.py"
    if dep_check_script.exists():
        print("🔍 Running dependency checker...")
        result = subprocess.run([str(python_path), str(dep_check_script)], 
                              capture_output=True, text=True, 
                              env={**os.environ, 'PYTHONPATH': f"{project_root}/src:{project_root}/tests"})
        if result.returncode == 0:
            print("✅ Dependency check passed")
        else:
            print(f"⚠️ Dependency check warnings: {result.stdout}")
    
    print("✅ WSL2 environment testing completed")

def setup_windows_production():
    """Setup Windows production environment (called from Windows)."""
    print("\n🪟 Setting up Windows production environment...")
    
    project_root = Path.cwd()
    
    # Check if we have a WSL2 conversion to work with
    windows_deploy_dir = project_root / "windows_deployment"
    if windows_deploy_dir.exists():
        print(f"✅ Found existing Windows deployment: {windows_deploy_dir}")
        os.chdir(windows_deploy_dir)
        run_windows_setup(windows_deploy_dir)
    else:
        print("⚠️ No Windows deployment found")
        print("Run this script from WSL2 first to create the deployment")

def run_windows_setup(deploy_dir: Path):
    """Run Windows setup scripts."""
    # Try PowerShell script first
    ps_script = deploy_dir / "setup_windows.ps1"
    if ps_script.exists():
        print("📜 Running PowerShell setup script...")
        result = subprocess.run(['powershell', '-File', str(ps_script)], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PowerShell setup completed")
            print(result.stdout)
        else:
            print(f"⚠️ PowerShell setup had issues: {result.stderr}")
            
            # Fallback to batch script
            bat_script = deploy_dir / "setup_windows.bat"
            if bat_script.exists():
                print("📜 Trying batch setup script...")
                subprocess.run([str(bat_script)], shell=True)

def show_wsl2_guide():
    """Show WSL2 development guide."""
    print("\n" + "=" * 60)
    print("🐧 WSL2 Development Environment Ready!")
    print("=" * 60)
    print("""
✅ DEVELOPMENT WORKFLOW:

1. 📝 Code in VS Code (WSL2 extension)
   - Open folder in WSL2: code .
   - Use integrated terminal for all commands
   - Python interpreter: ./.venv/bin/python

2. 🧪 Run tests:
   source .venv/bin/activate
   python tests/run_integration_tests.py

3. 🔄 Convert to Windows when ready:
   python convert_wsl2_to_windows.py

4. 📧 Email verification uses IMAP (cross-platform)
   - No Outlook dependency
   - Works with any email provider
   - Configure in tests/config/integration-config.toml

✅ ADVANTAGES OF WSL2 DEVELOPMENT:

- 🐧 Linux comfort zone for development
- 📦 Easy package management (apt)
- 🔧 Native Python/pip behavior
- 📧 Standard IMAP email handling
- 🚀 Fast file system operations
- 🔄 Easy Windows conversion

✅ CONVERSION TO WINDOWS:

- 🔄 Automated deployment creation
- 🪟 Windows-optimized configurations
- 📧 Outlook COM integration
- 📜 PowerShell setup scripts
- ✅ Production-ready deployment

Next steps:
1. Test the integration suite: python tests/run_integration_tests.py
2. When ready for Windows: python convert_wsl2_to_windows.py
3. Deploy to Windows and run setup_windows.ps1
    """)

if __name__ == '__main__':
    main()
