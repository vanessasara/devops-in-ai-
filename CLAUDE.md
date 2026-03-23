# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Obsidian notes repository about AI-powered log analysis systems for DevOps teams. It contains educational documentation plus working code projects at increasing complexity levels.

## Project Structure

```
05 - Projects/
├── 00-terminal-prototype/   # Level 0 - Terminal-only prototype
├── 01-streamlit-ui/         # Level 1 - Streamlit chat interface
├── 02-nextjs-production/    # Level 2 - Next.js + FastAPI (production)
│   ├── backend/             # Python FastAPI + OpenAI Agents SDK
│   └── frontend/            # Next.js 16 + React 19 + TypeScript
├── 03-multi-source/         # Level 3 - Decision making & K8s actions
└── 04-multi-agent/          # Level 4 - Multi-agent system
```

Each project level is **standalone** — do not modify previous level folders.

## Tech Stack

| Layer | Technology |
|-------|------------|
| AI Agent | OpenAI Agents SDK |
| Model | Google Gemini (via LiteLLM) |
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 16 + React 19 + TypeScript |
| UI | shadcn/ui + Tailwind CSS 4 |
| Package Managers | uv (backend), pnpm (frontend) |

## Common Commands

### Backend (02-nextjs-production/backend)

```bash
cd backend
uv sync                    # Install dependencies
uv run main.py             # Start FastAPI server with hot reload (port 8000)
```

### Frontend (02-nextjs-production/frontend)

```bash
cd frontend
pnpm install               # Install dependencies
pnpm dev                   # Start development server (port 3000)
pnpm build                 # Production build
pnpm lint                  # Run ESLint
```

## Environment Variables

Backend `.env`:
```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-3-flash-preview
LOG_DIRECTORY=logs
TEMPERATURE=0.1
FRONTEND_URL=http://localhost:3000
```

Frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

**Backend**: FastAPI app with `/chat` POST endpoint that proxies to a LogAnalyzerAgent. Agent uses OpenAI Agents SDK with LiteLLM to call Google Gemini. Tools include: `list_log_files`, `read_log_file`, `search_logs`, `save_summary`.

**Frontend**: Next.js app with React chat components. Calls backend `/chat` endpoint via `/lib/api.ts`.

## Key Files

- `backend/main.py` — FastAPI entry point with CORS and lifespan setup
- `backend/src/config.py` — Configuration and agent instructions
- `backend/src/agents/log_analyzer.py` — LogAnalyzerAgent class
- `backend/src/tools/log_tools.py` — Log manipulation tools
- `frontend/lib/api.ts` — API client for backend communication
- `frontend/components/chat.tsx` — Main chat component

## Development Notes

- Each level folder (`00-terminal-prototype/`, etc.) is independent and complete
- AGENTS.md files in project folders contain build instructions for that level
- Log files go in `backend/logs/` directory
- The agent reads `system_prompt.txt` for instructions when present