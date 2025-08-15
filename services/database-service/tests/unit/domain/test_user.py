"""Unit tests for User domain model.
Following TDD - these tests are written BEFORE implementation.
"""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from src.domain.models.user import User, UserRole, UserStatus


class TestUser:
    """Test User domain model"""
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "email": "user@example.com",
            "username": "testuser",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.USER,
            "status": UserStatus.ACTIVE
        }
    
    def test_user_creation_with_required_fields(self):
        """Test User creation with only required fields"""
        user = User(
            email="test@example.com",
            username="testuser"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == ""
        assert user.last_name == ""
        assert user.role == UserRole.USER
        assert user.status == UserStatus.ACTIVE
        assert isinstance(user.id, UUID)
        assert isinstance(user.created_at, datetime)
        assert user.last_login is None
    
    def test_user_creation_with_all_fields(self, sample_user_data):
        """Test User creation with all fields"""
        user = User(**sample_user_data)
        
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.role == sample_user_data["role"]
        assert user.status == sample_user_data["status"]
        assert isinstance(user.id, UUID)
    
    def test_user_id_is_unique(self, sample_user_data):
        """Test that each User gets a unique ID"""
        user1 = User(**sample_user_data)
        # Change email to avoid validation error for duplicate email
        sample_user_data["email"] = "user2@example.com"
        sample_user_data["username"] = "testuser2"
        user2 = User(**sample_user_data)
        
        assert user1.id != user2.id
        assert isinstance(user1.id, UUID)
        assert isinstance(user2.id, UUID)
    
    def test_user_validation_empty_email(self):
        """Test validation fails for empty email"""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            User(email="", username="testuser")
    
    def test_user_validation_invalid_email(self):
        """Test validation fails for invalid email format"""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(email="invalid-email", username="testuser")
    
    def test_user_validation_empty_username(self):
        """Test validation fails for empty username"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            User(email="test@example.com", username="")
    
    def test_user_full_name_property(self, sample_user_data):
        """Test full_name property"""
        user = User(**sample_user_data)
        expected_full_name = f"{sample_user_data['first_name']} {sample_user_data['last_name']}"
        
        assert user.full_name == expected_full_name
        
        # Test with empty names
        user_no_names = User(email="test@example.com", username="testuser")
        assert user_no_names.full_name == " "
    
    def test_user_is_admin_property(self, sample_user_data):
        """Test is_admin property"""
        # Regular user
        user = User(**sample_user_data)
        assert user.is_admin is False
        
        # Admin user
        sample_user_data["role"] = UserRole.ADMIN
        admin_user = User(**sample_user_data)
        assert admin_user.is_admin is True
        
        # Super admin user
        sample_user_data["role"] = UserRole.SUPER_ADMIN
        super_admin_user = User(**sample_user_data)
        assert super_admin_user.is_admin is True
    
    def test_user_is_active_property(self, sample_user_data):
        """Test is_active property"""
        # Active user
        user = User(**sample_user_data)
        assert user.is_active is True
        
        # Inactive user
        sample_user_data["status"] = UserStatus.INACTIVE
        inactive_user = User(**sample_user_data)
        assert inactive_user.is_active is False
        
        # Suspended user
        sample_user_data["status"] = UserStatus.SUSPENDED
        suspended_user = User(**sample_user_data)
        assert suspended_user.is_active is False
    
    def test_user_update_last_login(self, sample_user_data):
        """Test updating last login timestamp"""
        user = User(**sample_user_data)
        assert user.last_login is None
        
        login_time = datetime.now(UTC)
        user.update_last_login(login_time)
        
        assert user.last_login == login_time
    
    def test_user_update_last_login_defaults_to_now(self, sample_user_data):
        """Test updating last login defaults to current time"""
        user = User(**sample_user_data)
        before_update = datetime.now(UTC)
        
        user.update_last_login()
        
        after_update = datetime.now(UTC)
        assert before_update <= user.last_login <= after_update
    
    def test_user_activate(self, sample_user_data):
        """Test activating a user"""
        sample_user_data["status"] = UserStatus.INACTIVE
        user = User(**sample_user_data)
        
        user.activate()
        
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True
    
    def test_user_deactivate(self, sample_user_data):
        """Test deactivating a user"""
        user = User(**sample_user_data)
        
        user.deactivate()
        
        assert user.status == UserStatus.INACTIVE
        assert user.is_active is False
    
    def test_user_suspend(self, sample_user_data):
        """Test suspending a user"""
        user = User(**sample_user_data)
        
        user.suspend()
        
        assert user.status == UserStatus.SUSPENDED
        assert user.is_active is False
    
    def test_user_to_dict(self, sample_user_data):
        """Test User serialization to dictionary"""
        user = User(**sample_user_data)
        user_dict = user.to_dict()
        
        assert isinstance(user_dict, dict)
        assert user_dict["email"] == sample_user_data["email"]
        assert user_dict["username"] == sample_user_data["username"]
        assert user_dict["first_name"] == sample_user_data["first_name"]
        assert user_dict["last_name"] == sample_user_data["last_name"]
        assert user_dict["role"] == sample_user_data["role"].value
        assert user_dict["status"] == sample_user_data["status"].value
        assert "id" in user_dict
        assert "created_at" in user_dict
    
    def test_user_from_dict(self, sample_user_data):
        """Test User deserialization from dictionary"""
        user = User(**sample_user_data)
        user_dict = user.to_dict()
        
        recreated_user = User.from_dict(user_dict)
        
        assert recreated_user.id == user.id
        assert recreated_user.email == user.email
        assert recreated_user.username == user.username
        assert recreated_user.first_name == user.first_name
        assert recreated_user.last_name == user.last_name
        assert recreated_user.role == user.role
        assert recreated_user.status == user.status
        assert recreated_user.created_at == user.created_at
    
    def test_user_repr(self, sample_user_data):
        """Test User string representation"""
        user = User(**sample_user_data)
        repr_str = repr(user)
        
        assert "User" in repr_str
        assert sample_user_data["username"] in repr_str
        assert sample_user_data["email"] in repr_str
    
    def test_user_equality(self, sample_user_data):
        """Test User equality comparison"""
        user1 = User(**sample_user_data)
        sample_user_data["email"] = "user2@example.com"
        sample_user_data["username"] = "testuser2"
        user2 = User(**sample_user_data)
        
        # Different instances should not be equal (different IDs)
        assert user1 != user2
        
        # Same instance should be equal to itself
        assert user1 == user1
        
        # Users with same ID should be equal
        user2.id = user1.id
        assert user1 == user2


class TestUserRole:
    """Test UserRole enum"""
    
    def test_user_role_values(self):
        """Test UserRole enum values"""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.SUPER_ADMIN.value == "super_admin"
    
    def test_user_role_string_conversion(self):
        """Test UserRole string conversion"""
        assert str(UserRole.USER) == "UserRole.USER"
        assert UserRole.USER.value == "user"


class TestUserStatus:
    """Test UserStatus enum"""
    
    def test_user_status_values(self):
        """Test UserStatus enum values"""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.SUSPENDED.value == "suspended"
    
    def test_user_status_string_conversion(self):
        """Test UserStatus string conversion"""
        assert str(UserStatus.ACTIVE) == "UserStatus.ACTIVE"
        assert UserStatus.ACTIVE.value == "active"
