#!/usr/bin/env python3
"""
Startup script for the Database Service API
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add database service to path
db_service_path = Path(__file__).parent
sys.path.insert(0, str(db_service_path))


def main():
    """Start the FastAPI server"""
    try:
        from src.interfaces.rest.main import create_app
        import uvicorn
        
        # Create the FastAPI app
        app = create_app()
        
        print("🚀 Starting Database Service API...")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🏥 Health Check: http://localhost:8000/health")
        print("⏹️  Press Ctrl+C to stop")
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Set to True for development
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
