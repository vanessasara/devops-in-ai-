# Level 3 — Decision Making & Actions

**Folder:** `03-decision-making/`
**Interface:** Streamlit UI (new project, do not modify Level 2)
**Builds on:** Level 2 concepts, new standalone project
**Goal:** Agent that classifies severity, recommends actions, and executes with human approval

---

## What This Level Adds

Level 2 was passive — the agent read logs and reported what it found. Level 3 makes the agent active. It now:

- **Classifies severity** — P1 critical, P2 high, P3 medium, Info
- **Recommends specific actions** — restart pod, investigate memory, scale service
- **Asks for approval before acting** — never executes blindly
- **Executes the action** — after confirmation
- **Provides next steps** — what to monitor and how to prevent recurrence

The interface for this level is **Streamlit**. This is intentional. Streamlit lets you validate the decision-making workflow quickly before investing in a full Next.js frontend. Prove the logic works here, then promote it to Level 4.

---

## Project Structure

```
03-decision-making/
├── app.py                   ← Streamlit interface
├── system_prompt.txt        ← agent instructions as a text file
├── src/
│   ├── __init__.py
│   ├── config.py            ← updated with K8s config + prompt loader
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── log_tools.py     ← carried over from Level 0
│   │   └── k8s_tools.py     ← new — kubernetes action tools
│   ├── agents/
│   │   ├── __init__.py
│   │   └── log_analyzer.py  ← updated with multi-step tool loop
│   └── utils/
│       └── response.py
├── logs/
│   └── k8s-java-app.log     ← new realistic OOM crash log
├── pyproject.toml
└── .env
```

---

## pyproject.toml

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

---

## .env

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-3-flash-preview
LOG_DIRECTORY=logs
K8S_ENABLED=false
```

`K8S_ENABLED=false` means all Kubernetes actions run as safe placeholders — they print what they would do without touching real infrastructure. Set to `true` only when you have a real cluster configured.

---

## system_prompt.txt

The system prompt is externalised to a text file. This means you can tune agent behaviour without touching Python code. Prompt engineering is iterative — keeping it in a file makes that workflow faster.

```
You are a DevOps expert specializing in log analysis and incident response.

## Core Capabilities
- Analyze application and Kubernetes logs to identify errors and patterns
- Classify incidents by severity (P1, P2, P3, Info)
- Recommend specific remediation actions based on what you find
- Execute approved actions using available tools
- Provide post-action monitoring guidance

## Severity Classification

P1 — Critical (service down, data loss risk, security breach)
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
3. Identify the affected system with specifics (pod name, namespace, service)
4. Show evidence — quote the key log lines with timestamps
5. State your recommended action and why
6. Ask: "Would you like me to proceed? (yes/no)"

Do NOT include next steps in Phase 1. Keep it focused on the decision.

### Phase 2 — Execution and Guidance
After the user approves and you execute the action:
1. Confirm what was done
2. Provide next steps: what to monitor, what to investigate, permanent fixes to consider

## Interaction Principles
- Be concise and direct — this is an incident, not a tutorial
- Explain WHY, not just WHAT
- Never execute actions without explicit user approval
- Always use the exact pod name and namespace from the logs
- If severity is P1, be urgent — time matters
- If you cannot find the information in the logs, say so clearly

## Tools Available
- list_log_files — list available log files
- read_log_file — read a specific log file
- search_logs — search for a term in a log file
- save_summary — save analysis to Summary.md
- restart_kubernetes_pod — restart a pod (ALWAYS ask approval first)

## Constraints
- Only analyse what is actually in the logs
- Do not speculate about causes not evidenced in the logs
- Do not execute restart_kubernetes_pod without explicit "yes" from the user
- Focus on actionable insights, not general advice
```

---

## logs/k8s-java-app.log

Create this file to test the decision-making workflow:

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
2024-01-28 08:30:00 ERROR 	at java.util.Arrays.copyOf(Arrays.java:3210)
2024-01-28 08:30:00 ERROR 	at com.app.DataProcessor.processBatch(DataProcessor.java:145)
2024-01-28 08:30:05 INFO  Container exiting with code 137 (OOMKilled)
2024-01-28 08:30:06 ERROR Kubernetes detected pod crash: CrashLoopBackOff
2024-01-28 08:30:10 ERROR Container killed by OOM killer (exit code 137)
2024-01-28 08:30:15 INFO  Kubernetes attempting pod restart (attempt 1/5)
2024-01-28 08:31:00 ERROR Pod restart failed: still OOMKilling on startup
2024-01-28 08:31:30 ERROR Status: CrashLoopBackOff - back-off 10s restarting
```

---

## src/config.py

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

The key addition here is `get_instructions()` reading from `system_prompt.txt` instead of a hardcoded string. If the file doesn't exist it falls back gracefully.

---

## src/tools/k8s_tools.py

```python
from agents import function_tool
from ..config import Config

@function_tool
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restart a Kubernetes pod by deleting it. The deployment recreates it automatically.
    IMPORTANT: Always ask for explicit user approval before calling this tool.
    Input: pod_name (exact name from logs), namespace, reason for restart.
    """
    if not Config.K8S_ENABLED:
        return (
            f"[SIMULATED] Would execute: kubectl delete pod {pod_name} -n {namespace}\n"
            f"Reason: {reason}\n"
            f"Expected: Pod will be recreated by ReplicaSet automatically.\n"
            f"To enable real execution set K8S_ENABLED=true in .env"
        )

    # Real implementation — only runs when K8S_ENABLED=true
    import subprocess
    try:
        result = subprocess.run(
            ["kubectl", "delete", "pod", pod_name, "-n", namespace],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return f"Successfully deleted pod '{pod_name}' in namespace '{namespace}'. It will be recreated automatically."
        return f"Error restarting pod: {result.stderr}"
    except FileNotFoundError:
        return "Error: kubectl not found. Install kubectl or set K8S_ENABLED=false."
    except subprocess.TimeoutExpired:
        return "Error: kubectl command timed out after 30 seconds."
    except Exception as e:
        return f"Error: {e}"
```

The placeholder vs real execution is controlled by `K8S_ENABLED`. This means you can develop, test, and demo safely without a cluster. The tool description explicitly tells the agent to always ask for approval — the agent reads this.

---

## src/tools/__init__.py

```python
from .log_tools import get_log_tools
from .k8s_tools import restart_kubernetes_pod

def get_all_tools():
    return get_log_tools() + [restart_kubernetes_pod]
```

---

## src/agents/log_analyzer.py

The critical change in Level 3 is the **multi-step tool execution loop**. Level 2's agent ran tools once and returned. Level 3's agent needs to:

1. Call `read_log_file` — get the logs
2. Analyse — produce recommendation and ask for approval
3. User says yes
4. Call `restart_kubernetes_pod` — execute
5. Produce post-action guidance

This requires the Runner to handle multiple tool calls in sequence, which the Agents SDK does automatically. Your `process_query` method stays the same — just update the agent definition to use `get_all_tools()`.

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

The only change from Level 2 is `get_all_tools()` instead of `get_log_tools()`. The Runner handles the multi-step loop automatically.

---

## app.py — Streamlit Interface

The Streamlit UI carries over from Level 1 with small additions: a sidebar section showing severity levels and Kubernetes status.

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
            st.success("Kubernetes ✓ (live)")
        else:
            st.warning("Kubernetes ⚠ (simulation mode)")

        st.markdown("---")

        st.subheader("Severity Levels")
        st.markdown("""
- 🔴 **P1** — Critical, service down → auto-restart recommended
- 🟠 **P2** — High, degraded → investigate immediately
- 🟡 **P3** — Medium, warning → monitor and plan
- 🔵 **Info** — No action needed
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
        st.caption(f"K8s mode: `{'live' if Config.K8S_ENABLED else 'simulation'}`")

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
    st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    initialize_session_state()
    display_sidebar()

    st.title("🚨 AI Incident Responder")
    st.markdown("Paste a question or use the examples in the sidebar. The agent will classify severity, recommend action, and ask for your approval before doing anything.")

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

## Run It

```bash
cd 03-decision-making
uv sync
uv run streamlit run app.py
```

---

## Test Walkthrough

**Test 1 — Full incident response flow:**
```
You: Check k8s-java-app.log for issues
```
Agent should: read the file → detect OOM + CrashLoopBackOff → classify P1 → show evidence → recommend pod restart → ask for approval

```
You: yes
```
Agent should: call `restart_kubernetes_pod` → confirm execution → provide next steps

**Test 2 — Approval gate:**
```
You: Restart the pod immediately
```
Agent should NOT restart. It should ask for confirmation first regardless of how the request is phrased.

**Test 3 — Rejection:**
```
You: Check k8s-java-app.log for issues
Agent: [recommends restart, asks approval]
You: no
```
Agent should acknowledge the decision and suggest manual steps or monitoring instead.

**Test 4 — Severity check:**
```
You: What severity is this incident?
```
Agent should classify P1 with clear reasoning from the log evidence.

---

## The Two-Phase Response Pattern

This is the most important concept in Level 3.

**Phase 1** — delivered before any action:
- What is wrong
- Severity classification with reasoning
- Evidence from the logs
- Recommended action
- Request for approval

**Phase 2** — delivered after action executes:
- Confirmation of what was done
- What to monitor now
- How to prevent recurrence
- Permanent fixes to consider

Never mix them. Phase 1 should end with a question. Phase 2 should begin with a confirmation. This keeps responses focused and prevents information overload during an active incident.

---

## What Changes in Level 4

Level 4 promotes this project to a Next.js frontend with FastAPI backend, adds more action tools (cache clear, disk cleanup, service health check), and introduces the structured JSON response format — severity, affected system, and recommended action as structured data rather than plain text.

The `system_prompt.txt`, `k8s_tools.py`, and `log_analyzer.py` from this level carry forward unchanged.