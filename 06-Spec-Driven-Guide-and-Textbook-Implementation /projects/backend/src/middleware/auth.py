"""
Auth Middleware
Interactive Textbook - Agentic AI in DevOps

Authentication middleware for protecting routes and extracting user context.
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import uuid

from ..auth.better_auth import decode_jwt_token, get_auth_cookie_config

security = HTTPBearer(auto_error=False)


# In-memory fallback for session-less users (Phase 8: T047)
# Maps anonymous session IDs to user preferences
_anonymous_sessions: Dict[str, Dict[str, Any]] = {}


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from JWT token.

    Checks for token in:
    1. Authorization header (Bearer token)
    2. Auth cookie

    Args:
        request: FastAPI request object
        credentials: Optional Bearer token from Authorization header

    Returns:
        User dict if authenticated, None otherwise

    Raises:
        HTTPException: 401 if token is invalid (for protected routes)
    """
    token = None

    # Check Authorization header
    if credentials:
        token = credentials.credentials
    else:
        # Check auth cookie
        cookie_name = get_auth_cookie_config()["key"]
        token = request.cookies.get(cookie_name)

    if not token:
        return None

    # Decode and validate token
    payload = decode_jwt_token(token)
    if not payload:
        return None

    return {
        "id": payload["sub"],
        "email": payload["email"],
        "background": payload["background"],
    }


async def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Require authentication for a route.

    Args:
        request: FastAPI request object
        credentials: Optional Bearer token

    Returns:
        User dict

    Raises:
        HTTPException: 401 if not authenticated
    """
    user = await get_current_user(request, credentials)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_anonymous_session(
    request: Request,
    response: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Get or create an anonymous session for users without cookies enabled.
    Implements Phase 8 requirement T047: Handle session-less users.

    Args:
        request: FastAPI request object
        response: Optional response object to set session header

    Returns:
        Anonymous session with preferences
    """
    # Try to get existing anonymous session ID from header
    session_id = request.headers.get("X-Anonymous-Session")

    if session_id and session_id in _anonymous_sessions:
        return _anonymous_sessions[session_id]

    # Create new anonymous session
    new_session_id = str(uuid.uuid4())
    session_data = {
        "id": new_session_id,
        "isAnonymous": True,
        "background": "engineer",  # Default background
    }

    _anonymous_sessions[new_session_id] = session_data

    # Set session ID in response header if response provided
    if response:
        response.headers["X-Anonymous-Session"] = new_session_id

    return session_data


async def get_user_or_anonymous(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Get authenticated user or create anonymous session.
    Useful for routes that work for both logged-in and anonymous users.

    Args:
        request: FastAPI request object
        credentials: Optional Bearer token

    Returns:
        User dict or anonymous session
    """
    user = await get_current_user(request, credentials)
    if user:
        return {**user, "isAnonymous": False}

    return await get_anonymous_session(request)


class AuthMiddleware:
    """
    Middleware to handle auth and add user context to requests.
    """

    async def __call__(self, request: Request, call_next):
        """
        Process request and add user context.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response with user context added
        """
        # Try to get user from token
        user = await get_current_user(request)

        # Add user to request state
        request.state.user = user

        # Continue processing
        response = await call_next(request)

        return response


# Dependency exports
require_user = require_auth
get_optional_user = get_current_user
get_any_user = get_user_or_anonymous

__all__ = [
    "get_current_user",
    "require_auth",
    "get_anonymous_session",
    "get_user_or_anonymous",
    "AuthMiddleware",
    "require_user",
    "get_optional_user",
    "get_any_user",
]
