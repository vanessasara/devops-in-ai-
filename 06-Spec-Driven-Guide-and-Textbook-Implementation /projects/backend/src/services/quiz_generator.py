"""
Quiz Generator Service
Interactive Textbook - Agentic AI in DevOps

Generates multiple-choice quizzes from chapter content using LLM.
Supports background-based personalization for question difficulty.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class QuizGenerator:
    """
    Generate quizzes from chapter content.

    Uses LLM to create comprehension-testing questions with
    background-appropriate difficulty levels.
    """

    # Background-specific question guidance
    BACKGROUND_GUIDANCE = {
        "beginner": """Focus on definitions and basic concepts.
Use simple language. Questions should test understanding of fundamental ideas.
Example: "What is the primary role of an orchestrator agent?" """,

        "engineer": """Include technical details and implementation concepts.
Reference specific technologies and patterns where relevant.
Example: "Which pattern is used to handle tool failures in agent workflows?" """,

        "architect": """Focus on design patterns, trade-offs, and system design.
Questions should test understanding of architectural decisions.
Example: "What is a key trade-off when choosing between single-agent and multi-agent systems?" """,

        "manager": """Focus on business value, team considerations, and ROI.
Questions should relate to strategic and organizational aspects.
Example: "How does observability in agents impact team velocity?" """,
    }

    # System prompt for quiz generation
    QUIZ_SYSTEM_PROMPT = """You are an expert quiz creator for technical education.
Generate EXACTLY 4 multiple-choice questions from the provided chapter content.

CRITICAL REQUIREMENTS:
1. Questions must test COMPREHENSION, not just recall
2. Each question must have EXACTLY 4 options
3. Only ONE option is correct
4. Wrong options (distractors) should be PLAUSIBLE common misconceptions
5. Include a brief explanation for the correct answer
6. Include a reflection prompt that encourages application

{background_guidance}

OUTPUT FORMAT (valid JSON):
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctIndex": 0,
      "explanation": "Brief explanation of why this is correct."
    }}
  ],
  "reflectionPrompt": "How would you apply X concept to your work?"
}}

CHAPTER CONTENT:
{chapter_content}

Generate the quiz now as valid JSON only."""

    def __init__(self, model: str = None):
        """
        Initialize the quiz generator.

        Args:
            model: LLM model to use (defaults to env var or gemini)
        """
        self.model = model or os.getenv("LLM_MODEL", "gemini/gemini-pro")
        self._llm_client = None

    def _get_llm_client(self):
        """Get or create LLM client (lazy initialization)."""
        if self._llm_client is None:
            try:
                from litellm import completion
                self._llm_client = completion
            except ImportError:
                print("Warning: litellm not installed. Using placeholder quiz.")
                self._llm_client = None
        return self._llm_client

    async def generate_quiz(
        self,
        chapter_slug: str,
        chapter_content: str,
        background: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a quiz for a chapter.

        Args:
            chapter_slug: URL-friendly chapter identifier
            chapter_content: Full chapter text
            background: User's background level (beginner, engineer, architect, manager)

        Returns:
            Quiz dict with questions and metadata
        """
        # Get background guidance
        background_guidance = self.BACKGROUND_GUIDANCE.get(
            background or "engineer",
            self.BACKGROUND_GUIDANCE["engineer"]
        )

        # Build prompt
        prompt = self.QUIZ_SYSTEM_PROMPT.format(
            background_guidance=background_guidance,
            chapter_content=chapter_content[:8000],  # Limit content length
        )

        # Try to generate with LLM
        quiz_data = await self._generate_with_llm(prompt, chapter_slug)

        # Add metadata
        quiz_data["chapterSlug"] = chapter_slug
        quiz_data["generatedAt"] = datetime.utcnow().isoformat()

        return quiz_data

    async def _generate_with_llm(
        self,
        prompt: str,
        chapter_slug: str,
    ) -> Dict[str, Any]:
        """
        Generate quiz using LLM.

        Args:
            prompt: Full prompt for quiz generation
            chapter_slug: Chapter identifier for fallback

        Returns:
            Quiz data dict
        """
        llm_client = self._get_llm_client()

        if llm_client is None:
            # Return placeholder quiz
            return self._get_placeholder_quiz(chapter_slug)

        try:
            response = await llm_client(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a quiz generation assistant. Output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            # Parse JSON response
            content = response.choices[0].message.content
            quiz_data = json.loads(content)

            # Validate structure
            if "questions" not in quiz_data:
                raise ValueError("Missing 'questions' in response")

            # Ensure questions have correct structure
            for i, q in enumerate(quiz_data["questions"]):
                q["id"] = f"q{i+1}"
                if "correctIndex" not in q:
                    # Default to first option if missing
                    q["correctIndex"] = 0

            return quiz_data

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            return self._get_placeholder_quiz(chapter_slug)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._get_placeholder_quiz(chapter_slug)

    def _get_placeholder_quiz(self, chapter_slug: str) -> Dict[str, Any]:
        """
        Generate a placeholder quiz when LLM is unavailable.

        Args:
            chapter_slug: Chapter identifier

        Returns:
            Placeholder quiz dict
        """
        return {
            "questions": [
                {
                    "id": "q1",
                    "question": "What is the primary role of an orchestrator agent?",
                    "options": [
                        "Execute specific tasks directly",
                        "Coordinate multiple specialized agents",
                        "Store vector embeddings",
                        "Manage database connections"
                    ],
                    "correctIndex": 1,
                    "explanation": "Orchestrator agents coordinate multiple specialized agents to handle complex workflows."
                },
                {
                    "id": "q2",
                    "question": "Which pattern is commonly used for agent decision-making?",
                    "options": [
                        "MVC Pattern",
                        "ReAct Pattern",
                        "Factory Pattern",
                        "Singleton Pattern"
                    ],
                    "correctIndex": 1,
                    "explanation": "The ReAct (Reasoning + Acting) pattern is widely used for agent decision-making."
                },
                {
                    "id": "q3",
                    "question": "What is the purpose of tool use in AI agents?",
                    "options": [
                        "To store conversation history",
                        "To enable agents to perform external actions",
                        "To manage database connections",
                        "To handle user authentication"
                    ],
                    "correctIndex": 1,
                    "explanation": "Tool use allows agents to perform external actions like API calls, database queries, and file operations."
                },
                {
                    "id": "q4",
                    "question": "Why is observability important for AI agents?",
                    "options": [
                        "To reduce code complexity",
                        "To monitor agent behavior and debug issues",
                        "To improve response time",
                        "To decrease memory usage"
                    ],
                    "correctIndex": 1,
                    "explanation": "Observability helps monitor agent behavior, track decisions, and debug issues in production."
                }
            ],
            "reflectionPrompt": f"How would you apply the concepts from {chapter_slug} to automate a task in your DevOps workflow?"
        }

    def get_background_level(self, user_background: Optional[str]) -> str:
        """
        Normalize background level to valid value.

        Args:
            user_background: User's background preference

        Returns:
            Valid background level string
        """
        valid_backgrounds = ["beginner", "engineer", "architect", "manager"]
        if user_background and user_background.lower() in valid_backgrounds:
            return user_background.lower()
        return "engineer"  # Default


# Global instance
_quiz_generator: QuizGenerator = None


def get_quiz_generator() -> QuizGenerator:
    """Get or create the global quiz generator instance."""
    global _quiz_generator
    if _quiz_generator is None:
        _quiz_generator = QuizGenerator()
    return _quiz_generator


# Convenience export
quiz_generator = get_quiz_generator()