"""User Business Service.
Handles user management workflows and business rules.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from ...domain.models.user import User, UserRole, UserStatus
from ...infrastructure.persistence.database import DatabaseConnection


class UserService:
    """User business service handling user management workflows.

    Coordinates user creation, authentication, and authorization.
    """

    def __init__(
        self,
        db_connection: DatabaseConnection,
        logger: logging.Logger | None = None,
    ):
        self._db_connection = db_connection
        self._logger = logger or logging.getLogger(__name__)
        self._users: dict[UUID, User] = {}

    async def create_user(
        self,
        email: str,
        username: str,
        first_name: str = "",
        last_name: str = "",
        role: UserRole = UserRole.USER,
    ) -> User:
        """Create a new user with validation and business rules."""
        self._logger.info("Creating user: %s (%s)", username, email)

        if role == UserRole.ADMIN:
            allowed_admin_domains = ["company.com", "admin.org"]
            email_domain = email.split("@")[-1] if "@" in email else ""
            if email_domain not in allowed_admin_domains:
                raise ValueError(
                    "Admin users must use an approved email domain"
                )

        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            status=UserStatus.ACTIVE,
            last_login=None,
            created_at=datetime.now(),
        )
        self._logger.info("Successfully created user: %s", user.id)
        self._users[user.id] = user
        return user

    async def authenticate_user(self, username: str) -> User | None:
        """Authenticate a user and update last login.

        This is a placeholder; real authentication would verify credentials.
        """
        self._logger.info("Authenticating user: %s", username)

        user = User(
            email=f"{username}@example.com",
            username=username,
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            last_login=None,
            created_at=datetime.now(),
        )
        user.update_last_login()
        self._logger.info("Successfully authenticated user: %s", username)
        return user

    async def authorize_user(
        self, user: User, required_role: UserRole
    ) -> bool:
        """Check if user has required authorization level."""
        if user.status != UserStatus.ACTIVE:
            self._logger.warning(
                "Authorization failed - user not active: %s", user.username
            )
            return False

        # Role hierarchy: SUPER_ADMIN > ADMIN > USER
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.ADMIN: 2,
            UserRole.SUPER_ADMIN: 3,
        }
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        authorized = user_level >= required_level

        if authorized:
            self._logger.debug(
                "User %s authorized for %s",
                user.username,
                required_role.value,
            )
        else:
            self._logger.warning(
                "User %s not authorized for %s",
                user.username,
                required_role.value,
            )
        return authorized

    async def deactivate_user(self, user: User, reason: str = "") -> User:
        """Deactivate a user account."""
        self._logger.info(
            "Deactivating user: %s, reason: %s", user.username, reason
        )
        user.deactivate()
        self._logger.info(
            "Successfully deactivated user: %s", user.username
        )
        return user

    async def reactivate_user(self, user: User) -> User:
        """Reactivate a user account."""
        self._logger.info("Reactivating user: %s", user.username)
        user.activate()
        self._logger.info(
            "Successfully reactivated user: %s", user.username
        )
        return user

    async def get_user_summary(self, user: User) -> dict[str, Any]:
        """Get user summary information."""
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat()
            if user.last_login
            else None,
            "created_at": user.created_at.isoformat(),
        }

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_all_users(self) -> list[User]:
        return list(self._users.values())

    async def update_user(
        self, user_id: UUID, data: dict[str, Any]
    ) -> User | None:
        user = self._users.get(user_id)
        if not user:
            return None
        for field, value in data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        return self._users.pop(user_id, None) is not None
