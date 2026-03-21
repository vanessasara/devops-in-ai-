# Building the Components

The book builds a layered architecture using LangChain. This project uses the same layered approach with the same reasoning — but using the OpenAI Agents SDK. The structure is identical. The code inside each layer is simpler.

---

## Why Layers Matter

Everything in one file works until it doesn't. The moment you want to add a tool, change the model, fix a prompt, or add a new API route — you end up reading 400 lines to find the 3 you need to change.

Layers give each concern its own file. Config doesn't know about tools. Tools don't know about the agent. The agent doesn't know about FastAPI. You change one layer without touching the others.

---

## The Six Layers

### Layer 1 — Config

`src/config.py` is the single source of truth for every setting in the project.

It reads environment variables using `python-dotenv`, provides sensible defaults, validates that required values exist before the app starts, and exposes the agent's system prompt as a method.

The key principle: if the API key is missing, the app fails immediately with a clear message — not halfway through an agent run with a cryptic API error. Validation on startup saves debugging time later.

The system prompt lives here rather than inside the agent file. This means you can tune the agent's behaviour — its workflow, its tone, its limitations — without touching any logic code.

### Layer 2 — Tools

`src/tools/log_tools.py` contains every `@function_tool` decorated function.

Each tool is a plain Python function that does one thing. The four tools in this project are `list_log_files`, `read_log_file`, `search_logs`, and `save_summary`.

**Writing good tool docstrings is the most important skill in this layer.** The agent reads the docstring to decide when to call the tool. "List all available log files. Use this first when no filename is given." is an instruction to the model. Write docstrings as if you're telling a colleague when to reach for a particular command.

The `get_log_tools()` function at the bottom returns all tools as a list. The agent layer imports this single function. When you add a new tool, you add it here and to this list — nowhere else changes.

### Layer 3 — Agent

`src/agents/log_analyzer.py` defines the `LogAnalyzerAgent` class.

The `__init__` method creates the `Agent` object — instructions from Config, model from LiteLLM, tools from `get_log_tools()`. This happens once when the class is instantiated.

The `process_query` method calls `Runner.run()` with the user's input and returns `final_output` as a string. That's the entire method. Five lines.

Compare this to the book's LangChain equivalent which manually checks for tool calls, loops through them, finds matching tool functions, executes them, collects results, sends them back to the model, extracts text from various response formats, and updates chat history. The Agents SDK makes all of that invisible.

### Layer 4 — Utils

`src/utils/response.py` contains a single helper that safely extracts text from the Runner result.

`result.final_output` can be `None` if the agent only called tools without producing a text response. The helper handles this case so the calling code never receives `None` or crashes.

### Layer 5 — FastAPI Entry Point

`main.py` at the backend root is where FastAPI lives.

It uses the `lifespan` context manager to create the agent once when the server starts and store it in `app.state.agent`. Every request reuses this instance. This is important — you don't want to reinitialise the model on every HTTP request.

There are two routes. `/chat` accepts a message and returns the agent's response. `/health` returns a status check. That's the entire API surface for Level 1.

CORS middleware is configured here to allow requests from the Next.js frontend. In development this is `localhost:3000`. In production it reads from an environment variable.

### Layer 6 — CLI Entry Point (optional)

`src/main.py` and `src/__main__.py` provide a terminal interface using `python -m src`.

This is the interface described in the book's Chapter 7. It's useful for testing the agent without running the full frontend stack. You can run `uv run python -m src` and chat with the agent directly in the terminal.

---

## What the Book Does Differently

The book's Chapter 7 agent manages its own chat history internally using `InMemoryChatMessageHistory` and `RunnableWithMessageHistory`. Every query passes the full conversation history back into the model.

This project's agent is stateless. `process_query` takes an input string and returns an output string. It remembers nothing between calls. The frontend holds the display history. The agent holds nothing.

This is cleaner for a web interface. State belongs in the layer closest to the user — the frontend — not buried inside business logic.

---

## Chapter 8 — Two Paths

The book's Chapter 8 builds a **Streamlit** web interface.

### Streamlit (book version)

Streamlit is a Python framework that turns a script into a web app. You write Python, it handles the HTML. It's excellent for prototyping and internal tools — you can have a working chat UI in under 50 lines.

**Streamlit is the right choice when:**
- You want to test your backend with a real UI quickly
- The audience is technical (data scientists, DevOps engineers)
- You're prototyping before committing to a full frontend
- You don't want to touch JavaScript

For this project, Streamlit would mean running `streamlit run app.py` and getting a chat interface instantly. No TypeScript, no components, no build step.

### FastAPI + Next.js (this project)

This project replaces Streamlit with a proper full-stack setup — FastAPI as the backend API and Next.js as the frontend.

**This is the right choice when:**
- The tool will be used by non-technical users
- You want full control over the UI
- The project will grow into something production-grade
- You want TypeScript, component architecture, and proper theming

The tradeoff is setup time. The Streamlit version takes 30 minutes. The FastAPI + Next.js version takes a few hours. The result is a significantly more capable and customisable interface.

**Use Streamlit to validate your agent works. Use Next.js when you're ready to make it a real product.**
