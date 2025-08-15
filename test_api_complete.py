"""Test script for database service API endpoints.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_api_creation():
    """Test that the API can be created successfully"""
    try:
        # Add the services directory to path for import
        services_path = os.path.join(os.path.dirname(__file__), 'services')
        if services_path not in sys.path:
            sys.path.insert(0, services_path)
        
        # Import using the hyphenated directory name
        sys.path.insert(0, os.path.join(services_path, 'database-service'))
        from src.interfaces.rest.main import create_app
        
        # Create the app
        app = create_app()
        
        # Check that it's a FastAPI instance
        from fastapi import FastAPI
        assert isinstance(app, FastAPI), (
            f"Expected FastAPI instance, got {type(app)}"
        )
        
        print("✅ API creation successful")
        return True
    except Exception as e:
        print(f"❌ Failed to create API: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🧪 Testing Database Service API...")
    success = test_api_creation()
    
    if success:
        print("\n✅ All tests passed! API is ready for deployment.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
    
    return success


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
