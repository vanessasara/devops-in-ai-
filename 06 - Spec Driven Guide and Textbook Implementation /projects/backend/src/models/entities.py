"""
Pydantic models for API entities
Interactive Textbook - Agentic AI in DevOps
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


# ====================
# Enums
# ====================

class Background(str, Enum):
    """User background levels for content personalization"""
    beginner = "beginner"
    engineer = "engineer"
    architect = "architect"
    manager = "manager"


# ====================
# Chapter Models
# ====================

class ChapterSummary(BaseModel):
    """Summary for chapter listing"""
    slug: str = Field(..., description="URL-friendly chapter identifier")
    title: str = Field(..., description="Chapter title")
    order: int = Field(..., description="Chapter ordering")
    reading_time: int = Field(..., alias="readingTime", description="Reading time in minutes")

    class Config:
        populate_by_name = True


class Chapter(ChapterSummary):
    """Full chapter content"""
    summary: List[str] = Field(default_factory=list, description="3-5 bullet summary")
    body: str = Field(..., description="Full MDX content")
    tags: List[str] = Field(default_factory=list, description="Topic tags")


# ====================
# Chat Models
# ====================

class Citation(BaseModel):
    """Citation for chatbot answer"""
    chapter_slug: str = Field(..., alias="chapterSlug", description="Chapter slug")
    section_title: str = Field(..., alias="sectionTitle", description="Section title")
    chunk_text: str = Field(..., alias="chunkText", description="Relevant text chunk")

    class Config:
        populate_by_name = True


class ChatRequest(BaseModel):
    """Chat question request"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's question")


class ChatResponse(BaseModel):
    """Chat answer with citations"""
    answer: str = Field(..., description="AI's grounded answer")
    sources: List[Citation] = Field(default_factory=list, description="Source citations")


# ====================
# Auth Models
# ====================

class SignupRequest(BaseModel):
    """User signup request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, max_length=128, description="User password")


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")


class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool = Field(..., description="Auth success status")
    message: Optional[str] = Field(None, description="Error message if failed")


# ====================
# User Profile Models
# ====================

class UserProfile(BaseModel):
    """User profile data"""
    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    background: Background = Field(..., description="User's background level")


class UpdateProfileRequest(BaseModel):
    """Profile update request"""
    background: Background = Field(..., description="New background level")


# ====================
# Quiz Models
# ====================

class QuizQuestion(BaseModel):
    """Single quiz question"""
    id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., min_length=2, description="Answer options")


class Quiz(BaseModel):
    """Quiz for a chapter"""
    chapter_slug: str = Field(..., alias="chapterSlug", description="Chapter slug")
    questions: List[QuizQuestion] = Field(..., description="Quiz questions")
    reflection_prompt: Optional[str] = Field(None, alias="reflectionPrompt", description="Reflection prompt")

    class Config:
        populate_by_name = True


class QuizAnswer(BaseModel):
    """Single answer submission"""
    question_id: str = Field(..., alias="questionId", description="Question ID")
    selected_index: int = Field(..., alias="selectedIndex", ge=0, description="Selected option index")

    class Config:
        populate_by_name = True


class SubmitQuizRequest(BaseModel):
    """Quiz submission request"""
    answers: List[QuizAnswer] = Field(..., description="Submitted answers")


class AnswerResult(BaseModel):
    """Result for a single answer"""
    question_id: str = Field(..., alias="questionId", description="Question ID")
    correct: bool = Field(..., description="Whether answer was correct")

    class Config:
        populate_by_name = True


class QuizResult(BaseModel):
    """Quiz submission result"""
    score: int = Field(..., ge=0, description="Number correct")
    total: int = Field(..., ge=1, description="Total questions")
    answers: List[AnswerResult] = Field(..., description="Per-question results")


class QuizResultSummary(BaseModel):
    """Summary of a quiz result for listing"""
    chapter_slug: str = Field(..., alias="chapterSlug", description="Chapter slug")
    score: int = Field(..., description="Score achieved")
    completed_at: datetime = Field(..., alias="completedAt", description="Completion time")

    class Config:
        populate_by_name = True


# ====================
# Health Check Models
# ====================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="ok", description="Health status")
    version: str = Field(default="1.0.0", description="API version")
    services: dict = Field(default_factory=dict, description="Service statuses")


# ====================
# Error Models
# ====================

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional details")