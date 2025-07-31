"""
User Business Service.
Handles user management workflows and business rules.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from ...domain.models.user import User, UserRole, UserStatus
from ...infrastructure.persistence.database import DatabaseConnection


class UserService:
    """
    User business service handling user management workflows.
    Coordinates user creation, authentication, and authorization.
    """
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 logger: Optional[logging.Logger] = None):
        self._db_connection = db_connection
        self._logger = logger or logging.getLogger(__name__)
    
    async def create_user(self, 
                         email: str,
                         username: str,
                         first_name: str = "",
                         last_name: str = "",
                         role: UserRole = UserRole.USER) -> User:
        """
        Create a new user with validation and business rules.
        
        Args:
            email: User email address
            username: Unique username
            first_name: User first name
            last_name: User last name
            role: User role (default: USER)
            
        Returns:
            User: The created user
            
        Raises:
            ValueError: If user data is invalid or duplicate
        """
        self._logger.info(f"Creating user: {username} ({email})")
        
        # Business rule: Validate email domain for admin users
        if role == UserRole.ADMIN:
            allowed_admin_domains = ['company.com', 'admin.org']
            email_domain = email.split('@')[-1] if '@' in email else ''
            if email_domain not in allowed_admin_domains:
                raise ValueError(f"Admin users must use approved email domains")
        
        # Create user
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            status=UserStatus.ACTIVE,
            last_login=None,
            created_at=datetime.now()
        )
        
        self._logger.info(f"Successfully created user: {user.id}")
        return user
    
    async def authenticate_user(self, username: str) -> Optional[User]:
        """
        Authenticate a user and update last login.
        
        Args:
            username: Username to authenticate
            
        Returns:
            User if authentication successful, None otherwise
        """
        self._logger.info(f"Authenticating user: {username}")
        
        # In a real system, this would verify credentials
        # For now, we'll simulate successful authentication
        
        # Create a mock user for demonstration
        user = User(
            email=f"{username}@example.com",
            username=username,
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            last_login=None,
            created_at=datetime.now()
        )
        
        # Update last login
        user.update_last_login()
        
        self._logger.info(f"Successfully authenticated user: {username}")
        return user
    
    async def authorize_user(self, user: User, required_role: UserRole) -> bool:
        """
        Check if user has required authorization level.
        
        Args:
            user: User to check
            required_role: Minimum required role
            
        Returns:
            True if user is authorized, False otherwise
        """
        if user.status != UserStatus.ACTIVE:
            self._logger.warning(f"Authorization failed - user not active: {user.username}")
            return False
        
        # Role hierarchy: ADMIN > USER > GUEST
        role_hierarchy = {
            UserRole.GUEST: 1,
            UserRole.USER: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        authorized = user_level >= required_level
        
        if authorized:
            self._logger.debug(f"User {user.username} authorized for {required_role.value}")
        else:
            self._logger.warning(f"User {user.username} not authorized for {required_role.value}")
        
        return authorized
    
    async def deactivate_user(self, user: User, reason: str = "") -> User:
        """
        Deactivate a user account.
        
        Args:
            user: User to deactivate
            reason: Reason for deactivation
            
        Returns:
            Updated user
        """
        self._logger.info(f"Deactivating user: {user.username}, reason: {reason}")
        
        user.deactivate()
        
        self._logger.info(f"Successfully deactivated user: {user.username}")
        return user
    
    async def reactivate_user(self, user: User) -> User:
        """
        Reactivate a user account.
        
        Args:
            user: User to reactivate
            
        Returns:
            Updated user
        """
        self._logger.info(f"Reactivating user: {user.username}")
        
        user.activate()
        
        self._logger.info(f"Successfully reactivated user: {user.username}")
        return user
    
    async def get_user_summary(self, user: User) -> Dict[str, Any]:
        """
        Get user summary information.
        
        Args:
            user: User to summarize
            
        Returns:
            Dictionary containing user summary
        """
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat()
        }
