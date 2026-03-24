# Implementation Plan: Interactive Textbook Generation

**Branch**: `001-textbook-gen` | **Date**: 2026-03-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-textbook-gen/spec.md`

## Summary

Build an AI-native interactive textbook for Agentic AI in DevOps with 7 chapters + intro, RAG-powered chatbot, user authentication, content personalization by background level, and chapter quizzes. The system uses Docusaurus for the frontend textbook, FastAPI backend for API/chat endpoints, and integrates with Qdrant for vector search and Neon for database.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript/JavaScript (Docusaurus frontend)
**Primary Dependencies**: Docusaurus v3, FastAPI, Better-Auth, OpenAI Agents SDK, LiteLLM, sentence-transformers, Qdrant client, Prisma
**Storage**: Neon Postgres (user data, quiz results), Qdrant (vector embeddings)
**Testing**: pytest (backend), Docusaurus built-in testing
**Target Platform**: Web (Vercel frontend, Railway backend)
**Project Type**: Web application with separate frontend (Docusaurus) and backend (FastAPI)
**Performance Goals**: Page load <2s, chatbot response <5s, handle 1000 concurrent users
**Constraints**: Free tier infrastructure only (Vercel, Railway, Qdrant, Neon), no LangChain, no self-hosted models
**Scale/Scope**: Single textbook with ~15k words, ~200 vector chunks, estimated <1000 initial users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Mission-Driven Content | ✅ PASS | Textbook teaches Agentic AI in DevOps |
| II. Clean Repository Structure | ✅ PASS | Content in /projects folder per constitution |
| III. Pattern-Based Learning | ✅ PASS | Covers ReAct, Triage, Orchestrator patterns |
| IV. Free Tier Infrastructure First | ✅ PASS | Uses Vercel, Railway, Qdrant, Neon free tiers |
| V. Content Grounding (NON-NEGOTIABLE) | ✅ PASS | RAG must cite sources, no hallucinations |
| VI. Agent Skills Convention | ✅ PASS | Agents will follow SKILL.md pattern |

## Project Structure

### Documentation (this feature)

```text
specs/001-textbook-gen/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yaml     # REST API specification
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

Per Constitution Section II, all deployable content lives in `/projects`:

```text
projects/
├── website/                    # Docusaurus textbook (deployed to Vercel)
│   ├── docs/                   # Chapter MDX files
│   ├── src/
│   │   ├── components/        # Chat widget, quiz component
│   │   └── pages/              # Custom pages if needed
│   ├── docusaurus.config.js
│   └── sidebars.js
├── backend/                   # FastAPI backend (deployed to Railway)
│   ├── src/
│   │   ├── api/                # REST endpoints
│   │   ├── services/           # Business logic
│   │   ├── models/             # Pydantic models
│   │   └── rag/                # RAG pipeline
│   ├── tests/
│   └── requirements.txt
├── rag/                       # RAG service (can be part of backend)
│   └── [embedding, chunking logic]
└── agents/                    # Reusable agent skills
    ├── rag-chatbot/SKILL.md
    ├── quiz-generator/SKILL.md
    ├── summarizer/SKILL.md
    └── personalization/SKILL.md
```

**Structure Decision**: Web application with Docusaurus frontend (projects/website) and FastAPI backend (projects/backend). RAG functionality integrated into backend. All content under /projects per Constitution II.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitutional principles are satisfied.

## Phase 0: Research

### Research Tasks

Based on the technical context, the following research tasks are needed:

1. **Docusaurus v3 customization**: Research custom theming (violet accent), MDX components, and search integration (Algolia vs local).
2. **Better-Auth with Prisma**: Research integration with Neon Postgres, email/password provider setup.
3. **RAG pipeline best practices**: Research chunking strategies (512 tokens, 64 overlap), reranking approaches, and prompt engineering for citation.
4. **Content personalization**: Research server-side MDX personalization approaches in Docusaurus.
5. **Quiz generation**: Research AI-powered quiz generation from chapter content with caching.

### Research Findings

All technology choices are specified in the Constitution:
- Docusaurus v3 for frontend
- FastAPI Python 3.12 for backend
- Better-Auth for authentication
- OpenAI Agents SDK (NOT LangChain) per Constitution non-goals
- Gemini via LiteLLM for AI model
- MiniLM-L6-v2 for embeddings
- Qdrant Cloud for vector storage
- Neon Postgres with Prisma ORM

**Decision**: Use Constitution-specified stack directly - no NEEDS CLARIFICATION required.

## Phase 1: Design & Contracts

### Data Model

Key entities from spec:
- **Chapter**: id, title, slug, readingTime, summary, body, order
- **User**: id, email, passwordHash, background (enum: beginner, engineer, architect, manager), createdAt
- **Quiz**: id, chapterId, questions (JSON array), correctAnswers
- **QuizResult**: id, userId, chapterId, score, answers (JSON), completedAt
- **ChatMessage**: id, userId, question, answer, sources (JSON array), createdAt

### API Contracts

Endpoints needed:
- `GET /api/chapters` - List all chapters
- `GET /api/chapters/{slug}` - Get chapter content with personalization
- `POST /api/chat` - Send chat question, get answer with citations
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update background preference
- `GET /api/quiz/{chapterId}` - Get quiz for chapter
- `POST /api/quiz/{chapterId}` - Submit quiz answers
- `GET /api/quiz/results` - Get user's quiz results

### Quickstart

To run the project locally:
1. Set up environment variables (GEMINI_API_KEY, QDRANT_URL, DATABASE_URL, etc.)
2. Run `pip install -r requirements.txt` in backend
3. Run `npm install` in website
4. Start backend: `uvicorn main:app --reload`
5. Start frontend: `npm run start`
6. Access at http://localhost:3000 (frontend) and http://localhost:8000 (backend)