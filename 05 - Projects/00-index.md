---
title: Projects
aliases: [Code]
tags: [index, projects]
---

# Projects

This section contains the actual implementation code and project files.

---

## Available Projects

### Level 1 - Basic Log Analysis Agent

A conversational agent that reads log files and answers questions about them.

- [[ai-logging-agent Level 1/README|Project README]]
- **Backend:** FastAPI + OpenAI Agents SDK + Gemini
- **Frontend:** Next.js + TypeScript + shadcn/ui

---

## Project Levels Roadmap

| Level | Focus | Features |
|-------|-------|----------|
| 1 | Reactive Analysis | Chat interface, log reading, basic analysis |
| 2 | Reasoning Agents | Multi-step reasoning, deeper root cause analysis |
| 3 | Temporal Integration | Time-series awareness, anomaly detection |
| 4 | Multi-Agent | Orchestrator + specialist agents coordination |

---

## Directory Structure

```
ai-logging-agent Level 1/
├── backend/
│   ├── main.py          # FastAPI entry point
│   ├── src/
│   │   ├── config.py    # Configuration
│   │   ├── agents/      # Log analyzer agent
│   │   ├── tools/       # Log manipulation tools
│   │   └── utils/       # Utilities
│   └── logs/            # Log files directory
│
└── frontend/
    ├── app/             # Next.js pages
    ├── components/      # React components
    │   ├── chat/        # Chat-specific components
    │   └── ui/          # shadcn/ui components
    └── lib/
        └── api.ts       # Backend communication
```

---

## Quick Start

1. **Backend:**
   ```bash
   cd backend
   uv sync
   uv run main.py
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open http://localhost:3000

---

## Connections

- Prerequisites: [[../04 - Project Guide/00-index|Project Guide]]