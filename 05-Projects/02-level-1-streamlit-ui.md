# Level 1 — Streamlit UI

**Folder:** `01-streamlit-ui/`
**Interface:** Browser via Streamlit
**Goal:** Wrap the terminal agent in a quick chat UI for testing and demos

---

## What This Level Is

Streamlit is a Python framework that turns a script into a web app. No HTML, no JavaScript, no TypeScript. You write Python and get a browser-based chat interface in under 50 lines.

This level is not the production frontend. It is the fastest way to make your agent accessible to non-terminal users — your team, your manager, yourself when you want a nicer interface during development.

**Use Streamlit to validate your agent works with a real UI. Use Next.js when you are ready to make it a product.**

The entire `src/` folder from Level 0 copies over unchanged. Only one new file is added — `app.py`.

---

## What Streamlit Gives You

- `st.chat_message()` — renders chat bubbles automatically
- `st.chat_input()` — input box pinned to the bottom
- `st.session_state` — persists data across reruns within a browser session
- `st.spinner()` — loading indicator while the agent thinks
- `st.sidebar` — side panel for controls and info
- Built-in dark/light theme toggle

No CSS, no components, no build step. Run one command and it opens in your browser.

---

## Folder Structure

```
01-streamlit-ui/
├── app.py               ← new — the entire Streamlit interface
├── src/                 ← copied from Level 0 unchanged
│   ├── __init__.py
│   ├── config.py
│   ├── tools/
│   ├── agents/
│   └── utils/
├── logs/
│   └── sample_app.log
├── pyproject.toml
└── .env
```

---

## pyproject.toml

Add `streamlit` to your dependencies:

```toml
[project]
name = "ai-logging-agent-streamlit"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
    "streamlit",
]
```

---

## app.py — The Complete Streamlit Interface

```python
import asyncio
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import LogAnalyzerAgent
from src.config import Config

st.set_page_config(
    page_title="AI Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        try:
            Config.validate()
            st.session_state.agent = LogAnalyzerAgent()
        except ValueError as e:
            st.error(f"Configuration error: {e}")
            st.stop()

def display_sidebar():
    with st.sidebar:
        st.title("🔍 AI Log Analyzer")
        st.caption("Agents SDK · LiteLLM · Gemini")
        st.markdown("---")

        st.subheader("Try asking")
        examples = [
            "What log files are available?",
            "Read sample_app.log",
            "Search for ERROR in sample_app.log",
            "Summarise everything and save it",
        ]
        for q in examples:
            if st.button(q, use_container_width=True):
                st.session_state.pending_input = q

        st.markdown("---")

        if st.button("🗑️ Clear chat history", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption(f"Model: `{Config.GEMINI_MODEL}`")
        st.caption(f"Logs: `{Config.LOG_DIRECTORY}`")

def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

async def get_response(user_input: str) -> str:
    return await st.session_state.agent.process_query(user_input)

def handle_input(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Analysing..."):
            response = asyncio.run(get_response(user_input))
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    initialize_session_state()
    display_sidebar()

    st.title("💬 Chat with your logs")
    st.markdown("Ask me anything about your log files in plain language.")

    display_messages()

    if "pending_input" in st.session_state and st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = None
        handle_input(pending)

    if prompt := st.chat_input("Ask about your logs..."):
        handle_input(prompt)

if __name__ == "__main__":
    main()
```

---

## How Session State Works Here

Streamlit reruns the entire script on every interaction. `st.session_state` is a dictionary that survives those reruns within a browser tab.

Two things are stored in session state:

**`messages`** — the list of chat messages for display. This is what gets rendered as chat bubbles. When the user clicks "Clear chat history", this list is emptied and the page reruns.

**`agent`** — the `LogAnalyzerAgent` instance. Created once on first load, reused for every subsequent message. Without this, the agent would be recreated on every keypress — wasteful and slow.

When the browser tab closes, everything in session state is gone. This is intentional at Level 1. Persistent storage across sessions is a Level 2 concern.

---

## The Sidebar Example Buttons

The clickable example questions use a pattern with `pending_input`. When a button is clicked, Streamlit reruns the script. The button's `onclick` sets `st.session_state.pending_input` to the question string. On the next rerun, the main function checks for `pending_input`, submits it as if the user typed it, then clears it.

This is the standard Streamlit pattern for sidebar buttons that trigger chat messages.

---

## Run It

```bash
cd 01-streamlit-ui
uv sync
uv run streamlit run app.py
```

Opens at `http://localhost:8501` automatically.

---

## Tests to Run

```
Click "What log files are available?" in the sidebar
Type: Read sample_app.log
Type: Search for ERROR in sample_app.log
Click: Clear chat history → verify conversation resets
Refresh the page → verify messages are gone (expected at this level)
```

---

## Streamlit vs Next.js — When to Use Each

| | Streamlit | Next.js |
|---|---|---|
| Setup time | 5 minutes | 1–2 hours |
| Audience | Technical users | Anyone |
| Customisation | Limited | Full control |
| TypeScript | No | Yes |
| Component architecture | No | Yes |
| Session persistence | Tab only | localStorage + DB |
| Production ready | Prototype | Yes |

Streamlit is the right tool for validating ideas quickly. Next.js is the right tool for building something people will actually use daily.

When your Streamlit prototype works reliably and you know what the interface needs to do — move to Level 2.
