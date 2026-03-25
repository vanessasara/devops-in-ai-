"""
FastAPI Backend for Interactive Textbook
Agentic AI in DevOps
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Agentic AI in DevOps - API",
    description="Backend API for interactive textbook with RAG-powered chatbot",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {"message": "Agentic AI in DevOps API", "version": "1.0.0"}


# Include routers
from .api import health_router
from .api.chapters import router as chapters_router
from .api.chat import router as chat_router
from .api.auth import router as auth_router

app.include_router(health_router, tags=["System"])
app.include_router(chapters_router, prefix="/api", tags=["Chapters"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(auth_router, prefix="/api", tags=["Auth"])

from .api.profile import router as profile_router
from .api.quiz import router as quiz_router

app.include_router(profile_router, prefix="/api", tags=["User"])
app.include_router(quiz_router, prefix="/api", tags=["Quiz"])

__all__ = ["app"]