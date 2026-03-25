"""
Auth API Endpoints
Interactive Textbook - Agentic AI in DevOps

Authentication endpoints for user signup and login.
"""

from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse

from ..models.entities import SignupRequest, LoginRequest, AuthResponse
from .better_auth import (
    hash_password,
    verify_password,
    create_jwt_token,
    get_auth_cookie_config,
)
from .prisma_adapter import auth_adapter

router = APIRouter()


@router.post("/auth/signup", response_model=AuthResponse, status_code=201)
async def signup(request: SignupRequest, response: Response):
    """
    Create a new user account.

    Args:
        request: Signup data with email and password
        response: FastAPI response object for setting cookies

    Returns:
        AuthResponse with success status

    Raises:
        HTTPException: 400 if email already exists or validation fails
    """
    # Validate email format
    if not request.email or "@" not in request.email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )

    # Validate password
    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )

    # Check if user already exists
    existing_user = await auth_adapter.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(request.password)

    # Create user
    user = await auth_adapter.create_user(
        email=request.email,
        password_hash=password_hash,
    )

    if not user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create account"
        )

    # Create JWT token
    token = create_jwt_token(
        user_id=user["id"],
        email=user["email"],
        background=user["background"],
    )

    # Set auth cookie
    cookie_config = get_auth_cookie_config()
    response.set_cookie(
        key=cookie_config["key"],
        value=token,
        httponly=cookie_config["httponly"],
        secure=cookie_config["secure"],
        samesite=cookie_config["samesite"],
        max_age=cookie_config["max_age"],
    )

    return AuthResponse(
        success=True,
        message="Account created successfully",
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response):
    """
    Login to an existing account.

    Args:
        request: Login data with email and password
        response: FastAPI response object for setting cookies

    Returns:
        AuthResponse with success status

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Get user by email
    user = await auth_adapter.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user["passwordHash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_jwt_token(
        user_id=user["id"],
        email=user["email"],
        background=user["background"],
    )

    # Set auth cookie
    cookie_config = get_auth_cookie_config()
    response.set_cookie(
        key=cookie_config["key"],
        value=token,
        httponly=cookie_config["httponly"],
        secure=cookie_config["secure"],
        samesite=cookie_config["samesite"],
        max_age=cookie_config["max_age"],
    )

    return AuthResponse(
        success=True,
        message="Login successful",
    )


@router.post("/auth/logout")
async def logout(response: Response):
    """
    Logout the current user.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        Success message
    """
    cookie_config = get_auth_cookie_config()
    response.delete_cookie(
        key=cookie_config["key"],
        httponly=cookie_config["httponly"],
        secure=cookie_config["secure"],
        samesite=cookie_config["samesite"],
    )

    return {"success": True, "message": "Logged out successfully"}


@router.get("/auth/session")
async def get_session(request: Request):
    """
    Get current session info.

    Args:
        request: FastAPI request object with cookies

    Returns:
        Session data if authenticated
    """
    from .better_auth import decode_jwt_token

    token = request.cookies.get(get_auth_cookie_config()["key"])
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    return {
        "authenticated": True,
        "user": {
            "id": payload["sub"],
            "email": payload["email"],
            "background": payload["background"],
        },
    }
