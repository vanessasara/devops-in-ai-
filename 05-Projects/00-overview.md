# Project Phases — AI Logging Agent

This project is built in progressive levels. Each level adds capability on top of the previous one. You never rewrite — you layer.

---

## The Five Levels

| Level | Name | Interface | What It Adds |
|---|---|---|---|
| 0 | Terminal Prototype | CLI only | Prove the agent works |
| 1 | Streamlit UI | Browser (Python) | Make it accessible for testing |
| 2 | Production Web | Next.js + FastAPI | Real frontend with session state |
| 3 | Multi-Source | Next.js + FastAPI | Multiple log sources, correlation |
| 4 | Multi-Agent | Next.js + FastAPI | Specialist subagents, orchestrator |

---

## The Rule

**Each level's agent logic carries forward unchanged.**

When you move from Level 0 to Level 1, you don't rewrite the tools or the agent. You wrap them. When you move from Level 1 to Level 2, you don't rewrite FastAPI. You add a frontend. The core always stays the same.

This is what the layered architecture from Chapter 7 was designed for.

---

## Folder Structure

```
ai-logging-agent/
├── 00-terminal-prototype/     ← Level 0 — CLI only
├── 01-streamlit-ui/           ← Level 1 — Streamlit chat interface
├── 02-nextjs-production/      ← Level 2 — Next.js + FastAPI + session state
├── 03-multi-source/           ← Level 3 — coming later
└── 04-multi-agent/            ← Level 4 — coming later
```

---

## Start Here

If you are new to this project, start at `00-terminal-prototype`. Get the agent working in the terminal first. Understand the tools, the config, the agent loop. Then move to Level 1.

Do not skip levels. Each one teaches something the next one depends on.
