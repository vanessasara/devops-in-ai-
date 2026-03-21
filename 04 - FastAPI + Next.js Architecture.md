# FastAPI + Next.js Architecture

This chapter replaces the book's Streamlit UI with a production-ready full-stack setup. The backend is FastAPI. The frontend is Next.js with TypeScript. They communicate over HTTP. The agent logic from Chapter 7 is completely unchanged.

---

## Why This Stack

The book uses Streamlit because it's fast to set up and good for prototyping. For a tool that DevOps engineers, support teams, and managers will all use — a proper web interface makes more sense.

FastAPI handles the backend API. It's async-native, which matters because `Runner.run()` is an async call. It has automatic request/response validation through Pydantic. And it's easy to extend — adding new routes for Level 2 and Level 3 features requires minimal boilerplate.

Next.js handles the frontend. The App Router, TypeScript, and Tailwind are all set up out of the box. shadcn/ui provides accessible, well-designed components that don't require writing CSS from scratch.

---

## How the Two Sides Connect

The connection is a single HTTP call.

The frontend has `lib/api.ts` which defines a `sendMessage` function. It takes a string, posts it to `/chat` on the backend, and returns the response string. The frontend never imports anything from Python. The backend never imports anything from TypeScript. They are completely independent.

The backend URL is read from an environment variable — `NEXT_PUBLIC_API_URL`. In development this points to `localhost:8000`. In production it points to wherever the backend is deployed. No code changes needed between environments.

---

## Backend Structure

### The Agent Lives in app.state

The most important architectural decision in `main.py` is where the agent lives.

The agent is created once in the `lifespan` context manager and stored in `app.state.agent`. Every incoming request reuses the same instance. This matters because initialising a LiteLLM model connection is not free — you don't want to pay that cost on every single request.

### One Route for Level 1

The `/chat` route accepts a `ChatRequest` with a single `message` field and returns a `ChatResponse` with a single `response` field. The Pydantic models handle validation automatically — if the request body is malformed, FastAPI returns a 400 before your code even runs.

The route calls `await app.state.agent.process_query(body.message)` and returns the result. That's the entire route handler.

### CORS

CORS middleware is required because the frontend and backend run on different origins — different ports in development, different domains in production. Without it, the browser blocks the request before it reaches FastAPI.

The middleware reads the allowed frontend URL from an environment variable so you don't hardcode domains.

---

## Frontend Structure

### Component Architecture

The chat interface is split into focused components rather than one large file. Each component has a single responsibility.

`chat.tsx` is the shell — it owns state (messages, loading, error) and passes data and callbacks down to its children. It contains no JSX beyond wiring components together.

`chat/message-bubble.tsx` renders a single message. It knows whether it's a user or assistant message and styles accordingly. It knows nothing about state or API calls.

`chat/typing-indicator.tsx` shows the animated dots while the agent is thinking. Three lines of JSX.

`chat/chat-input.tsx` owns the text input and send button. It calls `onSubmit` when the user presses Enter or clicks Send. It doesn't know what happens after that.

`chat/chat-messages.tsx` renders the list of messages, the typing indicator, and the error state. It auto-scrolls to the bottom when new messages arrive.

`chat/sidebar.tsx` shows example questions and the session message history. Clicking an example question submits it directly.

`theme-toggle.tsx` switches between light and dark mode using `next-themes`.

### State Lives in One Place

All state — `messages`, `loading`, `error` — lives in `chat.tsx`. Child components receive data as props and call callbacks when something happens. They never fetch data or mutate state directly.

This makes the components reusable and easy to reason about. If the typing indicator needs to change, you open one small file. If the API call needs to change, you open `lib/api.ts`.

### The Message Format

Messages are stored as an array of objects with three fields: `id`, `role`, and `content`. The `id` is a UUID generated in the browser using `crypto.randomUUID()`. The `role` is either `"user"` or `"assistant"`. The `content` is the text.

This is display-only state. The backend receives only the current message — not the history. The agent is stateless. The frontend is the source of truth for what has been said in this session.

---

## The Full Request Lifecycle

```
1. User types a message and presses Enter
2. chat.tsx calls handleSubmit()
3. User message added to state → appears in UI immediately
4. loading set to true → typing indicator appears
5. lib/api.ts sends POST /chat with the message
6. FastAPI validates the request body
7. FastAPI calls agent.process_query()
8. Runner.run() starts the agent loop
9. Agent reasons → calls tools → reasons again → produces answer
10. Runner returns final_output
11. FastAPI returns ChatResponse
12. lib/api.ts resolves with the response string
13. Assistant message added to state → appears in UI
14. loading set to false → typing indicator disappears
```

Steps 8 and 9 are entirely handled by the Agents SDK. FastAPI handles 6–7 and 11–12. The frontend handles everything else.

---

## Development Setup

Two terminals, two commands.

Backend starts with `uv run uvicorn main:app --reload --port 8000` from the `backend/` directory. The `--reload` flag restarts the server automatically when you change a Python file.

Frontend starts with `pnpm dev` from the `frontend/` directory. Next.js watches for changes and hot-reloads the browser.

The `.env` files in each directory handle configuration. The backend reads `GEMINI_API_KEY` and `GEMINI_MODEL`. The frontend reads `NEXT_PUBLIC_API_URL`.

---

## What Comes Next

This setup handles Level 1 — a single agent, single log source, single chat endpoint.

Level 2 adds a second FastAPI route `/analyse` that returns structured JSON — severity level, affected service, recommended action — instead of plain text. The frontend renders this as an incident card rather than a chat bubble.

Level 3 adds multi-source integration. The agent gains tools that query Elasticsearch, CloudWatch, and Kubernetes. The runs get longer. This is where background processing becomes relevant.

Level 4 introduces multiple specialist agents coordinated by an orchestrator — each as a separate Agents SDK `Agent` instance, spawned and managed by the orchestrator agent.

The FastAPI + Next.js foundation built in this chapter supports all of it without structural changes.
