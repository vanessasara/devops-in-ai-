---
title: Project Guide
aliases: [Build Guide]
tags: [index, guide, tutorial]
---

# Project Guide

This section provides step-by-step guidance for building the Level 1 log analysis agent.

---

## Topics

| Order | Topic | Description |
|-------|-------|-------------|
| 1 | [[01 - How the Project Works]] | Architecture overview, request flow, stack explanation |
| 2 | [[02 - OpenAI Agents SDK]] | Core primitives: Agent, function_tool, Runner, LiteLLM |
| 3 | [[03 - Building the Components]] | Six-layer architecture: Config, Tools, Agent, Utils, API, CLI |
| 4 | [[04 - FastAPI + Next.js Architecture]] | Full-stack setup, component structure, request lifecycle |

---

## Learning Order

Follow these guides in order:

1. **[[01 - How the Project Works]]** - Understand the big picture
2. **[[02 - OpenAI Agents SDK]]** - Learn the SDK primitives
3. **[[03 - Building the Components]]** - Build the layered architecture
4. **[[04 - FastAPI + Next.js Architecture]]** - Create the full-stack application

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                │
│  chat.tsx → api.ts → POST /chat → ChatResponse     │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                  │
│  main.py → app.state.agent → process_query()       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                Agent (OpenAI Agents SDK)            │
│  Agent → Runner.run() → tools → final_output       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  Logs Directory                     │
│  list_log_files() → read_log_file() → search_logs() │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| AI Agent | OpenAI Agents SDK | Handles ReAct loop automatically |
| Model | Gemini via LiteLLM | Easy model swapping |
| Backend | FastAPI | Async, Pydantic validation |
| Frontend | Next.js + TypeScript | Modern React, App Router |

---

## Connections

- Prerequisites: [[../03 - Implementation/00-index|Implementation]]
- Project: [[../05 - Projects/ai-logging-agent Level 1/README|Level 1 Project]]