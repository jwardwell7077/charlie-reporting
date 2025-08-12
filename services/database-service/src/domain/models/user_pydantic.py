"""
User domain model.
Represents system users with roles and authentication (legacy Pydantic v1).
"""

import re
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timezone


class UserRole(Enum):
    """User role levels."""

    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    """Domain model for system users (Pydantic v1 variant)."""

    email: str
    username: str
    first_name: str = ""
    last_name: str = ""
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    last_login: Optional[datetime] = None
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:  # type: ignore
        arbitrary_types_allowed = True
        use_enum_values = True

    @validator("email")
    def validate_email(cls, v: str) -> str:  # noqa: D401
        if not v:
            raise ValueError("Email cannot be empty")
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v

    @validator("username")
    def validate_username(cls, v: str) -> str:  # noqa: D401
        if not v:
            raise ValueError("Username cannot be empty")
        return v

    @classmethod
    def _is_valid_email(cls, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def update_last_login(self, login_time: Optional[datetime] = None) -> None:
        if login_time is None:
            login_time = datetime.now(timezone.utc)
        self.last_login = login_time

    def activate(self) -> None:
        self.status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE

    def suspend(self) -> None:
        self.status = UserStatus.SUSPENDED

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value,
            "status": self.status.value,
            "last_login": (
                self.last_login.isoformat() if self.last_login else None
            ),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user_data = data.copy()
        user_data["id"] = UUID(user_data["id"])
        user_data["created_at"] = datetime.fromisoformat(
            user_data["created_at"]
        )
        if user_data.get("last_login"):
            user_data["last_login"] = datetime.fromisoformat(
                user_data["last_login"]
            )
        user_data["role"] = UserRole(user_data["role"])
        user_data["status"] = UserStatus(user_data["status"])
        return cls(**user_data)

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return isinstance(other, User) and self.id == other.id

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "User(id="
            f"{self.id}, username='{self.username}', email='{self.email}')"
        )
