"""Users router (placeholder).

The previous merge produced an invalid file (indentation, duplicate
imports, partially written blocks). This cleaned version restores a
valid module while user management logic is developed.

All endpoints currently raise HTTP 501 to make the unfinished status
explicit without causing import errors elsewhere.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


class UserCreateRequest(BaseModel):
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    role: str = Field("user", description="Role (enum placeholder)")


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    role: str | None = Field(None)
    status: str | None = Field(None)


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    status: str


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(_: UserCreateRequest):  # pragma: no cover - stub
    raise HTTPException(status_code=501, detail="User creation not yet implemented")


@router.get("/", response_model=list[UserResponse])
async def list_users():  # pragma: no cover - stub
    raise HTTPException(status_code=501, detail="User listing not yet implemented")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):  # pragma: no cover - stub
    raise HTTPException(
        status_code=501, detail=f"Retrieving user {user_id} not yet implemented"
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, _: UserUpdateRequest):  # pragma: no cover - stub
    raise HTTPException(
        status_code=501, detail=f"Updating user {user_id} not yet implemented"
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID):  # pragma: no cover - stub
    raise HTTPException(
        status_code=501, detail=f"Deleting user {user_id} not yet implemented"
    )

