# Personalization Agent Skill

**Agent Type**: Content Adaptation | **Pattern**: Transform

## Purpose

Adapt textbook content based on user's background level to provide personalized learning experience.

## User Background Levels

| Level | Description | Content Adaptation |
|-------|-------------|-------------------|
| beginner | New to AI/DevOps | Simple language, explain terms, more context |
| engineer | Has DevOps experience | Code examples, implementation focus |
| architect | Senior technical | Design patterns, trade-offs, system thinking |
| manager | Leadership focus | Business value, ROI, team impact |

## Input

- `original_content`: Raw MDX content from chapter
- `user_background`: Target background level

## Output

- `personalized_content`: Adapted MDX content
- `adaptations_applied`: Array of changes made

## Adaptation Strategies

### For beginners
- Add explanations of technical terms in parentheses
- Add "What is X?" style context before introducing concepts
- Simplify complex sentences
- Add more examples

### For engineers
- Add code snippets where concepts apply
- Focus on implementation details
- Include API references
- Show integration patterns

### For architects
- Add trade-off analyses
- Include system design considerations
- Focus on scalability patterns
- Reference related patterns

### For managers
- Add business context
- Include ROI considerations
- Focus on team impact
- Add project planning notes

## Implementation Note

Instead of generating different content, use MDX components to conditionally show sections:
- `<Note type="beginner">` - Only shown to beginners
- `<CodeExample language="python">` - Shown to engineers/architects
- `<BusinessValue>` - Shown to managers

The personalization happens at render time based on user's background.