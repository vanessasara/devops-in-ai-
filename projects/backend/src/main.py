"""
FastAPI Backend for Interactive Textbook
Agentic AI in DevOps
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Agentic AI in DevOps - API",
    description="Backend API for interactive textbook with RAG-powered chatbot",
    version="1.0.0",
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
    return {"message": "Agentic AI in DevOps API", "version": "1.0.0"}


# Health check endpoint (T009 will add proper health check)
@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Import and include routers (will be added in subsequent tasks)
# from .api import chapters, chat, auth, quiz, profile

__all__ = ["app"]