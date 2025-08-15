"""setup_project_environment.py
---------------------------
One - time setup script to configure the project environment properly.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT

LEGACY NOTICE: This script is noisy (prints, undefined vars) and will be moved to tools/legacy/ and excluded from strict lint/type passes. No functional edits yet.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Set up the project environment."""
    print("Charlie Reporting - Project Environment Setup")
    print("=" * 50)

    project_root = Path(__file__).parent
    venvpath = project_root / ".venv"

    # Check if virtual environment exists
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Creating virtual environment...")

        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return 1
    else:
        print("✅ Virtual environment found")

    # Get Python executable path
    if os.name == 'nt':  # Windows
        pythonexe = venv_path / "Scripts" / "python.exe"
        pipexe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix / Linux / Mac
        pythonexe = venv_path / "bin" / "python"
        pipexe = venv_path / "bin" / "pip"

    if not python_exe.exists():
        print(f"❌ Python executable not found: {python_exe}")
        return 1

    print(f"✅ Python executable: {python_exe}")

    # Install / upgrade pip
    print("Upgrading pip...")
    try:
        subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Pip upgrade failed: {e}")

    # Install requirements
    requirementsfile = project_root / "requirements.txt"
    if requirements_file.exists():
        print("Installing requirements...")
        try:
            subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
            print("✅ Requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Requirements installation failed: {e}")
            return 1
    else:
        print("⚠️ requirements.txt not found, installing essential packages...")
        essentialpackages = ["pandas", "toml", "pywin32"]
        try:
            subprocess.run([str(pip_exe), "install"] + essential_packages, check=True)
            print("✅ Essential packages installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Essential packages installation failed: {e}")
            return 1

    # Verify VS Code settings
    vscodedir = project_root / ".vscode"
    if vscode_dir.exists():
        print("✅ VS Code configuration found")

        settingsfile = vscode_dir / "settings.json"
        if settings_file.exists():
            print("✅ VS Code settings.json found")
        else:
            print("⚠️ VS Code settings.json missing")

        tasksfile = vscode_dir / "tasks.json"
        if tasks_file.exists():
            print("✅ VS Code tasks.json found")
        else:
            print("⚠️ VS Code tasks.json missing")

        launchfile = vscode_dir / "launch.json"
        if launch_file.exists():
            print("✅ VS Code launch.json found")
        else:
            print("⚠️ VS Code launch.json missing")
    else:
        print("⚠️ VS Code configuration directory missing")

    # Verify .env file
    envfile = project_root / ".env"
    if env_file.exists():
        print("✅ Environment file (.env) found")
    else:
        print("⚠️ Environment file (.env) missing")

    # Test Python environment
    print("\nTesting Python environment...")
    try:
        result = subprocess.run([
            str(python_exe), "-c",
            "import sys; import pandas; import toml; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ready')"
        ], capture_output=True, text=True, check=True)
        print(f"✅ {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Python environment test failed: {e}")
        print(f"stderr: {e.stderr}")
        return 1

    # Check Windows - specific dependencies
    if os.name == 'nt':
        try:
            result = subprocess.run([
                str(python_exe), "-c",
                "import win32com.client; print('Windows COM interface available')"
            ], capture_output=True, text=True, check=True)
            print(f"✅ {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("⚠️ Windows COM interface not available (pywin32 may need reinstallation)")

    print("\n" + "=" * 50)
    print("Project Environment Setup Complete!")
    print("\nNext steps:")
    print("1. Set your email passwords in environment variables:")
    print("   $env:INTEGRATIONTEST_EMAIL_PASSWORD = 'your_password'")
    print("   $env:INTEGRATIONTEST_APP_PASSWORD = 'your_app_password'")
    print("\n2. Run integration tests:")
    print("   Use VS Code Command Palette: 'Tasks: Run Task' -> 'Run Integration Tests'")
    print("   Or run: .venv\\Scripts\\python.exe tests\\run_integration_tests.py")
    print("\n3. Use VS Code with configured environment:")
    print("   - F5 to debug")
    print("   - Ctrl + Shift + P -> 'Python: Select Interpreter' (should auto - select .venv)")
    print("   - Terminal will auto - activate virtual environment")

    return 0


if __name__ == '__main__':
    sys.exit(main())