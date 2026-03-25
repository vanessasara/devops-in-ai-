"""
Health Check Endpoint
Interactive Textbook - Agentic AI in DevOps
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import time
import os

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime: float
    services: Dict[str, str]


# Track startup time
_startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for deployment verification.

    Returns:
        HealthResponse: Current health status and service availability
    """
    services = {}

    # Check database connectivity (will be implemented after Prisma setup)
    try:
        # Database check will be added when Prisma is configured
        services["database"] = "not_configured"
    except Exception as e:
        services["database"] = f"error: {str(e)}"

    # Check Qdrant (will be implemented)
    try:
        qdrant_url = os.getenv("QDRANT_URL")
        if qdrant_url:
            services["qdrant"] = "not_configured"
        else:
            services["qdrant"] = "not_configured"
    except Exception as e:
        services["qdrant"] = f"error: {str(e)}"

    # Check LLM configuration
    llm_key = os.getenv("LITELLM_API_KEY")
    services["llm"] = "configured" if llm_key else "not_configured"

    # Calculate uptime
    uptime = time.time() - _startup_time

    return HealthResponse(
        status="ok",
        version="1.0.0",
        uptime=round(uptime, 2),
        services=services
    )


@router.get("/health/live")
async def liveness():
    """Kubernetes liveness probe - is the app running?"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    """
    Kubernetes readiness probe - is the app ready to serve traffic?
    Checks critical dependencies.
    """
    # Check critical environment variables
    required_vars = ["DATABASE_URL", "LITELLM_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise HTTPException(
            status_code=503,
            detail=f"Missing required configuration: {', '.join(missing_vars)}"
        )

    return {"status": "ready"}