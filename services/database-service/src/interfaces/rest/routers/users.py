"""
User management endpoints for the database service API.
Provides CRUD operations for user records.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field

from ....domain.models.user import User, UserRole, UserStatus
from ....business.services.user_service import UserService

from uuid import UUID
from typing import Optional
from typing import List
router = APIRouter()


# Request/Response Models


class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    email: str = Field(..., description="User email address")
        username: str = Field(..., description="Username")
        first_name: Optional[str] = Field(None, description="First name")
        last_name: Optional[str] = Field(None, description="Last name")
        role: UserRole = Field(UserRole.USER, description="User role")


class UserUpdateRequest(BaseModel):
    """Request model for updating a user"""
    first_name: Optional[str] = Field(None, description="First name")
        last_name: Optional[str] = Field(None, description="Last name")
        role: Optional[UserRole] = Field(None, description="User role")
        status: Optional[UserStatus] = Field(None, description="User status")


class UserResponse(BaseModel):
    """Response model for user"""
    id: UUID
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    status: UserStatus
    full_name: str
    is_admin: bool
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

    @classmethod
    def from_domain(cls, user: User) -> 'UserResponse':
        """Convert domain model to response model"""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            full_name=user.full_name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
            )


# Dependency injection


    async def get_user_service(request: Request) -> UserService:
        """Dependency to get user service from app state"""
        return request.app.state.user_service


# Endpoints
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)


async def create_user(
        user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
        """Create a new user"""
    try:
        # Convert request to domain model
        user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )

            # Create via service (placeholder - implement when user service is ready)
            created_user = await user_service.create_user(user)

            return UserResponse.from_domain(created_user)

        except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
            )


@router.get("/", response_model=List[UserResponse])


async def list_users(
        status_filter: Optional[UserStatus] = (
            Query(None, description="Filter by status"),
        )
        role_filter: Optional[UserRole] = (
            Query(None, description="Filter by role"),
        )
        user_service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
        """Get list of users with optional filtering"""
    try:
        # Placeholder implementation
        users = await user_service.get_all_users()
            return [UserResponse.from_domain(user) for user in users]

        except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserResponse)


async def get_user(
        user_id: UUID,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
        """Get a specific user by ID"""
    try:
        user = await user_service.get_user_by_id(user_id)
            if not user:
            raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
            )

            return UserResponse.from_domain(user)

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/{user_id}", response_model=UserResponse)


async def update_user(
        user_id: UUID,
    user_data: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
        """Update an existing user"""
    try:
        updated_user = (
            await user_service.update_user(user_id, user_data.dict(exclude_unset=True))
            )
            if not updated_user:
            raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
            )

            return UserResponse.from_domain(updated_user)

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)


async def delete_user(
        user_id: UUID,
    user_service: UserService = Depends(get_user_service)
):
        """Delete a user"""
    try:
        success = await user_service.delete_user(user_id)
            if not success:
            raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
            )

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
