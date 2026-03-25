---
tags: [guide, project, architecture]
---

# How the Project Works

This project is an AI-powered log analysis agent. You send it a question about your logs in plain language, and it reads, searches, and analyses your log files — then gives you a clear answer.

The entire system is built around three ideas:

**1. The agent decides what to do.**
You don't write `if error then do X`. You describe the agent's role and give it tools. The agent reasons about your question and chooses which tools to call, in what order, and when it has enough information to answer.

**2. Tools are just Python functions.**
Reading a log file, searching for a term, saving a summary — each of these is a plain Python function decorated with `@function_tool`. The agent calls them like a human would use a terminal.

**3. The layers are separated.**
Config, tools, agent logic, and the web interface are all in separate files. Changing one doesn't break the others. Adding a new tool doesn't touch the agent file. Swapping the frontend doesn't touch the backend.

---

## The Flow of a Single Request

```
You type a question
        ↓
Frontend sends it to the API
        ↓
FastAPI receives it and passes it to the agent
        ↓
Agent reasons: "I need to read a log file first"
        ↓
Agent calls read_log_file() tool
        ↓
Tool returns the file contents
        ↓
Agent reasons: "Now I can answer"
        ↓
Agent returns final response
        ↓
FastAPI sends it back to the frontend
        ↓
You see the answer in the chat
```

This loop — reason, act, observe, reason again — is called the **ReAct pattern**. The Agents SDK handles this loop automatically. You never write it manually.

---

## What Lives Where

```
backend/
├── src/
│   ├── config.py        ← API keys, model name, log directory
│   ├── tools/           ← what the agent can do
│   ├── agents/          ← the agent definition and runner
│   └── utils/           ← output helpers
└── main.py              ← FastAPI routes

frontend/
├── app/                 ← Next.js pages
├── components/          ← UI components
│   └── chat/            ← chat-specific components
└── lib/
    └── api.ts           ← talks to the FastAPI backend
```

---

## The Stack

| Layer | Technology | Why |
|---|---|---|
| AI Agent | OpenAI Agents SDK | Handles the ReAct loop, tool calling, and agent execution |
| Model | Gemini via LiteLLM | LiteLLM lets you swap models by changing one string |
| Backend API | FastAPI | Exposes the agent as an HTTP endpoint |
| Frontend | Next.js + TypeScript | Chat interface the user interacts with |
| UI Components | shadcn/ui | Clean, accessible components built on Tailwind |

---

## The Agent vs LangChain

This project uses the **OpenAI Agents SDK**, not LangChain. The book this project is based on uses LangChain — but the Agents SDK achieves the same result with significantly less code.

LangChain requires you to wire together Chains, PromptTemplates, Memory objects, RunnableWithMessageHistory, and tool execution loops manually. The Agents SDK collapses all of that into three things: an `Agent`, a `Runner`, and `@function_tool` decorated functions. The Runner handles the entire execution loop internally.

The concepts are identical. The code is much simpler.
