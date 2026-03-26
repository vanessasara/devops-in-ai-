# Tasks: Interactive Textbook Generation

**Feature**: 001-textbook-gen | **Feature Name**: Interactive Textbook Generation
**Generated**: 2026-03-24 | **Based On**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md)

## Implementation Strategy

**MVP Scope**: User Story 1 (Read Textbook Chapters) - the core reading experience
**Delivery**: Incremental by user story - each story is independently testable
**Parallel Opportunities**: Frontend/backend can be developed in parallel after foundational phase

## Phase 1: Setup

- [X] T001 Initialize projects/website/ with Docusaurus v3 in projects/website/
- [X] T002 Initialize projects/backend/ with FastAPI in projects/backend/
- [X] T003 Configure projects/agents/ directory structure in projects/agents/
- [X] T004 Set up .env.example files for both frontend and backend
- [X] T005 Create initial docusaurus.config.js with violet theme in projects/website/docusaurus.config.js

## Phase 2: Foundational

- [X] T006 Set up Prisma schema with all entities in projects/backend/prisma/schema.prisma
- [X] T007 Run initial database migration against Neon in projects/backend/
- [X] T008 Create Pydantic models for all API entities in projects/backend/src/models/
- [X] T009 Implement health check endpoint in projects/backend/src/api/health.py
- [X] T010 Create RAG indexing script for chapter content in projects/rag/indexer.py
- [X] T011 Set up Qdrant client and create collection in projects/backend/src/rag/qdrant_client.py

## Phase 3: User Story 1 - Read Textbook Chapters (P1)

**Goal**: Users can navigate and read all textbook chapters on any device
**Independent Test**: Load textbook, navigate chapters, verify mobile readability

- [X] T012 [P] [US1] Create chapter MDX files for all 7 chapters in projects/website/docs/
- [X] T013 [P] [US1] Configure docusaurus sidebars.js in projects/website/sidebars.js
- [X] T014 [US1] Implement GET /api/chapters endpoint in projects/backend/src/api/chapters.py
- [X] T015 [US1] Implement GET /api/chapters/{slug} endpoint in projects/backend/src/api/chapters.py
- [X] T016 [US1] Add prev/next navigation component in projects/website/src/components/PrevNext.js
- [X] T017 [US1] Create local search functionality in projects/website/
- [X] T018 [US1] Style Docusaurus with violet accent theme in projects/website/src/css/custom.css

## Phase 4: User Story 2 - Ask Chatbot Questions (P1)

**Goal**: Users can ask the AI chatbot questions that are answered only from textbook content
**Independent Test**: Ask questions, verify answers cite sources, verify out-of-scope questions are rejected

- [X] T019 [P] [US2] Create RAG retrieval function in projects/backend/src/rag/retriever.py
- [X] T020 [P] [US2] Implement embedding generation with MiniLM in projects/backend/src/rag/embeddings.py
- [X] T021 [US2] Create chat system prompt with grounding instructions in projects/agents/rag-chatbot/SKILL.md
- [X] T022 [US2] Implement POST /api/chat endpoint in projects/backend/src/api/chat.py
- [X] T023 [US2] Build chat widget component in projects/website/src/components/ChatWidget.js
- [X] T024 [US2] Add citation display and clickable links in projects/website/src/components/ChatMessage.js
- [X] T025 [US2] Test RAG returns citations for all in-scope questions in projects/backend/tests/

## Phase 5: User Story 3 - Create Account and Personalize (P2)

**Goal**: Users can create accounts and set background level to see personalized content
**Independent Test**: Sign up, log in, change background, verify content changes

- [X] T026 [P] [US3] Configure Better-Auth with email/password in projects/backend/src/auth/better_auth.py
- [X] T027 [P] [US3] Set up Prisma adapter for Better-Auth in projects/backend/src/auth/prisma_adapter.py
- [X] T028 [US3] Implement POST /api/auth/signup endpoint in projects/backend/src/api/auth.py
- [X] T029 [US3] Implement POST /api/auth/login endpoint in projects/backend/src/api/auth.py
- [X] T030 [US3] Add auth cookie handling middleware in projects/backend/src/middleware/auth.py
- [X] T031 [US3] Implement GET/PUT /api/user/profile endpoints in projects/backend/src/api/profile.py
- [X] T032 [US3] Create signup/login UI components in projects/website/src/components/AuthForms.js
- [X] T033 [US3] Create profile settings page in projects/website/src/pages/profile.js

## Phase 6: User Story 4 - Take Chapter Quizzes (P2)

**Goal**: Users can take quizzes at end of chapters and see their scores
**Independent Test**: Complete quiz, verify score, verify results persist

- [X] T034 [P] [US4] Create quiz generator agent skill in projects/agents/quiz-generator/SKILL.md
- [X] T035 [P] [US4] Implement quiz generation function in projects/backend/src/services/quiz_generator.py
- [X] T036 [US4] Add background parameter support to quiz generator in projects/backend/src/services/quiz_generator.py
- [X] T037 [US4] Implement GET /api/quiz/{slug} endpoint in projects/backend/src/api/quiz.py
- [X] T038 [US4] Implement POST /api/quiz/{slug} endpoint in projects/backend/src/api/quiz.py
- [X] T039 [US4] Get /api/quiz/results endpoint in projects/backend/src/api/quiz.py
- [X] T040 [US4] Build quiz UI component in projects/website/src/components/QuizComponent.js
- [X] T041 [US4] Add quiz results display in profile page in projects/website/src/pages/profile.js

## Phase 7: User Story 5 - Read Chapter Summaries (P3)

**Goal**: Users see summaries at start of each chapter
**Independent Test**: Open chapter, verify 3-5 bullet summary appears

- [X] T042 [P] [US5] Create summarizer agent skill in projects/agents/summarizer/SKILL.md
- [X] T043 [P] [US5] Implement summary generation function in projects/backend/src/services/summarizer.py
- [X] T044 [US5] Cache summaries in database during build in projects/backend/src/services/summarizer.py
- [X] T045 [US5] Add summary section to chapter MDX template in projects/website/src/components/ChapterSummary.js

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T046 Add error handling for chatbot unavailability in projects/backend/src/api/chat.py
- [X] T047 Handle session-less users (cookies disabled) with in-memory fallback in projects/backend/src/middleware/auth.py
- [X] T048 Add loading states to chat widget in projects/website/src/components/ChatWidget.js
- [X] T049 Verify mobile layout at 375px width in projects/website/src/css/custom.css
- [X] T050 Run performance tests (<2s page load, <5s chatbot response) in projects/
- [X] T051 Final end-to-end test: full user flow in projects/

## Dependencies Graph

```
Phase 1 (Setup)
  └─ All tasks complete before Phase 2

Phase 2 (Foundational)
  ├─ T006-T008: Database + models → needed by all user stories
  ├─ T009: Health check → needed for deployment verification
  └─ T010-T011: RAG setup → needed for US2

Phase 3 (US1 - Read Chapters)
  └─ Depends on: Phase 2 complete

Phase 4 (US2 - Chatbot)
  ├─ Depends on: Phase 2 (RAG)
  └─ Can parallel with: Phase 3

Phase 5 (US3 - Auth)
  ├─ Depends on: Phase 2 (DB)
  └─ Can parallel with: Phases 3, 4

Phase 6 (US4 - Quizzes)
  ├─ Depends on: Phase 2 (DB), Phase 5 (Auth)
  └─ Uses: Summarizer service (Phase 7)

Phase 7 (US5 - Summaries)
  ├─ Depends on: Phase 2 (DB)
  └─ Can parallel with: Phases 3-6

Phase 8 (Polish)
  └─ Depends on: All previous phases
```

## Parallel Execution Examples

**Example 1**: Frontend + Backend in parallel (after foundational)
- Task A: Frontend team works on Phase 3-7 UI components
- Task B: Backend team works on Phase 3-7 API endpoints
- Coordination: API contracts defined in openapi.yaml

**Example 2**: RAG pipeline + Auth in parallel
- Task A: Build RAG retrieval and chat widget (US2)
- Task B: Build authentication flow (US3)
- No dependencies between them

**Example 3**: Quiz + Summary in parallel
- Task A: Quiz generation and UI (US4)
- Task B: Summary generation and display (US5)
- Both depend on Phase 2 only