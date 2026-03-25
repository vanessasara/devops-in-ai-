# Level 2 — Next.js Production Interface

**Folder:** `02-nextjs-production/`
**Interface:** Next.js frontend + FastAPI backend
**Goal:** Production-ready chat interface with full session state management

---

## What This Level Is

Level 2 replaces Streamlit with a proper full-stack setup. The backend becomes a FastAPI server. The frontend becomes a Next.js application with TypeScript, shadcn/ui components, and persistent session state.

The `src/` folder from Level 0 copies over completely unchanged. FastAPI wraps it. Next.js talks to FastAPI. The agent never knows or cares which interface is calling it.

---

## Folder Structure

```
02-nextjs-production/
├── backend/
│   ├── src/                    ← copied from Level 0 unchanged
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── tools/
│   │   ├── agents/
│   │   └── utils/
│   ├── main.py                 ← FastAPI server
│   ├── pyproject.toml
│   └── .env
└── frontend/
    ├── app/
    │   ├── page.tsx
    │   ├── layout.tsx
    │   └── globals.css
    ├── components/
    │   ├── chat.tsx
    │   └── chat/
    │       ├── message-bubble.tsx
    │       ├── typing-indicator.tsx
    │       ├── chat-input.tsx
    │       ├── chat-messages.tsx
    │       └── sidebar.tsx
    ├── lib/
    │   ├── api.ts
    │   └── hooks/
    │       ├── use-local-storage.ts
    │       └── use-sessions.ts
    ├── components.json
    ├── package.json
    └── .env.local
```

---

## Phase 1 — Backend (FastAPI)

### backend/pyproject.toml

```toml
[project]
name = "ai-logging-agent-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
    "fastapi",
    "uvicorn",
]
```

### backend/main.py

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.config import Config
from src.agents import LogAnalyzerAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.validate()
    app.state.agent = LogAnalyzerAgent()
    yield

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000"]
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    response = await app.state.agent.process_query(body.message)
    return ChatResponse(response=response)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

**Run backend:**
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

---

## Phase 2 — Frontend Setup

```bash
pnpm create next-app frontend --typescript --tailwind --eslint --app --no-src-dir
cd frontend
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button input card scroll-area avatar
pnpm add next-themes lucide-react date-fns
```

### frontend/.env.local

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Phase 3 — Session State (the key difference from Streamlit)

This is what Streamlit's `st.session_state` was doing — but in the browser.

### lib/hooks/use-local-storage.ts

```typescript
"use client"

import { useState, useEffect } from "react"

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(initialValue)

  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key)
      if (item) setStoredValue(JSON.parse(item))
    } catch (error) {
      console.error(error)
    }
  }, [key])

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }

  return [storedValue, setValue] as const
}
```

### lib/hooks/use-sessions.ts

```typescript
"use client"

import { useState, useCallback } from "react"
import { useLocalStorage } from "./use-local-storage"
import { type Message } from "@/lib/api"

export interface Session {
  id: string
  title: string
  createdAt: number
  messages: Message[]
}

const MAX_SESSIONS = 20

function createSession(): Session {
  return {
    id: crypto.randomUUID(),
    title: "New chat",
    createdAt: Date.now(),
    messages: [],
  }
}

export function useSessions() {
  const [sessions, setSessions] = useLocalStorage<Session[]>("chat_sessions", [createSession()])
  const [activeId, setActiveId] = useLocalStorage<string>("chat_active_session", sessions[0]?.id ?? "")

  const activeSession = sessions.find((s) => s.id === activeId) ?? sessions[0]

  const updateMessages = useCallback((messages: Message[]) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== activeId) return s
        const title = messages.find((m) => m.role === "user")?.content.slice(0, 40) ?? "New chat"
        return { ...s, messages, title }
      })
    )
  }, [activeId, setSessions])

  const newSession = useCallback(() => {
    const session = createSession()
    setSessions((prev) => {
      const updated = [session, ...prev]
      return updated.slice(0, MAX_SESSIONS)
    })
    setActiveId(session.id)
  }, [setSessions, setActiveId])

  const switchSession = useCallback((id: string) => {
    setActiveId(id)
  }, [setActiveId])

  const deleteSession = useCallback((id: string) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== id)
      if (updated.length === 0) {
        const fresh = createSession()
        setActiveId(fresh.id)
        return [fresh]
      }
      if (id === activeId) setActiveId(updated[0].id)
      return updated
    })
  }, [activeId, setSessions, setActiveId])

  return {
    sessions,
    activeSession,
    updateMessages,
    newSession,
    switchSession,
    deleteSession,
  }
}
```

---

## Phase 4 — Frontend Components

### lib/api.ts

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: number
}

export async function sendMessage(message: string): Promise<string> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail ?? `Request failed: ${res.status}`)
  }
  const data = await res.json()
  return data.response
}
```

### components/chat/message-bubble.tsx

```tsx
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { type Message } from "@/lib/api"
import { Bot, User } from "lucide-react"
import { format } from "date-fns"

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"

  return (
    <div className={`flex gap-3 group ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className={isUser ? "bg-violet-600 text-white" : "bg-emerald-500 text-white"}>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>
      <div className="flex flex-col gap-1">
        <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words shadow-sm ${
          isUser ? "bg-violet-600 text-white rounded-tr-sm" : "bg-muted text-foreground rounded-tl-sm"
        }`}>
          {message.content}
        </div>
        <span className={`text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity ${isUser ? "text-right" : "text-left"}`}>
          {format(message.timestamp, "HH:mm")}
        </span>
      </div>
    </div>
  )
}
```

### components/chat/sidebar.tsx

```tsx
"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ThemeToggle } from "@/components/theme-toggle"
import { type Session } from "@/lib/hooks/use-sessions"
import { MessageSquare, Trash2, Terminal, Plus } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

const EXAMPLE_QUESTIONS = [
  "What log files are available?",
  "Read sample_app.log",
  "Search for ERROR in sample_app.log",
  "Summarise everything and save it",
]

interface SidebarProps {
  sessions: Session[]
  activeSessionId: string
  loading: boolean
  onExampleClick: (q: string) => void
  onNewSession: () => void
  onSwitchSession: (id: string) => void
  onDeleteSession: (id: string) => void
}

export function Sidebar({
  sessions, activeSessionId, loading,
  onExampleClick, onNewSession, onSwitchSession, onDeleteSession,
}: SidebarProps) {
  return (
    <div className="w-64 shrink-0 flex flex-col h-full border-r bg-muted/30">
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-violet-500 to-emerald-500 flex items-center justify-center">
            <Terminal className="h-3.5 w-3.5 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold leading-none">Log Analyzer</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">Gemini · Agents SDK</p>
          </div>
        </div>
        <ThemeToggle />
      </div>

      <div className="p-3 border-b">
        <Button onClick={onNewSession} variant="outline" size="sm" className="w-full gap-2 text-xs">
          <Plus className="h-3.5 w-3.5" /> New chat
        </Button>
      </div>

      <ScrollArea className="flex-1 p-3">
        <div className="flex flex-col gap-4">

          {sessions.length > 0 && (
            <div>
              <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide mb-2 px-1">
                Recent chats
              </p>
              <div className="flex flex-col gap-1">
                {sessions.map((s) => (
                  <div
                    key={s.id}
                    className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer transition-colors ${
                      s.id === activeSessionId
                        ? "bg-violet-50 dark:bg-violet-950/30 border border-violet-100 dark:border-violet-900"
                        : "hover:bg-muted"
                    }`}
                    onClick={() => onSwitchSession(s.id)}
                  >
                    <MessageSquare className="h-3 w-3 shrink-0 text-violet-400" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-foreground truncate">{s.title}</p>
                      <p className="text-[10px] text-muted-foreground">
                        {formatDistanceToNow(s.createdAt, { addSuffix: true })}
                      </p>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); onDeleteSession(s.id) }}
                      className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-500 transition-all"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide mb-2 px-1">
              Try asking
            </p>
            <div className="flex flex-col gap-1">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => onExampleClick(q)}
                  disabled={loading}
                  className="text-left text-xs text-foreground/70 hover:text-foreground hover:bg-violet-50 dark:hover:bg-violet-950/30 rounded-lg px-2.5 py-1.5 transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

        </div>
      </ScrollArea>
    </div>
  )
}
```

### components/chat.tsx

```tsx
"use client"

import { useState } from "react"
import { Sidebar } from "@/components/chat/sidebar"
import { ChatMessages } from "@/components/chat/chat-messages"
import { ChatInput } from "@/components/chat/chat-input"
import { sendMessage, type Message } from "@/lib/api"
import { useSessions } from "@/lib/hooks/use-sessions"

export function Chat() {
  const { sessions, activeSession, updateMessages, newSession, switchSession, deleteSession } = useSessions()
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const messages = activeSession?.messages ?? []

  async function handleSubmit(message: string) {
    if (!message.trim() || loading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message.trim(),
      timestamp: Date.now(),
    }

    const updated = [...messages, userMessage]
    updateMessages(updated)
    setInput("")
    setError(null)
    setLoading(true)

    try {
      const response = await sendMessage(message.trim())
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response,
        timestamp: Date.now(),
      }
      updateMessages([...updated, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSession?.id ?? ""}
        loading={loading}
        onExampleClick={handleSubmit}
        onNewSession={newSession}
        onSwitchSession={switchSession}
        onDeleteSession={deleteSession}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatMessages messages={messages} loading={loading} error={error} />
        <ChatInput value={input} onChange={setInput} onSubmit={handleSubmit} disabled={loading} />
      </div>
    </div>
  )
}
```

---

## How Session State Maps to Streamlit

| Streamlit | Next.js Level 2 |
|---|---|
| `st.session_state.messages` | `activeSession.messages` in `useSessions` |
| `st.session_state.agent` | `app.state.agent` in FastAPI lifespan |
| Persists within browser tab | Persists in `localStorage` across refreshes |
| Single conversation | Multiple named sessions with history |
| Cleared on tab close | Persists until user deletes |
| `st.rerun()` | React state update triggers re-render |

---

## Run Both Together

```bash
# Terminal 1
cd backend && uv run uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend && pnpm dev
```

Open `http://localhost:3000`.

---

## Tests to Run

```
1. Send a message — verify it appears and persists on refresh
2. Click New chat — verify a new empty session starts
3. Switch between sessions — verify each has its own messages
4. Delete a session — verify it disappears and another is selected
5. Hover over a message — verify timestamp appears
6. Refresh the page — verify all sessions and messages are still there
```
