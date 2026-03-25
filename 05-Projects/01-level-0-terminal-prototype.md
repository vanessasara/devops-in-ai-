# Level 0 — Terminal Prototype

**Folder:** `00-terminal-prototype/`
**Interface:** Command line only
**Goal:** Prove the agent works before building any UI

---

## What This Level Is

This is where you start. No web interface, no frontend, no HTTP. Just Python, the Agents SDK, and your log files. You type a question. The agent answers. That's it.

The terminal prototype exists to answer one question: **does the agent actually work?** Before you build a UI around something, you need to know the core is solid.

---

## Folder Structure

```
00-terminal-prototype/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── main.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── log_tools.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── log_analyzer.py
│   └── utils/
│       └── response.py
├── logs/
│   └── sample_app.log
├── pyproject.toml
└── .env
```

---

## pyproject.toml

```toml
[project]
name = "ai-logging-agent-terminal"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
]
```

---

## .env

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-3-flash-preview
LOG_DIRECTORY=logs
```

---

## src/config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini/gemini-3-flash-preview")
    LOG_DIRECTORY  = os.getenv("LOG_DIRECTORY", "logs")

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        if not os.path.exists(cls.LOG_DIRECTORY):
            os.makedirs(cls.LOG_DIRECTORY)

    @classmethod
    def get_instructions(cls) -> str:
        return """You are a DevOps expert specializing in log analysis.
- Analyze logs to identify errors, warnings, and patterns
- Explain issues in clear, concise language
- Use list_log_files first if no filename is given
- Use read_log_file to read full contents
- Use search_logs for specific patterns
- Always call save_summary after a full analysis"""
```

---

## src/tools/log_tools.py

```python
import os
from pathlib import Path
from agents import function_tool
from ..config import Config

@function_tool
def list_log_files() -> str:
    """List all available log files. Use this first when no filename is given."""
    files = sorted(Path(Config.LOG_DIRECTORY).glob("*.log"))
    if not files:
        return "No .log files found."
    return "Available files:\n" + "\n".join(
        f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)" for f in files
    )

@function_tool
def read_log_file(filename: str) -> str:
    """Read the full contents of a log file. Input: filename e.g. app.log"""
    path = Path(Config.LOG_DIRECTORY) / filename
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.count("\n") + 1
        return f"File: {filename} | {lines} lines\n\n{content}"
    except FileNotFoundError:
        return f"Error: '{filename}' not found"
    except Exception as e:
        return f"Error: {e}"

@function_tool
def search_logs(filename: str, search_term: str) -> str:
    """Search for a term in a log file. Input: filename, search_term e.g. ERROR"""
    path = Path(Config.LOG_DIRECTORY) / filename
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        matches = [
            f"Line {i}: {line}"
            for i, line in enumerate(lines, 1)
            if search_term.lower() in line.lower()
        ]
        if not matches:
            return f"No matches for '{search_term}' in {filename}"
        return f"Found {len(matches)} matches:\n\n" + "\n".join(matches)
    except FileNotFoundError:
        return f"Error: '{filename}' not found"

@function_tool
def save_summary(summary: str) -> str:
    """Save the final analysis to Summary.md. Always call this after analysis."""
    Path("Summary.md").write_text(
        f"## Log Analysis Summary\n\n{summary}", encoding="utf-8"
    )
    return "Summary saved to Summary.md"

def get_log_tools():
    return [list_log_files, read_log_file, search_logs, save_summary]
```

---

## src/agents/log_analyzer.py

```python
from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from ..config import Config
from ..tools import get_log_tools

set_tracing_disabled(disabled=True)

class LogAnalyzerAgent:
    def __init__(self):
        self.agent = Agent(
            name="DevOps logs analyzer",
            instructions=Config.get_instructions(),
            model=LitellmModel(
                model=Config.GEMINI_MODEL,
                api_key=Config.GEMINI_API_KEY,
            ),
            tools=get_log_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        try:
            result = await Runner.run(self.agent, input=user_input)
            output = getattr(result, "final_output", None)
            return str(output).strip() if output else "No response."
        except Exception as e:
            return f"Error: {e}"
```

---

## src/main.py

```python
import asyncio
from .agents import LogAnalyzerAgent
from .config import Config

def main():
    Config.validate()
    print("=" * 50)
    print("  AI Log Analyzer — Terminal")
    print("  Type 'quit' to exit, 'clear' to reset")
    print("=" * 50)

    agent = LogAnalyzerAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                break
            if user_input.lower() == "clear":
                agent = LogAnalyzerAgent()
                print("Agent reset.")
                continue

            response = asyncio.run(agent.process_query(user_input))
            print(f"\nAgent: {response}")

        except KeyboardInterrupt:
            print("\nType 'quit' to exit.")
        except EOFError:
            break

if __name__ == "__main__":
    main()
```

---

## src/__main__.py

```python
from .main import main
if __name__ == "__main__":
    main()
```

---

## src/tools/__init__.py

```python
from .log_tools import get_log_tools
```

---

## src/agents/__init__.py

```python
from .log_analyzer import LogAnalyzerAgent
```

---

## Sample Log File — logs/sample_app.log

```
[2025-01-15 10:23:45] INFO  Application started
[2025-01-15 10:23:46] INFO  Connected to database on port 5432
[2025-01-15 10:24:12] ERROR Database connection timeout after 30s
[2025-01-15 10:24:13] ERROR Failed to execute query: SELECT * FROM users
[2025-01-15 10:24:14] WARN  Retrying connection attempt 1/3
[2025-01-15 10:24:16] INFO  Connection re-established
[2025-01-15 10:25:01] ERROR API response 500 from payment-service
[2025-01-15 10:25:45] INFO  Payment service recovered
[2025-01-15 10:30:00] INFO  Health check passed
```

---

## Run It

```bash
cd 00-terminal-prototype
uv sync
uv run python -m src
```

---

## Tests to Run Before Moving to Level 1

```
You: What log files are available?
You: Read sample_app.log
You: Search for ERROR in sample_app.log
You: Analyse sample_app.log and save a summary
```

All four must work before you move to Level 1. Check that `Summary.md` was created after the last one.
