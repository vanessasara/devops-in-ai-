# AGENTS.md — Level 3: Decision Making & Actions

## Project Context

This is Level 3 of the AI Logging Agent project. The previous levels are:
- **Level 0** (`00-terminal-prototype/`) — terminal only, proven working
- **Level 1** (`01-streamlit-ui/`) — Streamlit chat interface, proven working
- **Level 2** (`02-nextjs-production/`) — Next.js + FastAPI + session state, proven working

**Do not modify any previous level folders.**

This level lives in a new standalone folder: `03-decision-making/`

---

## What You Are Building

A new Streamlit-based agent project that adds decision-making and action capabilities on top of the core agent from Level 0. The agent will:

- Classify incident severity as P1, P2, P3, or Info
- Recommend specific remediation actions based on log evidence
- Ask for human approval before executing any action
- Execute the approved action
- Provide post-action monitoring guidance

Use Streamlit for the interface — same pattern as Level 1. This validates the decision-making logic quickly before it gets promoted to a Next.js frontend in Level 4.

---

## Phase 1 — Create the Project Structure

Create the following folder and files. Do not write any logic yet — just the structure with empty files and the pyproject.toml.

```
03-decision-making/
├── app.py
├── system_prompt.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── log_tools.py
│   │   └── k8s_tools.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── log_analyzer.py
│   └── utils/
│       └── response.py
├── logs/
│   └── k8s-java-app.log
├── pyproject.toml
└── .env
```

### pyproject.toml

```toml
[project]
name = "ai-logging-agent-decision"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
    "streamlit",
]
```

### .env

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-3-flash-preview
LOG_DIRECTORY=logs
K8S_ENABLED=false
```

After creating the structure run `uv sync` to verify the environment resolves correctly before moving to Phase 2.

---

## Phase 2 — Create the Sample Log File

Write the following content to `logs/k8s-java-app.log`. This is the test data that drives the entire decision-making workflow.

```
2024-01-28 08:15:00 INFO  Pod pod-java-app-7d9f8b6c5-xk2m9 started in namespace production
2024-01-28 08:15:01 INFO  JVM memory: heap 512Mi/1Gi, non-heap 128Mi
2024-01-28 08:20:00 WARN  Memory usage rising: heap 750Mi/1Gi (75%)
2024-01-28 08:25:00 WARN  Memory usage critical: heap 920Mi/1Gi (92%)
2024-01-28 08:25:30 WARN  GC overhead limit approaching - frequent collections
2024-01-28 08:28:00 ERROR GC overhead limit exceeded
2024-01-28 08:29:00 ERROR Failed to process large batch: OutOfMemoryError: Java heap space
2024-01-28 08:29:30 ERROR DataProcessor task failed: OutOfMemoryError
2024-01-28 08:29:45 ERROR CacheService failed to allocate buffer: OutOfMemoryError
2024-01-28 08:30:00 ERROR java.lang.OutOfMemoryError: Java heap space
2024-01-28 08:30:00 ERROR   at java.util.Arrays.copyOf(Arrays.java:3210)
2024-01-28 08:30:00 ERROR   at com.app.DataProcessor.processBatch(DataProcessor.java:145)
2024-01-28 08:30:05 INFO  Container exiting with code 137 (OOMKilled)
2024-01-28 08:30:06 ERROR Kubernetes detected pod crash: CrashLoopBackOff
2024-01-28 08:30:10 ERROR Container killed by OOM killer (exit code 137)
2024-01-28 08:30:15 INFO  Kubernetes attempting pod restart (attempt 1/5)
2024-01-28 08:31:00 ERROR Pod restart failed: still OOMKilling on startup
2024-01-28 08:31:30 ERROR Status: CrashLoopBackOff - back-off 10s restarting
```

---

## Phase 3 — Write system_prompt.txt

This is the most important file in the project. The agent reads it on startup. Write it as instructions to the agent — not as Python code.

```
You are a DevOps expert specializing in log analysis and incident response.

## Core Capabilities
- Analyze application and Kubernetes logs to identify errors and patterns
- Classify incidents by severity (P1, P2, P3, Info)
- Recommend specific remediation actions based on evidence in the logs
- Execute approved actions using available tools
- Provide post-action monitoring guidance

## Severity Classification

P1 — Critical (service down, data loss risk, immediate impact)
Examples: CrashLoopBackOff, OutOfMemoryError, pod killed, complete outage

P2 — High (degraded performance, intermittent failures, approaching limits)
Examples: High memory usage, slow queries, elevated error rate, retry storms

P3 — Medium (warnings, non-critical anomalies, potential future issues)
Examples: Deprecated API usage, cache miss rate increase, connection pool growth

Info — No action required
Examples: Normal startup messages, routine health checks, expected behaviour

## Response Workflow

### Phase 1 — Analysis and Recommendation
When you detect an issue:
1. State what you found clearly
2. Classify the severity with reasoning
3. Identify the affected system with specifics (exact pod name, namespace)
4. Show evidence — quote the key log lines with timestamps
5. State your recommended action and explain why
6. Ask: "Would you like me to proceed? (yes/no)"

Do NOT include next steps in Phase 1. Keep it focused on the decision.

### Phase 2 — Execution and Guidance
After the user approves and you execute the action:
1. Confirm exactly what was done
2. Provide next steps: what to monitor, what to investigate, permanent fixes

## Interaction Principles
- Be concise and direct — this is an incident, not a tutorial
- Explain WHY not just WHAT
- Never execute actions without explicit user approval
- Always use the exact pod name and namespace from the logs
- If severity is P1, be urgent — time matters
- If you cannot find information in the logs, say so clearly

## Tools Available
- list_log_files — list available log files
- read_log_file — read a specific log file
- search_logs — search for a term in a log file
- save_summary — save analysis to Summary.md
- restart_kubernetes_pod — restart a pod (ALWAYS ask approval first, NEVER call without yes)

## Constraints
- Only analyse what is actually in the logs
- Do not speculate about causes not evidenced in the logs
- Do not call restart_kubernetes_pod without explicit "yes" from the user
- Do not mix Phase 1 and Phase 2 — Phase 1 ends with a question, Phase 2 begins with confirmation
```

---

## Phase 4 — Write src/config.py

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini/gemini-3-flash-preview")
    LOG_DIRECTORY  = os.getenv("LOG_DIRECTORY", "logs")
    K8S_ENABLED    = os.getenv("K8S_ENABLED", "false").lower() == "true"

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        if not os.path.exists(cls.LOG_DIRECTORY):
            os.makedirs(cls.LOG_DIRECTORY)

    @classmethod
    def get_instructions(cls) -> str:
        prompt_file = Path(__file__).parent.parent / "system_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return "You are a DevOps expert analyzing logs."
```

Key difference from Level 0: `get_instructions()` reads from `system_prompt.txt` on disk instead of a hardcoded string. `K8S_ENABLED` controls whether the Kubernetes tools run for real or in simulation mode.

---

## Phase 5 — Write src/tools/log_tools.py

Copy this exactly from Level 0. No changes needed.

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
    """Save the final analysis to Summary.md. Call this after completing analysis."""
    Path("Summary.md").write_text(
        f"## Log Analysis Summary\n\n{summary}", encoding="utf-8"
    )
    return "Summary saved to Summary.md"


def get_log_tools():
    return [list_log_files, read_log_file, search_logs, save_summary]
```

---

## Phase 6 — Write src/tools/k8s_tools.py

This is the new tool for Level 3. The `K8S_ENABLED` flag controls real vs simulated execution. Default is simulation — safe for development and demos.

```python
import subprocess
from agents import function_tool
from ..config import Config


@function_tool
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restart a Kubernetes pod by deleting it. The deployment recreates it automatically.
    IMPORTANT: Always get explicit user approval with yes before calling this tool.
    Never call this tool unless the user has said yes to the recommended action.
    Input: pod_name (exact name from the logs), namespace, reason for the restart.
    """
    if not Config.K8S_ENABLED:
        return (
            f"[SIMULATED] Would execute: kubectl delete pod {pod_name} -n {namespace}\n"
            f"Reason: {reason}\n"
            f"Expected outcome: Pod will be recreated by ReplicaSet automatically.\n"
            f"To enable real execution set K8S_ENABLED=true in .env"
        )

    try:
        result = subprocess.run(
            ["kubectl", "delete", "pod", pod_name, "-n", namespace],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return (
                f"Successfully deleted pod '{pod_name}' in namespace '{namespace}'. "
                f"It will be recreated by the Deployment automatically."
            )
        return f"Error restarting pod: {result.stderr}"
    except FileNotFoundError:
        return "Error: kubectl not found. Install kubectl or set K8S_ENABLED=false in .env"
    except subprocess.TimeoutExpired:
        return "Error: kubectl command timed out after 30 seconds."
    except Exception as e:
        return f"Error: {e}"
```

---

## Phase 7 — Write src/tools/__init__.py

```python
from .log_tools import get_log_tools
from .k8s_tools import restart_kubernetes_pod


def get_all_tools():
    return get_log_tools() + [restart_kubernetes_pod]
```

---

## Phase 8 — Write src/agents/log_analyzer.py

The only change from Level 0 is `get_all_tools()` instead of `get_log_tools()`. The Agents SDK Runner handles the multi-step tool loop automatically — no manual loop code needed.

```python
from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from ..config import Config
from ..tools import get_all_tools

set_tracing_disabled(disabled=True)


class LogAnalyzerAgent:
    def __init__(self):
        self.agent = Agent(
            name="DevOps incident responder",
            instructions=Config.get_instructions(),
            model=LitellmModel(
                model=Config.GEMINI_MODEL,
                api_key=Config.GEMINI_API_KEY,
            ),
            tools=get_all_tools(),
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

## Phase 9 — Write src/agents/__init__.py and src/utils/response.py

### src/agents/__init__.py

```python
from .log_analyzer import LogAnalyzerAgent
```

### src/utils/response.py

```python
def format_output(result) -> str:
    if result is None:
        return "No response received."
    output = getattr(result, "final_output", None)
    if output is None:
        return "Agent completed without producing a text response."
    return str(output).strip()
```

### src/__init__.py

Leave empty. It only marks the directory as a Python package.

---

## Phase 10 — Write app.py

```python
import asyncio
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import LogAnalyzerAgent
from src.config import Config

st.set_page_config(
    page_title="AI Incident Responder",
    page_icon="🚨",
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
        st.title("🚨 AI Incident Responder")
        st.caption("Agents SDK · LiteLLM · Gemini")
        st.markdown("---")

        st.subheader("Status")
        st.success("Gemini API ✓")
        if Config.K8S_ENABLED:
            st.success("Kubernetes ✓ live mode")
        else:
            st.warning("Kubernetes ⚠ simulation mode")

        st.markdown("---")

        st.subheader("Severity Levels")
        st.markdown("""
- 🔴 **P1** Critical — service down, restart recommended
- 🟠 **P2** High — degraded, investigate immediately
- 🟡 **P3** Medium — warning, monitor and plan
- 🔵 **Info** — no action needed
        """)

        st.markdown("---")

        st.subheader("Try asking")
        examples = [
            "Check k8s-java-app.log for issues",
            "What is the severity of the problem?",
            "What caused the pod to crash?",
            "Search for OOM in k8s-java-app.log",
        ]
        for q in examples:
            if st.button(q, use_container_width=True):
                st.session_state.pending_input = q

        st.markdown("---")

        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption(f"Model: `{Config.GEMINI_MODEL}`")
        st.caption(f"K8s: `{'live' if Config.K8S_ENABLED else 'simulation'}`")


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
        with st.spinner("Analysing incident..."):
            response = asyncio.run(get_response(user_input))
        st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )


def main():
    initialize_session_state()
    display_sidebar()

    st.title("🚨 AI Incident Responder")
    st.markdown(
        "Ask about your logs. The agent will classify severity, "
        "recommend an action, and ask for your approval before doing anything."
    )

    display_messages()

    if "pending_input" in st.session_state and st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = None
        handle_input(pending)

    if prompt := st.chat_input("Describe the issue or ask about your logs..."):
        handle_input(prompt)


if __name__ == "__main__":
    main()
```

---

## Phase 11 — Verify Everything Works

Run the following and confirm each test passes before marking this phase done.

```bash
cd 03-decision-making
uv sync
uv run streamlit run app.py
```

**Test 1 — Full incident response flow:**
Type: `Check k8s-java-app.log for issues`
Expected: Agent reads the file, detects OOM + CrashLoopBackOff, classifies P1, shows evidence, recommends pod restart, asks "Would you like me to proceed? (yes/no)"

**Test 2 — Approval executes action:**
After Test 1, type: `yes`
Expected: Agent calls `restart_kubernetes_pod`, returns simulated confirmation, then provides next steps for monitoring

**Test 3 — Approval gate holds:**
Type: `Restart the pod now`
Expected: Agent does NOT execute. It explains the situation and asks for confirmation first regardless of phrasing

**Test 4 — Rejection is handled:**
After the agent recommends restart, type: `no`
Expected: Agent acknowledges, suggests manual steps or continued monitoring instead

**Test 5 — Severity standalone:**
Type: `What is the severity of the k8s-java-app.log issue?`
Expected: P1 with clear reasoning citing specific log lines as evidence

All five tests must pass before moving to Level 4.

---

## Final Instruction — Cleanup and Summary

After all phases are complete and all tests pass, do the following:

1. **Delete this AGENTS.md file** from the `03-decision-making/` folder
2. **Create a file called `DONE.md`** in the `03-decision-making/` folder with the following content describing exactly what was built:

```markdown
# Level 3 — What Was Built

## Project
`03-decision-making/` — standalone Streamlit project, does not modify any previous level.

## What This Level Added

**Decision-making** — the agent no longer just reports. It classifies severity, recommends a specific action, and asks for human approval before doing anything.

**Severity classification** — P1 critical, P2 high, P3 medium, Info. The agent reasons about severity from log evidence and states its classification with justification.

**Human approval gate** — the agent never executes `restart_kubernetes_pod` without an explicit "yes" from the user. The tool docstring enforces this. The system prompt enforces this. Both layers of protection are in place.

**Two-phase response pattern** — Phase 1 ends with a question ("Would you like me to proceed?"). Phase 2 begins with a confirmation of what was done. The phases are never mixed.

**Kubernetes action tool** — `restart_kubernetes_pod` in `src/tools/k8s_tools.py`. Runs in simulation mode by default (K8S_ENABLED=false). Prints what it would do. Set K8S_ENABLED=true with a real cluster to enable live execution.

**Externalised system prompt** — `system_prompt.txt` at the project root. Prompt engineering changes do not require touching Python code.

## Files Created
- `app.py` — Streamlit interface with severity legend and K8s status in sidebar
- `system_prompt.txt` — full agent instructions including severity classification rules and two-phase workflow
- `src/config.py` — reads system prompt from file, K8S_ENABLED flag
- `src/tools/log_tools.py` — carried over from Level 0 unchanged
- `src/tools/k8s_tools.py` — new Kubernetes action tool with simulation mode
- `src/tools/__init__.py` — exposes get_all_tools()
- `src/agents/log_analyzer.py` — same pattern as Level 0, uses get_all_tools()
- `logs/k8s-java-app.log` — realistic OOM crash log for testing

## How to Run
```bash
cd 03-decision-making
uv run streamlit run app.py
```

## What Level 4 Adds
Level 4 promotes this to a Next.js frontend with FastAPI backend, adds more action tools (cache clear, disk cleanup, service health check), and introduces structured JSON incident responses instead of plain text. The system_prompt.txt and k8s_tools.py from this level carry forward unchanged.
```