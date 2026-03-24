# Quiz Generator Agent Skill

**Agent Type**: Content Generation | **Pattern**: Template + AI

## Purpose

Generate 4-question multiple-choice quizzes from chapter content. Questions should test comprehension, not just recall.

## Input

- `chapter_content`: Full chapter text
- `chapter_slug`: URL-friendly chapter identifier
- `user_background`: Optional - beginner, engineer, architect, or manager

## Output

```json
{
  "chapterSlug": "core-building-blocks",
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
    }
  ],
  "reflectionPrompt": "How would you apply the ReAct pattern to automate a CI/CD pipeline?",
  "generatedAt": "2026-03-24T12:00:00Z"
}
```

## Question Quality Requirements

1. **Test comprehension** - Questions should require understanding, not just recall
2. **One correct answer** - Exactly one option should be clearly correct
3. **Plausible distractors** - Wrong answers should be plausible (common misconceptions)
4. **Background-appropriate** - Adjust difficulty based on user background:
   - **beginner**: Focus on definitions, basic concepts
   - **engineer**: Include code snippets, implementation details
   - **architect**: Focus on design patterns, trade-offs
   - **manager**: Focus on business value, team considerations

## Content Rules

- Generate EXACTLY 4 questions per chapter
- Use the chapter content only - don't generate questions from external knowledge
- Include a reflection prompt that encourages application of concepts

## Caching

- Store generated quizzes in database to avoid regeneration
- Cache key: `quiz:{chapter_slug}:{background}`
- Invalidate cache when chapter content updates