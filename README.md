# AI Agents in DevOps

> A comprehensive guide to building AI-powered log analysis systems for DevOps teams.

This repository contains structured notes and guides for understanding and implementing AI agents for log analysis in DevOps environments.

---

## Quick Navigation

| Section | Description | Start Here |
|---------|-------------|------------|
| **Introduction** | Why AI agents matter for DevOps | [[00 - Introduction/00-index]] |
| **Core Concepts** | Building blocks of AI agents | [[01 - Core Concepts/00-index]] |
| **Design Patterns** | Architectural patterns for agents | [[02 - Design Patterns/00-index]] |
| **Implementation** | Practical considerations | [[03 - Implementation/00-index]] |
| **Project Guide** | Step-by-step build guide | [[04 - Project Guide/00-index]] |
| **Projects** | Working code examples | [[05 - Projects/00-index]] |

---

## What's Inside

### Concepts You'll Learn

- **Why AI agents?** - Understanding the value proposition vs. traditional tools
- **Core Components** - Role, tasks, tools, memory, guardrails, cooperation
- **Design Patterns** - ReAct, Tool Use, Reflection, Planning, Multi-Agent
- **Data Retrieval** - Getting logs from various sources into your agent
- **Cost Analysis** - Understanding the ROI of AI agents

### Project Structure

```
ai-logging-agent Level 1/
├── backend/              # Python FastAPI + OpenAI Agents SDK
│   ├── main.py           # API entry point
│   ├── src/
│   │   ├── agents/       # Log analyzer agent
│   │   ├── tools/        # Log manipulation tools
│   │   └── config.py     # Configuration
│   └── logs/             # Sample log files
│
└── frontend/             # Next.js + TypeScript
    ├── app/              # Pages
    ├── components/       # React components
    └── lib/              # API client
```

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| AI Agent | OpenAI Agents SDK |
| Model | Gemini (via LiteLLM) |
| Backend | FastAPI |
| Frontend | Next.js + TypeScript |
| UI | shadcn/ui + Tailwind |

---

## Getting Started

### For Learners

1. Open this repository in **Obsidian** for the best experience
2. Start with `MOC.md` (Map of Content) for navigation
3. Follow the learning path: Introduction → Core Concepts → Design Patterns → Implementation → Project Guide

### For Developers

1. Navigate to `05 - Projects/ai-logging-agent Level 1/`
2. Follow the README for setup instructions
3. Backend: `uv run main.py`
4. Frontend: `npm run dev`

---

## Obsidian Setup

This vault is optimized for **Obsidian**:

- Each folder has an `00-index.md` for navigation
- All internal links use wikilinks `[[filename]]`
- Tags are added via frontmatter for graph clustering
- Open `MOC.md` as your starting point

### Graph View Tips

- Filter by tags: `moc`, `index`, `concepts`, `patterns`, `guide`
- Group by folder for better visualization
- Use "Show attachments" to see image connections

---

## Contributing

This is a personal knowledge base, but suggestions are welcome via issues or pull requests.

---

## License

MIT