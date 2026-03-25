"""
Quiz API Endpoints
Interactive Textbook - Agentic AI in DevOps

Endpoints for chapter quizzes:
- GET /api/quiz/{slug}: Get quiz for a chapter
- POST /api/quiz/{slug}/submit: Submit quiz answers
- GET /api/quiz/results: Get user's quiz results
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import json

from ..models.entities import (
    Quiz,
    QuizQuestion,
    SubmitQuizRequest,
    QuizResult,
    AnswerResult,
    QuizResultSummary,
)
from ..middleware.auth import require_auth, get_current_user as optional_auth
from ..services.quiz_generator import get_quiz_generator
from ..auth.prisma_adapter import prisma

router = APIRouter()


async def get_chapter_content(chapter_slug: str) -> Optional[str]:
    """
    Get chapter content from database.

    Args:
        chapter_slug: Chapter identifier

    Returns:
        Chapter body content or None
    """
    try:
        chapter = await prisma.chapter.find_unique(
            where={"slug": chapter_slug}
        )
        if chapter:
            return chapter.body
        return None
    except Exception as e:
        print(f"Error fetching chapter: {e}")
        return None


async def get_or_generate_quiz(
    chapter_slug: str,
    background: str = "engineer",
) -> dict:
    """
    Get existing quiz or generate new one.

    Args:
        chapter_slug: Chapter identifier
        background: User's background level

    Returns:
        Quiz data dict
    """
    quiz_gen = get_quiz_generator()

    # Try to get cached quiz from database
    try:
        # Find chapter
        chapter = await prisma.chapter.find_unique(
            where={"slug": chapter_slug}
        )
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Try to find existing quiz
        existing_quiz = await prisma.quiz.find_first(
            where={"chapterId": chapter.id}
        )

        if existing_quiz:
            # Parse stored questions
            questions_data = existing_quiz.questions
            return {
                "chapterSlug": chapter_slug,
                "questions": questions_data,
                "reflectionPrompt": existing_quiz.reflectionPrompt,
            }
    except Exception as e:
        print(f"Database lookup failed, generating new quiz: {e}")

    # Get chapter content
    chapter_content = await get_chapter_content(chapter_slug)
    if not chapter_content:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter content not found for {chapter_slug}"
        )

    # Generate new quiz
    quiz_data = await quiz_gen.generate_quiz(
        chapter_slug=chapter_slug,
        chapter_content=chapter_content,
        background=background,
    )

    # Store in database for caching
    try:
        if chapter:
            await prisma.quiz.create(
                data={
                    "chapterId": chapter.id,
                    "questions": quiz_data["questions"],
                    "reflectionPrompt": quiz_data.get("reflectionPrompt"),
                }
            )
    except Exception as e:
        print(f"Failed to cache quiz: {e}")

    return quiz_data


@router.get("/quiz/{slug}", response_model=Quiz)
async def get_quiz(
    slug: str,
    user: Optional[dict] = Depends(optional_auth),
):
    """
    Get quiz for a chapter.

    Returns a quiz with 4 multiple-choice questions.
    Questions are personalized based on user's background level.

    Args:
        slug: Chapter slug
        user: Optional authenticated user (for personalization)

    Returns:
        Quiz with questions and reflection prompt

    Raises:
        HTTPException: 404 if chapter not found
    """
    # Get user's background for personalization
    background = "engineer"  # Default
    if user:
        background = user.get("background", "engineer")

    # Get or generate quiz
    quiz_data = await get_or_generate_quiz(slug, background)

    # Convert to response model
    questions = [
        QuizQuestion(
            id=q["id"],
            question=q["question"],
            options=q["options"],
        )
        for q in quiz_data["questions"]
    ]

    return Quiz(
        chapterSlug=slug,
        questions=questions,
        reflectionPrompt=quiz_data.get("reflectionPrompt"),
    )


@router.post("/quiz/{slug}/submit", response_model=QuizResult)
async def submit_quiz(
    slug: str,
    request: SubmitQuizRequest,
    user: dict = Depends(require_auth),
):
    """
    Submit quiz answers and get results.

    Args:
        slug: Chapter slug
        request: Submitted answers
        user: Authenticated user

    Returns:
        Quiz result with score and per-question results

    Raises:
        HTTPException: 401 if not authenticated, 404 if quiz not found
    """
    try:
        # Find chapter
        chapter = await prisma.chapter.find_unique(
            where={"slug": slug}
        )
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Get quiz with correct answers
        quiz = await prisma.quiz.find_first(
            where={"chapterId": chapter.id}
        )
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Get correct answers from stored quiz
        questions_data = quiz.questions
        correct_map = {q["id"]: q["correctIndex"] for q in questions_data}

        # Score answers
        correct_count = 0
        answer_results = []

        for answer in request.answers:
            correct_index = correct_map.get(answer.question_id)
            is_correct = correct_index is not None and answer.selected_index == correct_index
            if is_correct:
                correct_count += 1

            answer_results.append(
                AnswerResult(
                    questionId=answer.question_id,
                    correct=is_correct,
                )
            )

        # Store result in database
        try:
            await prisma.quizresult.create(
                data={
                    "userId": user["id"],
                    "chapterId": str(chapter.id),
                    "quizId": str(quiz.id),
                    "answers": [a.dict() for a in request.answers],
                    "score": correct_count,
                }
            )
        except Exception as e:
            # Unique constraint violation - user already took this quiz
            # Update existing result instead
            print(f"Quiz result exists, updating: {e}")
            await prisma.quizresult.update_many(
                where={
                    "userId": user["id"],
                    "chapterId": str(chapter.id),
                },
                data={
                    "score": correct_count,
                    "answers": [a.dict() for a in request.answers],
                }
            )

        return QuizResult(
            score=correct_count,
            total=len(questions_data),
            answers=answer_results,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting quiz: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit quiz"
        )


@router.get("/quiz/results", response_model=List[QuizResultSummary])
async def get_quiz_results(user: dict = Depends(require_auth)):
    """
    Get all quiz results for the current user.

    Args:
        user: Authenticated user

    Returns:
        List of quiz result summaries

    Raises:
        HTTPException: 401 if not authenticated
    """
    try:
        results = await prisma.quizresult.find_many(
            where={"userId": user["id"]},
            include={
                "chapter": True,
            },
            order_by={"completedAt": "desc"},
        )

        return [
            QuizResultSummary(
                chapterSlug=r.chapter.slug,
                score=r.score,
                completedAt=r.completedAt,
            )
            for r in results
        ]
    except Exception as e:
        print(f"Error fetching quiz results: {e}")
        return []


__all__ = ["router"]