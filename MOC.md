---
title: AI Agents in DevOps - Map of Content
aliases: [Home, Index, MOC]
tags: [moc, index]
---

# AI Agents in DevOps

A comprehensive guide to building AI-powered log analysis systems for DevOps teams.

---

## Learning Path

Follow these sections in order for a complete understanding.

### 1. Introduction

Start here to understand the "why" behind AI agents in DevOps.

- [[00 - Introduction/README|Introduction to AI Agents in DevOps]] - Why AI agents matter for log analysis
- [[00 - Introduction/AI Agent vs Traditional Tools|AI Agent vs Traditional Tools]] - Comparison with scripts and traditional monitoring tools

### 2. Core Concepts

Understand the fundamental building blocks of AI agents.

- [[01 - Core Concepts/Understanding the core building blocks|Understanding the Core Building Blocks]] - LLM basics and data retrieval concepts
- [[01 - Core Concepts/Core Components of an AI Agent|Core Components of an AI Agent]] - Role, tasks, tools, memory, guardrails, and cooperation
- [[01 - Core Concepts/What Your Agent Needs to Know|What Your Agent Needs to Know]] - How to structure an agent's knowledge and capabilities

### 3. Design Patterns

Learn the patterns that make agents effective and reliable.

- [[02 - Design Patterns/Design Patterns for AI Agents|Design Patterns for AI Agents]] - Reflection, Tool Use, ReAct, Planning, and Multi-Agent patterns
- [[02 - Design Patterns/Multiple agents working together|Multiple Agents Working Together]] - Orchestrator, Triage, and Agents as Tools patterns

### 4. Implementation

Practical considerations for building your agent.

- [[03 - Implementation/Data Retrieval|Data Retrieval]] - How to get logs into your agent
- [[03 - Implementation/Cost break down|Cost Breakdown]] - Infrastructure and operational costs

### 5. Project Guide

Step-by-step guide for building the Level 1 log analysis agent.

- [[04 - Project Guide/01 - How the Project Works|How the Project Works]] - Architecture overview and request flow
- [[04 - Project Guide/02 - OpenAI Agents SDK|OpenAI Agents SDK]] - Core primitives: Agent, function_tool, Runner
- [[04 - Project Guide/03 - Building the Components|Building the Components]] - The six-layer architecture
- [[04 - Project Guide/04 - FastAPI + Next.js Architecture|FastAPI + Next.js Architecture]] - Full-stack implementation

---

## Projects

### Level 1 - Basic Log Analysis Agent

A conversational agent that reads log files and answers questions about them.

- [[05 - Projects/ai-logging-agent Level 1/README|Project README]]
- Backend: FastAPI + OpenAI Agents SDK + Gemini
- Frontend: Next.js + TypeScript + shadcn/ui

---

## Quick Reference

| Topic | File | Description |
|-------|------|-------------|
| Why AI Agents | [[00 - Introduction/README]] | Introduction and motivation |
| Components | [[01 - Core Concepts/Core Components of an AI Agent]] | 6 essential components |
| Patterns | [[02 - Design Patterns/Design Patterns for AI Agents]] | 5 design patterns |
| Data Layer | [[03 - Implementation/Data Retrieval]] | Log ingestion strategies |
| SDK Guide | [[04 - Project Guide/02 - OpenAI Agents SDK]] | Agents SDK primitives |
| Architecture | [[04 - Project Guide/04 - FastAPI + Next.js Architecture]] | Full-stack setup |

---

## Graph Overview

```
Introduction ──→ Core Concepts ──→ Design Patterns ──→ Implementation ──→ Project Guide
     │                │                  │                   │                  │
     │                │                  │                   │                  │
     └────────────────┴──────────────────┴───────────────────┴──────────────────┘
                                        │
                                        ▼
                                   Projects
```

---

## How to Use This Vault

1. Start with [[00 - Introduction/00-index|Introduction Index]]
2. Progress through each folder in order (00 → 01 → 02 → 03 → 04 → 05)
3. Each folder has an `00-index.md` file with navigation
4. Use the graph view in Obsidian to see connections between topics