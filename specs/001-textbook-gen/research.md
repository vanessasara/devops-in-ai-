# Research: Interactive Textbook Generation

## Decisions Made

### Tech Stack (from Constitution)
- **Frontend**: Docusaurus v3 with MDX
- **Backend**: FastAPI Python 3.12
- **Auth**: Better-Auth with Prisma adapter
- **AI**: OpenAI Agents SDK + Gemini via LiteLLM
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: Qdrant Cloud
- **Database**: Neon Postgres with Prisma ORM

**Decision**: Use Constitution-specified stack directly.

**Rationale**: The Constitution already evaluated and selected these technologies for free-tier compatibility, simplicity, and project requirements. No need to re-evaluate.

**Alternatives considered**:
- LangChain (rejected per Constitution - too complex, more dependencies)
- Self-hosted models (rejected per Constitution - not free tier compatible)
- Other auth solutions (rejected - Better-Auth is lightweight and supports Postgres)

### Content Structure
- 7 chapters + intro per Constitution
- Each chapter: MDX file with frontmatter (title, time, tags)
- Chapter length: 800-1,400 words each

**Decision**: Use Docusaurus docs folder structure with MDX files.

**Rationale**: Docusaurus natively supports MDX with frontmatter, provides search, navigation, and mobile-friendly rendering out of the box.

### RAG Implementation
- Chunking: 512 tokens with 64-token overlap per chapter section
- Retrieval: top-3 chunks → rerank → inject as grounded context
- Every answer cites chapter and section

**Decision**: Two-pass retrieval with strict citation requirements.

**Rationale**: Constitution V mandates content grounding - strict system prompts and retrieval limits ensure no hallucinations.

### Content Personalization
- 4 background levels: beginner, engineer, architect, manager
- Server-side variant selection based on user profile
- Default: engineer (no auth required)

**Decision**: Server-side content transformation before render.

**Rationale**: Frontend doesn't need to handle branching logic, SEO-friendly (serves correct content), cleaner separation of concerns.

### Quiz Generation
- 4 multiple-choice questions per chapter
- Auto-generated at build time, cached in Neon
- Quiz results stored per user

**Decision**: Build-time generation with database caching.

**Rationale**: Constitution mandates no token cost spikes - pre-generation at build time prevents per-request AI calls.

## Findings Summary

All research questions resolved using Constitution-specified stack. No NEEDS CLARIFICATION markers needed - the feature is fully specified.

### Best Practices Applied

1. **Docusaurus**: Use docusaurus.config.js for theme customization, docs folder for chapters, sidebars.js for navigation
2. **Better-Auth**: Use email/password provider with Prisma adapter for Neon
3. **RAG**: Use sentence-transformers for embeddings, Qdrant for similarity search, strict system prompts for grounding
4. **Personalization**: Store background preference in user profile, transform content at server level
5. **Performance**: Target <2s page load, <5s chatbot response, use async FastAPI endpoints