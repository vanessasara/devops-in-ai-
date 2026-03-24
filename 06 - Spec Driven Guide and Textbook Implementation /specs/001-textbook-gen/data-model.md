# Data Model: Interactive Textbook Generation

## Entities

### Chapter
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| slug | string | URL-friendly identifier (e.g., "intro", "core-building-blocks") |
| title | string | Chapter title |
| order | integer | Chapter ordering (0=intro, 1-7=chapters) |
| readingTime | integer | Estimated reading time in minutes |
| summary | string | 3-5 bullet summary (AI-generated) |
| body | text | MDX content |
| tags | string[] | Topic tags |
| createdAt | timestamp | Creation timestamp |
| updatedAt | timestamp | Last update timestamp |

### User
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | string | User email (unique) |
| passwordHash | string | Bcrypt hashed password |
| background | enum | beginner, engineer, architect, manager |
| createdAt | timestamp | Account creation timestamp |
| updatedAt | timestamp | Last profile update |

### Quiz
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| chapterId | UUID | Foreign key to Chapter |
| questions | json | Array of {id, question, options[], correctIndex} |
| reflectionPrompt | string | Open-ended reflection question |
| generatedAt | timestamp | When quiz was generated |

### QuizResult
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| userId | UUID | Foreign key to User |
| chapterId | UUID | Foreign key to Chapter |
| quizId | UUID | Foreign key to Quiz |
| answers | json | Array of {questionId, selectedIndex} |
| score | integer | Number correct (0-4) |
| completedAt | timestamp | Submission timestamp |

### ChatMessage
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| userId | UUID | Foreign key to User (nullable for anonymous) |
| question | text | User's question |
| answer | text | AI's answer |
| sources | json | Array of {chapterSlug, sectionTitle, chunkText} |
| createdAt | timestamp | Message timestamp |

## Relationships

```
Chapter 1───* Quiz
User 1───* QuizResult
User 1───* ChatMessage
Chapter 1───* QuizResult
Chapter 1───* ChatMessage
```

## Validation Rules

- Chapter.slug: unique, lowercase, hyphens allowed, max 50 chars
- User.email: valid email format, unique
- User.password: min 8 characters
- User.background: must be one of enum values
- Quiz.questions: exactly 4 questions per quiz
- QuizResult.score: 0-4 integer
- ChatMessage.sources: array of objects with chapterSlug, sectionTitle

## State Transitions

- User: created → active (after email verification - optional for v1)
- QuizResult: created → completed (after submission)
- No complex state machines needed for this feature