"""
User domain model.
Represents system users with roles and authentication.
"""

import re
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, ConfigDict


from typing import Optional
from datetime import datetime, timezone


class UserRole(Enum):
        """User role levels"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(Enum):
        """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
        """Domain model for system users"""

    # Required fields
    email: str
    username: str

    # Optional fields with defaults
    first_name: str = ""
    last_name: str = ""
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    last_login: Optional[datetime] = None
    id: UUID = Field(default_factory=uuid4)
        created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

        model_config = ConfigDict(
        # Allow arbitrary types for UUID
        arbitrary_types_allowed=True
    )

        @field_validator('email')
        @classmethod


    def validate_email(cls, v: str) -> str:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
            return v.lower()

        @field_validator('username')
        @classmethod


    def validate_username(cls, v: str) -> str:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError(
                'Username can only contain letters, numbers, and underscores'
            )
            return v.lower()

        @classmethod

    def _is_valid_email(cls, email: str) -> bool:
            """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

        @property

    def full_name(self) -> str:
            """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    @property

    def is_admin(self) -> bool:
            """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property

    def is_active(self) -> bool:
            """Check if user account is active"""
        return self.status == UserStatus.ACTIVE

    def update_last_login(self, login_time: Optional[datetime] = None) -> None:
            """Update last login timestamp"""
        if login_time is None:
            login_time = datetime.now(timezone.utc)
            self.last_login = login_time

    def activate(self) -> None:
            """Activate user account"""
        self.status = UserStatus.ACTIVE

    def deactivate(self) -> None:
            """Deactivate user account"""
        self.status = UserStatus.INACTIVE

    def suspend(self) -> None:
            """Suspend user account"""
        self.status = UserStatus.SUSPENDED

    def to_dict(self) -> dict:
            """Convert user to dictionary"""
        return {
            'id': str(self.id),
                'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'status': self.status.value,
            'last_login': (
                self.last_login.isoformat() if self.last_login else None
                ),
                'created_at': self.created_at.isoformat()
            }

    @classmethod

    def from_dict(cls, data: dict) -> 'User':
            """Create user from dictionary"""
        user_data = data.copy()
            user_data['id'] = UUID(user_data['id'])
            user_data['created_at'] = datetime.fromisoformat(
            user_data['created_at']
        )
            if user_data.get('last_login'):
                user_data['last_login'] = datetime.fromisoformat(
                user_data['last_login']
            )
            user_data['role'] = UserRole(user_data['role'])
            user_data['status'] = UserStatus(user_data['status'])
            return cls(**user_data)

        def __eq__(self, other) -> bool:
            """Check equality based on ID"""
        if not isinstance(other, User):
                return False
        return self.id == other.id

    def __repr__(self) -> str:
            return (f"User(id={self.id}, username='{self.username}', "
                f"email='{self.email}')")
