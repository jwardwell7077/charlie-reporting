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
