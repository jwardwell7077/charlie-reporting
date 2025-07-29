"""
check_integration_dependencies.py
--------------------------------
Check and install dependencies required for integration tests.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import sys
import subprocess
import importlib
import logging
from typing import List, Tuple, Dict

def setup_logging():
    """Set up logging for dependency check."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('dependency_checker')

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """
    Check if a package is installed and importable.
    
    Args:
        package_name: Name of package for pip install
        import_name: Name to use for import (if different from package_name)
    
    Returns:
        Tuple[bool, str]: (is_available, error_message)
    """
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True, ""
    except ImportError as e:
        return False, str(e)

def install_package(package_name: str) -> bool:
    """
    Install a package using pip with the correct Python environment.
    
    Args:
        package_name: Name of package to install
    
    Returns:
        bool: True if installation successful
    """
    try:
        # Get the correct Python executable
        python_exe = get_python_executable()
        
        subprocess.check_call([
            python_exe, "-m", "pip", "install", package_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def get_python_executable():
    """Get the correct Python executable path for this environment."""
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment, use current executable
        return sys.executable
    
    # Check for .venv in project root
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    venv_python = project_root / '.venv' / 'Scripts' / 'python.exe'
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to current executable
    return sys.executable

def check_integration_dependencies() -> Dict[str, any]:
    """
    Check all dependencies required for integration tests.
    
    Returns:
        Dict: Status of dependency checks
    """
    logger = setup_logging()
    
    # Define required packages
    required_packages = [
        ("pandas", "pandas"),
        ("toml", "toml"),
        ("pywin32", "win32com.client"),
    ]
    
    # Standard library packages (should always be available)
    stdlib_packages = [
        ("os", "os"),
        ("unittest", "unittest"),
        ("logging", "logging"),
        ("time", "time"),
        ("pathlib", "pathlib"),
        ("datetime", "datetime"),
        ("smtplib", "smtplib"),
        ("email", "email"),
        ("tempfile", "tempfile"),
        ("shutil", "shutil"),
    ]
    
    results = {
        "required_packages": {},
        "stdlib_packages": {},
        "missing_packages": [],
        "installation_attempts": {},
        "overall_status": True
    }
    
    logger.info("Checking integration test dependencies...")
    
    # Check standard library packages
    logger.info("Checking standard library packages...")
    for package_name, import_name in stdlib_packages:
        is_available, error = check_package(package_name, import_name)
        results["stdlib_packages"][package_name] = {
            "available": is_available,
            "error": error
        }
        
        if is_available:
            logger.info(f"✓ {package_name}")
        else:
            logger.error(f"✗ {package_name}: {error}")
            results["overall_status"] = False
    
    # Check required packages
    logger.info("Checking required packages...")
    for package_name, import_name in required_packages:
        is_available, error = check_package(package_name, import_name)
        results["required_packages"][package_name] = {
            "available": is_available,
            "error": error
        }
        
        if is_available:
            logger.info(f"✓ {package_name}")
        else:
            logger.warning(f"✗ {package_name}: {error}")
            results["missing_packages"].append(package_name)
    
    return results

def install_missing_packages(missing_packages: List[str], auto_install: bool = False) -> Dict[str, bool]:
    """
    Install missing packages.
    
    Args:
        missing_packages: List of package names to install
        auto_install: If True, install without prompting
    
    Returns:
        Dict[str, bool]: Installation results
    """
    logger = logging.getLogger('dependency_checker')
    installation_results = {}
    
    if not missing_packages:
        logger.info("No missing packages to install.")
        return installation_results
    
    logger.info(f"Missing packages: {', '.join(missing_packages)}")
    
    if not auto_install:
        response = input("Do you want to install missing packages? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            logger.info("Package installation skipped by user.")
            return installation_results
    
    for package_name in missing_packages:
        logger.info(f"Installing {package_name}...")
        
        try:
            success = install_package(package_name)
            installation_results[package_name] = success
            
            if success:
                logger.info(f"✓ Successfully installed {package_name}")
                
                # Verify installation
                is_available, error = check_package(package_name)
                if is_available:
                    logger.info(f"✓ {package_name} import verified")
                else:
                    logger.warning(f"⚠ {package_name} installed but import failed: {error}")
            else:
                logger.error(f"✗ Failed to install {package_name}")
        
        except Exception as e:
            logger.error(f"✗ Error installing {package_name}: {e}")
            installation_results[package_name] = False
    
    return installation_results

def check_system_requirements() -> Dict[str, any]:
    """
    Check system-specific requirements.
    
    Returns:
        Dict: System requirements status
    """
    logger = logging.getLogger('dependency_checker')
    
    results = {
        "platform": sys.platform,
        "python_version": sys.version,
        "requirements_met": True,
        "warnings": []
    }
    
    logger.info("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 7):
        results["requirements_met"] = False
        results["warnings"].append(f"Python 3.7+ required, found {python_version.major}.{python_version.minor}")
        logger.error(f"✗ Python version too old: {python_version.major}.{python_version.minor}")
    else:
        logger.info(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check platform
    if sys.platform != "win32":
        results["warnings"].append(f"Integration tests designed for Windows, running on {sys.platform}")
        logger.warning(f"⚠ Platform: {sys.platform} (Windows recommended)")
    else:
        logger.info("✓ Platform: Windows")
    
    # Check for Outlook (Windows only)
    if sys.platform == "win32":
        try:
            import win32com.client
            outlook = win32com.client.Dispatch("Outlook.Application")
            outlook = None  # Release reference
            logger.info("✓ Microsoft Outlook available")
        except Exception as e:
            results["warnings"].append(f"Microsoft Outlook not available: {e}")
            logger.warning(f"⚠ Microsoft Outlook: {e}")
    
    return results

def generate_setup_instructions(dependency_results: Dict, system_results: Dict) -> str:
    """
    Generate setup instructions based on check results.
    
    Args:
        dependency_results: Results from dependency check
        system_results: Results from system check
    
    Returns:
        str: Setup instructions
    """
    instructions = []
    
    instructions.append("Integration Test Setup Instructions")
    instructions.append("=" * 50)
    
    # System requirements
    if not system_results["requirements_met"]:
        instructions.append("\n❌ CRITICAL SYSTEM ISSUES:")
        for warning in system_results["warnings"]:
            if "Python" in warning:
                instructions.append(f"  - {warning}")
                instructions.append("    Solution: Upgrade Python to 3.7 or later")
    
    # Missing packages
    if dependency_results["missing_packages"]:
        instructions.append("\n📦 MISSING PACKAGES:")
        for package in dependency_results["missing_packages"]:
            instructions.append(f"  - {package}")
        
        instructions.append("\nInstallation commands:")
        instructions.append("  pip install " + " ".join(dependency_results["missing_packages"]))
    
    # Environment variables
    instructions.append("\n🔐 REQUIRED ENVIRONMENT VARIABLES:")
    instructions.append("  $env:INTEGRATION_TEST_EMAIL_PASSWORD = 'your_email_password'")
    instructions.append("  $env:INTEGRATION_TEST_APP_PASSWORD = 'your_app_password'")
    instructions.append("  $env:INTEGRATION_TESTS_ENABLED = 'true'")
    
    # Configuration
    instructions.append("\n⚙️ CONFIGURATION SETUP:")
    instructions.append("  1. Edit tests/config/integration-config.toml")
    instructions.append("  2. Set integration_tests.enabled = true")
    instructions.append("  3. Configure email addresses")
    instructions.append("  4. Set SMTP settings")
    
    # System warnings
    if system_results["warnings"]:
        instructions.append("\n⚠️ SYSTEM WARNINGS:")
        for warning in system_results["warnings"]:
            instructions.append(f"  - {warning}")
    
    return "\n".join(instructions)

def main():
    """Main entry point for dependency checker."""
    print("Charlie Reporting - Integration Test Dependency Checker")
    print("=" * 60)
    
    # Check dependencies
    dependency_results = check_integration_dependencies()
    
    # Check system requirements
    system_results = check_system_requirements()
    
    # Install missing packages if any
    installation_results = {}
    if dependency_results["missing_packages"]:
        installation_results = install_missing_packages(
            dependency_results["missing_packages"],
            auto_install=False
        )
    
    # Generate and display setup instructions
    print("\n" + "=" * 60)
    instructions = generate_setup_instructions(dependency_results, system_results)
    print(instructions)
    
    # Final status
    print("\n" + "=" * 60)
    all_packages_available = (
        len(dependency_results["missing_packages"]) == 0 and
        dependency_results["overall_status"] and
        system_results["requirements_met"]
    )
    
    if all_packages_available:
        print("✅ All dependencies are satisfied!")
        print("You can now run integration tests.")
        return 0
    else:
        print("❌ Some dependencies need attention.")
        print("Please address the issues above before running integration tests.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
