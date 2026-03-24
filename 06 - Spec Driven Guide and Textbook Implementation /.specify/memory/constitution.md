# Agentic AI in DevOps Constitution

## Core Principles

### I. Mission-Driven Content
Build an AI-native interactive textbook that teaches Agentic AI in DevOps, FTE Digital Employees, and AI-driven operations. Every chapter, quiz, and chatbot answer must reinforce the goal of equipping engineers, architects, and teams to design, deploy, and operate AI agents as first-class infrastructure.

### II. Clean Repository Structure
ALL deployable content MUST live inside the /projects folder. The repo root must be clean. Remove index.html, _sidebar.md, _navbar.md, and .nojekyll from root. Docusaurus inside /projects/website handles all navigation, search, and theming.

### III. Pattern-Based Learning
Focus on transferable patterns (ReAct, Orchestrator, Triage, Agents-as-Tools, Planning), not vendor lock-in. Code examples are conceptual Python/pseudocode only — never copy-pasteable production scripts. Every concept MUST tie to a working DevOps use case.

### IV. Free Tier Infrastructure First
All services MUST run on free tiers of Vercel (frontend), Railway (backend), Qdrant (vectors), and Neon (database) for v1. No paid infrastructure. Backend must cold-start and serve a response within 5 seconds after warmup.

### V. Content Grounding (NON-NEGOTIABLE)
RAG chatbot MUST answer only from book content — no hallucination from general knowledge. Every answer MUST cite the chapter and section it came from. Return 'not in book' otherwise. Strict system prompt enforcement required.

### VI. Agent Skills Convention
Every agent in /projects/agents follows the SKILL.md convention: Role, Tasks, Tools, Input Schema, Output Schema, Guardrails. This makes agents composable, auditable, and easy to swap.

## Technical Architecture

**Stack**: Docusaurus v3 (frontend), FastAPI Python 3.12 (backend), Better-Auth (authentication), OpenAI Agents SDK (AI), Gemini via LiteLLM (model), MiniLM-L6-v2 (embeddings), Qdrant Cloud (vector store), Neon Postgres (database), Prisma (ORM).

**Deployment Targets**: Vercel (website), Railway (backend + RAG service), Qdrant Cloud (vectors), Neon (Postgres).

**Environment Variables**: GEMINI_API_KEY, GEMINI_MODEL, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, FRONTEND_URL.

## Success Criteria & Definition of Done

**P0 Must Have**: Clean mobile-friendly UI (<2s load), book readable in <45 min, RAG answers grounded with citations, auth signup/login working, all services deployed on free tiers, 90-second demo recordable.

**P1 Should Have**: Content personalization by background tier, auto-generated quizzes with results saved, AI-generated chapter summaries cached in Neon.

**Definition of Done Checklist**: Repo root clean (Docsify removed), all 7 chapters visible in Docusaurus with search, RAG chatbot functional with citations, auth working with profile save, personalization visible per background tier, quizzes/summaries generated and cached, all services deployed with health checks passing.

## Governance

Constitution supersedes all other practices. This document is the single source of truth for what will be built. Any feature, page, or service not described here is out of scope for v1.

**Amendment Procedure**: Changes require an explicit version bump and a note in the changelog. MAJOR: Backward incompatible governance/principle removals. MINOR: New principle/section added or materially expanded. PATCH: Clarifications, wording, typo fixes.

**Version Bump Rules**: All PRs/reviews must verify compliance with constitution principles. Non-goals (no robotics, no extra animations, no LangChain, no self-hosted models, no video content, no paid APIs beyond Gemini, no SSO) must be enforced.

**Compliance Review**: Every feature spec and implementation plan must pass a Constitution Check before Phase 0 research.

**Version**: 1.0.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2026-03-24