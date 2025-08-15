#!/bin/bash
# setup_wsl2_dev.sh
# Setup script for WSL2 development environment

set -e

echo "🐧 Charlie Reporting - WSL2 Development Environment Setup"
echo "========================================================="

# Check if we're in WSL
if ! grep -q microsoft /proc/version; then
    echo "❌ This script is designed for WSL2 environment"
    echo "Please run this inside WSL2"
    exit 1
fi

echo "✅ WSL2 environment detected"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python 3.11 and development tools
echo "🐍 Installing Python 3.11 and development tools..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    build-essential \
    git \
    curl \
    wget \
    vim

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️ Virtual environment already exists, skipping creation"
else
    python3.11 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "📦 Installing Python packages..."
pip install pandas toml python-dotenv

# Install email libraries for cross-platform support
echo "📧 Installing email libraries..."
pip install imaplib2

# Try to install exchangelib (for Office 365)
echo "📧 Installing Exchange Web Services support..."
pip install exchangelib || echo "⚠️ exchangelib installation failed (optional)"

# Install additional packages from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, skipping"
fi

# Set up environment variables
echo "🔧 Setting up environment variables..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
# Charlie Reporting System Environment Variables - WSL2 Version

# Integration Test Configuration (WSL2/Linux)
INTEGRATION_TEST_SENDER_EMAIL=jwardwell7077@gmail.com
INTEGRATION_TEST_RECEIVER_EMAIL=jontajon191@gmail.com
# INTEGRATION_TEST_EMAIL_PASSWORD=your_gmail_password_here
# INTEGRATION_TEST_APP_PASSWORD=your_app_specific_password_here
INTEGRATION_TESTS_ENABLED=true
INTEGRATION_TEST_SMTP_SERVER=smtp.gmail.com
INTEGRATION_TEST_SMTP_PORT=587
INTEGRATION_TEST_TIMEOUT=300

# Force IMAP email checker for WSL2
EMAIL_CHECKER_PLATFORM=imap

# Python Environment Configuration
PYTHONPATH=./src:./tests

# Debug Settings
DEBUG=true
LOG_LEVEL=DEBUG

# WSL2-specific settings
WSL_DISTRO_NAME=$(lsb_release -si)
WSL_VERSION=2
EOL
    echo "✅ Created .env file with WSL2 defaults"
else
    echo "✅ .env file already exists"
fi

# Create WSL2-specific activation script
cat > activate_wsl2.sh << 'EOL'
#!/bin/bash
# WSL2 activation script

# Activate virtual environment
source .venv/bin/activate

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded from .env"
fi

# Set Python path
export PYTHONPATH="$(pwd)/src:$(pwd)/tests"

echo "🐧 WSL2 Development Environment Ready!"
echo "Python: $(python --version)"
echo "Virtual Environment: $VIRTUAL_ENV"
echo "PYTHONPATH: $PYTHONPATH"
echo ""
echo "To run integration tests:"
echo "  python tests/run_integration_tests.py"
echo ""
echo "To check dependencies:"
echo "  python tests/check_integration_dependencies.py"
EOL

chmod +x activate_wsl2.sh

# Create VS Code settings for WSL2
mkdir -p .vscode
cat > .vscode/settings_wsl2.json << 'EOL'
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
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
        "PYTHONPATH": "${workspaceFolder}/src:${workspaceFolder}/tests"
    },
    "files.associations": {
        "*.toml": "toml"
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true
}
EOL

echo "✅ Created VS Code settings for WSL2"

# Test the environment
echo "🧪 Testing Python environment..."
python << 'EOL'
import sys
import platform

print(f"✅ Python {sys.version}")
print(f"✅ Platform: {platform.system()} {platform.release()}")

try:
    import pandas
    print("✅ pandas available")
except ImportError:
    print("❌ pandas not available")

try:
    import toml
    print("✅ toml available")
except ImportError:
    print("❌ toml not available")

try:
    import imaplib
    print("✅ imaplib available (email verification)")
except ImportError:
    print("❌ imaplib not available")

print("\n🎯 WSL2 environment setup complete!")
EOL

echo ""
echo "========================================================="
echo "🎉 WSL2 Development Environment Setup Complete!"
echo "========================================================="
echo ""
echo "Next steps:"
echo "1. Set your email passwords:"
echo "   export INTEGRATION_TEST_EMAIL_PASSWORD='your_password'"
echo "   export INTEGRATION_TEST_APP_PASSWORD='your_app_password'"
echo ""
echo "2. Activate the environment:"
echo "   source activate_wsl2.sh"
echo ""
echo "3. Run integration tests:"
echo "   python tests/run_integration_tests.py"
echo ""
echo "4. To use VS Code with WSL2:"
echo "   - Open this folder in VS Code"
echo "   - Install 'Remote - WSL' extension"
echo "   - Use Ctrl+Shift+P -> 'Remote-WSL: Open Folder in WSL'"
echo ""
echo "📧 Email verification will use IMAP (Gmail compatible)"
echo "🔄 Conversion to Windows production is automated"
echo ""
