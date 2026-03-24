# Summarizer Agent Skill

**Agent Type**: Content Summarization | **Pattern**: Extract + Synthesize

## Purpose

Generate 3-5 bullet point summaries for each chapter. Summaries appear at the start of each chapter to provide an overview.

## Input

- `chapter_content`: Full chapter text
- `chapter_title`: Title of the chapter
- `user_background`: Optional - beginner, engineer, architect, or manager

## Output

```json
{
  "chapterSlug": "core-building-blocks",
  "summary": [
    "Orchestrator agents coordinate multiple specialized agents to handle complex workflows",
    "The ReAct pattern combines reasoning with action selection in a loop",
    "Triage agents route requests to appropriate specialist agents based on intent"
  ],
  "keyTerms": [
    {"term": "Orchestrator", "definition": "Agent that coordinates other agents"},
    {"term": "ReAct", "definition": "Reasoning + Action pattern"}
  ],
  "generatedAt": "2026-03-24T12:00:00Z"
}
```

## Summary Quality Requirements

1. **3-5 bullets** - Concise, scannable overview
2. **Most important concepts** - Focus on key takeaways, not details
3. **Background-appropriate** - Adjust depth:
   - **beginner**: Focus on what, why basics
   - **engineer**: Include how-to, code concepts
   - **architect**: Focus on patterns, trade-offs
   - **manager**: Focus on value, business impact

## Key Terms

- Include 2-4 key terms with brief definitions
- Terms should be highlighted in the chapter

## Caching

- Pre-generate and cache summaries during build time
- Store in database to avoid regeneration
- Cache key: `summary:{chapter_slug}:{background}`