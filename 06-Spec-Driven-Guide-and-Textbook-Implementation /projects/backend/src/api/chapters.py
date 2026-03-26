"""
Chapters API Endpoints
Interactive Textbook - Agentic AI in DevOps
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from ..models.entities import ChapterSummary, Chapter, Background

router = APIRouter()


# Chapter data (will be loaded from database in production)
# This is the initial content structure
CHAPTERS_DATA = {
    "intro": {
        "slug": "intro",
        "title": "Introduction to Agentic AI",
        "order": 0,
        "reading_time": 10,
        "summary": [
            "Agentic AI represents a paradigm shift from static automation to dynamic, goal-driven systems",
            "Agents use tools, maintain context, and make decisions autonomously",
            "Key patterns include ReAct (Reason + Act), Triage, and Orchestration",
            "DevOps applications span CI/CD, incident response, and infrastructure management",
        ],
        "tags": ["introduction", "overview", "concepts"],
    },
    "core-building-blocks": {
        "slug": "core-building-blocks",
        "title": "Core Building Blocks of Agentic Systems",
        "order": 1,
        "reading_time": 15,
        "summary": [
            "Orchestrator agents coordinate multiple specialized agents",
            "Worker agents execute specific tasks with defined interfaces",
            "Memory systems maintain context across interactions",
            "Tool use enables agents to interact with external systems",
        ],
        "tags": ["architecture", "orchestration", "tools"],
    },
    "agent-patterns": {
        "slug": "agent-patterns",
        "title": "Agent Patterns for DevOps",
        "order": 2,
        "reading_time": 20,
        "summary": [
            "ReAct pattern combines reasoning with action selection",
            "Triage agents route requests to appropriate specialists",
            "Orchestrator patterns manage complex multi-step workflows",
            "Feedback loops enable continuous improvement",
        ],
        "tags": ["patterns", "react", "triage", "orchestration"],
    },
    "tool-use": {
        "slug": "tool-use",
        "title": "Tool Use and Integration",
        "order": 3,
        "reading_time": 18,
        "summary": [
            "Tools extend agent capabilities beyond text generation",
            "Common DevOps tools include kubectl, terraform, and CI/CD APIs",
            "Tool schemas define inputs, outputs, and constraints",
            "Error handling and retry logic are critical for reliability",
        ],
        "tags": ["tools", "integration", "apis"],
    },
    "implementation-overview": {
        "slug": "implementation-overview",
        "title": "Implementation Overview",
        "order": 4,
        "reading_time": 25,
        "summary": [
            "Implementation follows a phased approach: foundation, agents, integration",
            "Start with clear use cases and success metrics",
            "Choose between framework-based and custom implementations",
            "Testing and evaluation are essential for production readiness",
        ],
        "tags": ["implementation", "architecture", "deployment"],
    },
    "integration-strategies": {
        "slug": "integration-strategies",
        "title": "Integration Strategies",
        "order": 5,
        "reading_time": 22,
        "summary": [
            "API-first integration enables loose coupling with existing systems",
            "Event-driven architectures support real-time agent responses",
            "Hybrid approaches combine synchronous and asynchronous workflows",
            "Security considerations include authentication, authorization, and audit trails",
        ],
        "tags": ["integration", "apis", "events"],
    },
    "observability": {
        "slug": "observability",
        "title": "Observability for Agentic Systems",
        "order": 6,
        "reading_time": 20,
        "summary": [
            "Tracing tracks agent decision paths across tool calls",
            "Logging captures inputs, outputs, and intermediate states",
            "Metrics measure latency, token usage, and success rates",
            "Debugging tools help diagnose reasoning failures",
        ],
        "tags": ["observability", "tracing", "logging", "debugging"],
    },
    "scaling-patterns": {
        "slug": "scaling-patterns",
        "title": "Scaling Patterns",
        "order": 7,
        "reading_time": 18,
        "summary": [
            "Horizontal scaling distributes workload across agent instances",
            "Caching strategies reduce redundant LLM calls",
            "Queue-based architectures handle burst traffic",
            "Cost optimization balances performance with API expenses",
        ],
        "tags": ["scaling", "performance", "cost-optimization"],
    },
    "security-considerations": {
        "slug": "security-considerations",
        "title": "Security Considerations",
        "order": 8,
        "reading_time": 15,
        "summary": [
            "Prompt injection attacks can manipulate agent behavior",
            "Tool access controls limit the blast radius of compromised agents",
            "Audit trails provide accountability for autonomous actions",
            "Defense in depth combines multiple security layers",
        ],
        "tags": ["security", "prompt-injection", "audit"],
    },
}


@router.get("/chapters", response_model=List[ChapterSummary])
async def list_chapters():
    """
    List all chapters with summary information.

    Returns:
        List of chapter summaries ordered by chapter order.
    """
    chapters = [
        ChapterSummary(
            slug=data["slug"],
            title=data["title"],
            order=data["order"],
            reading_time=data["reading_time"],
        )
        for data in CHAPTERS_DATA.values()
    ]

    # Sort by order
    chapters.sort(key=lambda x: x.order)

    return chapters


@router.get("/chapters/{slug}", response_model=Chapter)
async def get_chapter(
    slug: str,
    background: Optional[Background] = Query(
        None,
        description="Content variant based on user background"
    ),
):
    """
    Get chapter content by slug.

    Args:
        slug: Chapter slug identifier
        background: Optional user background for content personalization

    Returns:
        Chapter with full content

    Raises:
        HTTPException: 404 if chapter not found
    """
    if slug not in CHAPTERS_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter not found: {slug}"
        )

    data = CHAPTERS_DATA[slug]

    # In production, load body from database or file system
    # For now, return placeholder content
    body = f"""
# {data['title']}

<div className="chapter-summary">
<strong>Key Takeaways:</strong>
<ul>
{chr(10).join(f'<li>{s}</li>' for s in data['summary'])}
</ul>
</div>

## Overview

This chapter covers the essential concepts of {data['title'].lower()} in the context of Agentic AI for DevOps.

## Key Concepts

{'Personalized for ' + background.value if background else 'Default (engineer) content'}

The content will be loaded from MDX files in the docs directory.

## Summary

{chr(10).join(f'- {s}' for s in data['summary'])}
"""

    chapter = Chapter(
        slug=data["slug"],
        title=data["title"],
        order=data["order"],
        reading_time=data["reading_time"],
        summary=data["summary"],
        body=body,
        tags=data["tags"],
    )

    return chapter


from ..services.summarizer import summarizer


@router.get("/chapters/{slug}/summary")
async def get_chapter_summary(
    slug: str,
    background: Optional[Background] = Query(
        None,
        description="Summary variant based on user background"
    ),
):
    """
    Get just the summary for a chapter.
    Generates summary using LLM if not already cached.

    Args:
        slug: Chapter slug identifier
        background: Optional user background for personalized summary

    Returns:
        Chapter summary and key terms
    """
    if slug not in CHAPTERS_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter not found: {slug}"
        )

    data = CHAPTERS_DATA[slug]
    
    # In a real implementation, we would load the MDX content here
    # For now, we use placeholder content to simulate the chapter text
    chapter_content = f"Content for {data['title']}. " + " ".join(data['summary'])

    # Generate personalized summary using the summarizer service
    summary_data = await summarizer.generate_summary(
        chapter_slug=slug,
        chapter_content=chapter_content,
        background=background.value if background else "engineer"
    )

    return {
        "slug": slug,
        "title": data["title"],
        "summary": summary_data["summary"],
        "keyTerms": summary_data.get("keyTerms", []),
        "reading_time": data["reading_time"],
    }