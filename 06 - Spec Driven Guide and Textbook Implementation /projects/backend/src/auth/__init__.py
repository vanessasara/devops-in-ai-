"""
Authentication module using Better-Auth
Interactive Textbook - Agentic AI in DevOps
"""

from .better_auth import auth, get_session
from .prisma_adapter import PrismaAdapter

__all__ = ["auth", "get_session", "PrismaAdapter"]
