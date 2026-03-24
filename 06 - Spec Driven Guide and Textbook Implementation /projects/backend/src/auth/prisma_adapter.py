"""
Prisma Adapter for Authentication
Interactive Textbook - Agentic AI in DevOps

Database operations for user authentication using Prisma Client Python.
"""

from typing import Optional, Dict, Any, List
from prisma import Prisma
from prisma.enums import Background

# Initialize Prisma client
prisma = Prisma()


class PrismaAuthAdapter:
    """Adapter for auth operations using Prisma ORM."""

    @staticmethod
    async def connect():
        """Connect to the database."""
        await prisma.connect()

    @staticmethod
    async def disconnect():
        """Disconnect from the database."""
        await prisma.disconnect()

    @staticmethod
    async def create_user(
        email: str,
        password_hash: str,
        background: str = "engineer",
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user.

        Args:
            email: User's email address
            password_hash: Bcrypt hashed password
            background: User's background level

        Returns:
            Created user dict or None if failed
        """
        try:
            user = await prisma.user.create(
                data={
                    "email": email,
                    "passwordHash": password_hash,
                    "background": background,
                }
            )
            return {
                "id": str(user.id),
                "email": user.email,
                "background": user.background.value,
                "createdAt": user.createdAt.isoformat(),
            }
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email.

        Args:
            email: User's email address

        Returns:
            User dict or None if not found
        """
        try:
            user = await prisma.user.find_unique(
                where={"email": email}
            )
            if not user:
                return None
            return {
                "id": str(user.id),
                "email": user.email,
                "passwordHash": user.passwordHash,
                "background": user.background.value,
                "createdAt": user.createdAt.isoformat(),
                "updatedAt": user.updatedAt.isoformat(),
            }
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User's UUID

        Returns:
            User dict or None if not found
        """
        try:
            user = await prisma.user.find_unique(
                where={"id": user_id}
            )
            if not user:
                return None
            return {
                "id": str(user.id),
                "email": user.email,
                "background": user.background.value,
                "createdAt": user.createdAt.isoformat(),
                "updatedAt": user.updatedAt.isoformat(),
            }
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    @staticmethod
    async def update_user_background(
        user_id: str,
        background: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Update user's background preference.

        Args:
            user_id: User's UUID
            background: New background level

        Returns:
            Updated user dict or None if failed
        """
        try:
            user = await prisma.user.update(
                where={"id": user_id},
                data={"background": background}
            )
            return {
                "id": str(user.id),
                "email": user.email,
                "background": user.background.value,
                "updatedAt": user.updatedAt.isoformat(),
            }
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    @staticmethod
    async def create_session(
        user_id: str,
        token: str,
        expires_at: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a session (for database session strategy).
        Note: Currently using JWT, this is for future database session support.

        Args:
            user_id: User's UUID
            token: Session token
            expires_at: Expiration timestamp

        Returns:
            Session dict or None if failed
        """
        # For JWT-based auth, sessions are stored client-side
        # This method is for future database session support
        return {"token": token, "userId": user_id}

    @staticmethod
    async def delete_session(token: str) -> bool:
        """
        Delete a session.
        Note: For JWT, this is a no-op. Implement token blacklist for logout.

        Args:
            token: Session token to delete

        Returns:
            True if successful
        """
        # For JWT, implement token blacklist in Redis/memory for logout
        return True


# Global adapter instance
auth_adapter = PrismaAuthAdapter()

__all__ = ["auth_adapter", "PrismaAuthAdapter", "prisma"]
