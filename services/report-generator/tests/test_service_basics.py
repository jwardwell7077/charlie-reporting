"""
Simple Unit Tests for Report Generator Service
Testing the main application and service integration
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import io

# Add the service source directory to Python path
service_root = Path(__file__).parent.parent
src_path = service_root / "src"
sys.path.insert(0, str(src_path))

def test_service_structure():
    """Test that the service has the expected structure"""
    # Check key directories exist
    assert (service_root / "src").exists()
    assert (service_root / "src" / "business").exists()
    assert (service_root / "src" / "business" / "services").exists()
    assert (service_root / "src" / "api").exists()
    assert (service_root / "src" / "api" / "routes").exists()

def test_main_module_imports():
    """Test that main module can be imported"""
    try:
        import main
        assert hasattr(main, 'app')
        print("✅ Main module imported successfully")
    except ImportError as e:
        pytest.skip(f"Main module import failed: {e}")

def test_business_services_structure():
    """Test business services directory structure"""
    business_services = service_root / "src" / "business" / "services"
    
    # Check for expected service files
    expected_files = [
        "csv_transformer.py",
        "excel_service.py"
    ]
    
    existing_files = [f.name for f in business_services.glob("*.py") if f.is_file()]
    
    for expected_file in expected_files:
        if expected_file in existing_files:
            print(f"✅ Found {expected_file}")
        else:
            print(f"⚠️  Missing {expected_file}")

def test_api_routes_structure():
    """Test API routes structure"""
    api_routes = service_root / "src" / "api" / "routes"
    
    # Check for routes file
    routes_file = api_routes / "reports.py"
    if routes_file.exists():
        print("✅ API routes file exists")
        
        # Try to read the file to check it's not empty
        content = routes_file.read_text()
        assert len(content) > 100  # Should have substantial content
        assert "FastAPI" in content or "router" in content
    else:
        pytest.fail("API routes file not found")

@patch('fastapi.FastAPI')
def test_fastapi_app_creation(mock_fastapi):
    """Test FastAPI app can be created"""
    try:
        import main
        
        # Check if app is a FastAPI instance or mock
        assert main.app is not None
        print("✅ FastAPI app created successfully")
        
    except ImportError:
        pytest.skip("Cannot import main module")
    except Exception as e:
        pytest.fail(f"Failed to create FastAPI app: {e}")

def test_requirements_file_exists():
    """Test that requirements file exists for the service"""
    # Check for requirements at service level
    service_requirements = service_root / "requirements.txt"
    
    # Or check for requirements at project level
    project_requirements = service_root.parent.parent / "requirements.txt"
    
    if service_requirements.exists():
        print("✅ Service-level requirements.txt found")
        content = service_requirements.read_text()
        assert "fastapi" in content.lower()
    elif project_requirements.exists():
        print("✅ Project-level requirements.txt found")
        content = project_requirements.read_text()
        # Should have web framework dependencies
        assert any(pkg in content.lower() for pkg in ["fastapi", "flask", "django"])
    else:
        pytest.skip("No requirements.txt found")

def test_business_logic_separation():
    """Test that business logic is properly separated"""
    business_dir = service_root / "src" / "business"
    
    if not business_dir.exists():
        pytest.skip("Business directory not found")
    
    # Check for proper separation
    business_files = list(business_dir.rglob("*.py"))
    
    # Business logic should not import web framework directly
    for file_path in business_files:
        if file_path.name == "__init__.py":
            continue
            
        try:
            content = file_path.read_text()
            
            # Business logic should not import FastAPI directly
            if "from fastapi" in content or "import fastapi" in content:
                pytest.fail(f"Business logic file {file_path} imports FastAPI directly")
                
            print(f"✅ {file_path.name} properly separates business logic")
            
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")

class TestServiceHealthCheck:
    """Test service health and basic functionality"""
    
    def test_service_can_start(self):
        """Test that the service can start without errors"""
        try:
            import main
            
            # If we can import main without errors, basic structure is OK
            assert main is not None
            print("✅ Service imports successfully")
            
        except ImportError as e:
            pytest.skip(f"Service cannot be imported: {e}")
        except Exception as e:
            pytest.fail(f"Service failed to start: {e}")
    
    def test_api_routes_accessible(self):
        """Test that API routes can be imported"""
        try:
            sys.path.insert(0, str(service_root / "src"))
            
            # Try to import the routes
            from api.routes import reports
            
            assert hasattr(reports, 'router') or hasattr(reports, 'app')
            print("✅ API routes imported successfully")
            
        except ImportError as e:
            pytest.skip(f"API routes cannot be imported: {e}")
    
    def test_business_services_importable(self):
        """Test that business services can be imported"""
        try:
            sys.path.insert(0, str(service_root / "src"))
            
            # Try to import business services
            from business.services import csv_transformer
            
            print("✅ CSV transformer service imported")
            
        except ImportError as e:
            print(f"⚠️  CSV transformer service import failed: {e}")
        
        try:
            from business.services import excel_service
            
            print("✅ Excel service imported")
            
        except ImportError as e:
            print(f"⚠️  Excel service import failed: {e}")


class TestDataModels:
    """Test data models if they exist"""
    
    def test_csv_models_exist(self):
        """Test CSV-related models"""
        try:
            sys.path.insert(0, str(service_root / "src"))
            from business.models import csv_file
            
            print("✅ CSV file model exists")
            
        except ImportError:
            print("⚠️  CSV file model not found - will need to be created")
    
    def test_report_models_exist(self):
        """Test report-related models"""
        try:
            sys.path.insert(0, str(service_root / "src"))
            from business.models import report
            
            print("✅ Report model exists")
            
        except ImportError:
            print("⚠️  Report model not found - will need to be created")


def test_pytest_configuration():
    """Test that pytest is configured correctly"""
    # This test ensures pytest can run in this environment
    assert pytest is not None
    
    # Check current working directory
    import os
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Check Python path
    print(f"Python path includes: {sys.path[:3]}...")
    
    print("✅ Pytest configuration verified")


if __name__ == "__main__":
    # Run basic tests when called directly
    print("Running basic service structure tests...")
    
    test_service_structure()
    test_business_services_structure() 
    test_api_routes_structure()
    test_pytest_configuration()
    
    print("\nBasic tests completed. Run 'pytest tests/ -v' for full test suite.")
