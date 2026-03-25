"""
User Profile API Endpoints
Interactive Textbook - Agentic AI in DevOps

Endpoints for user profile management (GET/PUT /api/user/profile).
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from ..models.entities import UserProfile, UpdateProfileRequest, Background
from ..middleware.auth import require_auth
from ..auth.prisma_adapter import auth_adapter

router = APIRouter()


@router.get("/user/profile", response_model=UserProfile)
async def get_profile(user: dict = Depends(require_auth)):
    """
    Get the current user's profile.

    Args:
        user: Authenticated user from JWT token

    Returns:
        UserProfile with id, email, and background

    Raises:
        HTTPException: 401 if not authenticated
    """
    # Get full user data from database
    db_user = await auth_adapter.get_user_by_id(user["id"])

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return UserProfile(
        id=db_user["id"],
        email=db_user["email"],
        background=Background(db_user["background"]),
    )


@router.put("/user/profile", response_model=UserProfile)
async def update_profile(
    request: UpdateProfileRequest,
    user: dict = Depends(require_auth),
):
    """
    Update the user's background preference.

    Args:
        request: UpdateProfileRequest with new background
        user: Authenticated user from JWT token

    Returns:
        Updated UserProfile

    Raises:
        HTTPException: 401 if not authenticated, 404 if user not found
    """
    # Update user background in database
    updated_user = await auth_adapter.update_user_background(
        user_id=user["id"],
        background=request.background.value,
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return UserProfile(
        id=updated_user["id"],
        email=updated_user["email"],
        background=Background(updated_user["background"]),
    )


__all__ = ["router"]