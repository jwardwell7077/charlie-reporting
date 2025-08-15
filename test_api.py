#!/usr/bin/env python3
"""Script to test run the database service API.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_api():
    """Test the API startup"""
    try:
        from services.database_service.src.interfaces.rest.main import create_app
        
        app = create_app()
        print("✅ API application created successfully")
        print(f"📝 API Title: {app.title}")
        print(f"📝 API Version: {app.version}")
        print("🚀 API is ready to run with: uvicorn main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create API application: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    sys.exit(0 if success else 1)
