"""
Authentication System
Interactive Textbook - Agentic AI in DevOps

Custom auth implementation using Prisma Client Python, bcrypt, and JWT.
"""

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30


class AuthConfig(BaseModel):
    """Authentication configuration."""
    jwt_secret: str = JWT_SECRET
    jwt_algorithm: str = JWT_ALGORITHM
    jwt_expiration_days: int = JWT_EXPIRATION_DAYS
    cookie_name: str = "auth_token"
    cookie_secure: bool = os.getenv("NODE_ENV") == "production"
    cookie_http_only: bool = True
    cookie_same_site: str = "lax"


# Global config instance
auth_config = AuthConfig()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password
        hashed: Bcrypt hashed password

    Returns:
        True if password matches
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_jwt_token(user_id: str, email: str, background: str) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: User's UUID
        email: User's email
        background: User's background level

    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(days=auth_config.jwt_expiration_days)

    payload = {
        "sub": user_id,
        "email": email,
        "background": background,
        "exp": expiration,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    return jwt.encode(
        payload,
        auth_config.jwt_secret,
        algorithm=auth_config.jwt_algorithm
    )


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_auth_cookie_config() -> Dict[str, Any]:
    """
    Get cookie configuration for auth token.

    Returns:
        Cookie configuration dict
    """
    return {
        "key": auth_config.cookie_name,
        "httponly": auth_config.cookie_http_only,
        "secure": auth_config.cookie_secure,
        "samesite": auth_config.cookie_same_site,
        "max_age": auth_config.jwt_expiration_days * 24 * 60 * 60,
    }


__all__ = [
    "auth_config",
    "hash_password",
    "verify_password",
    "create_jwt_token",
    "decode_jwt_token",
    "get_auth_cookie_config",
]
