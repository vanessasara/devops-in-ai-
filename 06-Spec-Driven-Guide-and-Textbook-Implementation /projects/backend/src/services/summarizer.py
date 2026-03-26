"""
Summarizer Service
Interactive Textbook - Agentic AI in DevOps

Generates 3-5 bullet point summaries for chapter content using LLM.
Supports background-based personalization for summary depth.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class Summarizer:
    """
    Generate summaries from chapter content.

    Uses LLM to create concise, scannable overviews with
    background-appropriate depth and key terms.
    """

    # Background-specific summary guidance
    BACKGROUND_GUIDANCE = {
        "beginner": """Focus on what and why basics. Use simple language. 
Explain fundamental concepts clearly. Avoid overly technical jargon.""",

        "engineer": """Include technical details and implementation concepts. 
Reference specific technologies, patterns, and 'how-to' aspects relevant to builders.""",

        "architect": """Focus on design patterns, trade-offs, and system design. 
Highlight architectural implications and high-level decision factors.""",

        "manager": """Focus on business value, strategic impact, and ROI. 
Highlight how these concepts affect team velocity, cost, and organizational goals.""",
    }

    # System prompt for summary generation
    SUMMARY_SYSTEM_PROMPT = """You are an expert technical content summarizer.
Generate a concise summary of the provided chapter content.

CRITICAL REQUIREMENTS:
1. Provide EXACTLY 3-5 bullet points
2. Focus on the most important concepts and takeaways
3. Use a tone appropriate for the specified user background
4. Extract 2-4 key terms with brief (1-sentence) definitions

{background_guidance}

OUTPUT FORMAT (valid JSON):
{{
  "summary": [
    "Bullet point 1",
    "Bullet point 2",
    "Bullet point 3"
  ],
  "keyTerms": [
    {{"term": "Term Name", "definition": "Brief definition here"}}
  ]
}}

CHAPTER CONTENT:
{chapter_content}

Generate the summary now as valid JSON only."""

    def __init__(self, model: str = None):
        """
        Initialize the summarizer.

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
                print("Warning: litellm not installed. Using placeholder summary.")
                self._llm_client = None
        return self._llm_client

    async def generate_summary(
        self,
        chapter_slug: str,
        chapter_content: str,
        background: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a summary for a chapter.

        Args:
            chapter_slug: URL-friendly chapter identifier
            chapter_content: Full chapter text
            background: User's background level (beginner, engineer, architect, manager)

        Returns:
            Summary dict with bullets and key terms
        """
        # Get background guidance
        background_guidance = self.BACKGROUND_GUIDANCE.get(
            background or "engineer",
            self.BACKGROUND_GUIDANCE["engineer"]
        )

        # Build prompt
        prompt = self.SUMMARY_SYSTEM_PROMPT.format(
            background_guidance=background_guidance,
            chapter_content=chapter_content[:8000],  # Limit content length
        )

        # Try to generate with LLM
        summary_data = await self._generate_with_llm(prompt, chapter_slug)

        # Add metadata
        summary_data["chapterSlug"] = chapter_slug
        summary_data["generatedAt"] = datetime.utcnow().isoformat()

        return summary_data

    async def _generate_with_llm(
        self,
        prompt: str,
        chapter_slug: str,
    ) -> Dict[str, Any]:
        """
        Generate summary using LLM.

        Args:
            prompt: Full prompt for summary generation
            chapter_slug: Chapter identifier for fallback

        Returns:
            Summary data dict
        """
        llm_client = self._get_llm_client()

        if llm_client is None:
            # Return placeholder summary
            return self._get_placeholder_summary(chapter_slug)

        try:
            response = await llm_client(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content summarization assistant. Output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3, # Lower temperature for more factual summary
                max_tokens=1000,
            )

            # Parse JSON response
            content = response.choices[0].message.content
            summary_data = json.loads(content)

            # Validate structure
            if "summary" not in summary_data:
                raise ValueError("Missing 'summary' in response")

            return summary_data

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            return self._get_placeholder_summary(chapter_slug)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._get_placeholder_summary(chapter_slug)

    def _get_placeholder_summary(self, chapter_slug: str) -> Dict[str, Any]:
        """
        Generate a placeholder summary when LLM is unavailable.

        Args:
            chapter_slug: Chapter identifier

        Returns:
            Placeholder summary dict
        """
        # Mapping of slugs to basic summaries for fallback
        placeholders = {
            "intro": {
                "summary": [
                    "Agentic AI represents a shift from static automation to dynamic, goal-driven systems.",
                    "Agents utilize tools, maintain context, and make autonomous decisions to solve complex tasks.",
                    "Key implementation patterns include ReAct, Triage, and Orchestration."
                ],
                "keyTerms": [
                    {"term": "Agentic AI", "definition": "AI systems that can reason and take actions autonomously."},
                    {"term": "Orchestration", "definition": "The coordination of multiple agents to achieve a complex goal."}
                ]
            },
            "core-building-blocks": {
                "summary": [
                    "Orchestrator agents coordinate specialized worker agents to handle multi-step workflows.",
                    "Memory systems allow agents to maintain state and context across multiple interactions.",
                    "Tool use enables agents to interact with external APIs, databases, and infrastructure."
                ],
                "keyTerms": [
                    {"term": "Memory", "definition": "A system for storing and retrieving conversation history and context."},
                    {"term": "Tool Use", "definition": "The ability of an agent to call external functions and APIs."}
                ]
            }
        }
        
        return placeholders.get(chapter_slug, {
            "summary": [
                f"This chapter covers the essential concepts of {chapter_slug.replace('-', ' ')}.",
                "Key takeaways include understanding the architecture and implementation patterns.",
                "Practical examples demonstrate how to apply these concepts in a DevOps environment."
            ],
            "keyTerms": [
                {"term": "Architecture", "definition": "The structural design of the agentic system."},
                {"term": "DevOps", "definition": "A set of practices that combines software development and IT operations."}
            ]
        })


# Global instance
_summarizer: Summarizer = None


def get_summarizer() -> Summarizer:
    """Get or create the global summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer


# Convenience export
summarizer = get_summarizer()
