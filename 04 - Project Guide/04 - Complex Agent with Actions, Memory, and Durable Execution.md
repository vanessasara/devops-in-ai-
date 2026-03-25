---
tags: [guide, sdk, openai, temporal, memory, mcp, tools]
---

# Implementation Guide — Complex Agent with Actions, Memory, and Durable Execution

> **Note:** The book this project follows teaches these concepts using LangChain. This guide replaces LangChain entirely with the OpenAI Agents SDK + LiteLLM + Temporal. The concepts are identical. The code is simpler and the execution is production-grade.

---

## The Stack at a Glance

```
OpenAI Agents SDK   → AI reasoning + tool calling loop
LiteLLM             → model bridge (Gemini, OpenAI, Anthropic — one string to change)
@function_tool      → simple tools you own (log reading, pod restart)
MCP                 → complex external tools (AWS RDS, Slack)
SQLite              → pattern memory — outcomes only, not conversations
Temporal            → durable orchestration + human approval + full audit trail
Streamlit           → UI + sends Temporal signals for approval
```

Each piece has one job. None of them overlap. If you want to swap Gemini for Claude, you change one string in `.env`. If you want to swap Streamlit for a REST API, the agent, Temporal workflows, and memory layer don't change.

---

## Tools — Two Kinds

The book chapter puts all tools in one category. In practice, tools split cleanly into two kinds based on one question: do you own the code that runs?

### Simple Tools with `@function_tool`

Use `@function_tool` for anything you own and control directly — reading log files, restarting a pod, saving a summary, querying your own database.

Three things matter when writing a tool:

**The docstring** is what the agent reads to decide when and how to use it. Write it as an instruction to the agent, not a description for a human reader. Compare:

```python
# Bad — describes what the function does
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restarts a Kubernetes pod by deleting it."""

# Good — instructs the agent when and how to use it
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restart a Kubernetes pod by deleting it. The Deployment recreates it automatically.
    IMPORTANT: Only call this after receiving explicit user approval.
    Use the exact pod name and namespace from the logs — never guess these values.
    Input: pod_name (exact name from logs), namespace, reason for restart.
    """
```

**Type hints** are required. The SDK uses them to validate inputs before your function runs. Missing type hints mean unpredictable behavior.

**The return value** is what the agent sees after the tool runs. Make it specific. "Pod deleted" tells the agent nothing. "Successfully deleted pod backend-orders-6f8d7c4b5-n2k8p in namespace production. Deployment will recreate it within 30 seconds." gives the agent enough to reason about what happened.

The real/simulation pattern from the book applies here too. A `K8S_ENABLED` flag controls whether the tool runs real `kubectl` commands or prints a simulation. The agent doesn't know the difference — it calls the tool either way.

```python
from agents import function_tool
from ..config import Config
import subprocess

@function_tool
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restart a Kubernetes pod by deleting it. The Deployment recreates it automatically.
    IMPORTANT: Only call this after receiving explicit user approval.
    Use the exact pod name and namespace from the logs — never guess these values.
    """
    if not Config.K8S_ENABLED:
        return (
            f"[SIMULATED] Would execute: kubectl delete pod {pod_name} -n {namespace}\n"
            f"Reason: {reason}\n"
            f"Expected: Pod will be recreated by Deployment automatically.\n"
            f"Set K8S_ENABLED=true in .env to enable real execution."
        )
    try:
        result = subprocess.run(
            ["kubectl", "delete", "pod", pod_name, "-n", namespace],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return f"Successfully deleted pod '{pod_name}' in namespace '{namespace}'. Will be recreated automatically."
        return f"Error: {result.stderr}"
    except FileNotFoundError:
        return "Error: kubectl not found. Set K8S_ENABLED=false in .env"
    except Exception as e:
        return f"Error: {e}"
```

### Complex Tools via MCP

Use MCP for external services you don't own — AWS, Slack, GitHub, PagerDuty. MCP (Model Context Protocol) is a standard protocol that lets the agent talk to an external service through a server process. You don't write API wrappers. You connect to an MCP server and the agent uses its tools directly.

The Agents SDK supports MCP through `MCPServerStdio`. You point it at an MCP server process, and the agent discovers its tools automatically.

```python
from agents import Agent
from agents.mcp import MCPServerStdio

async def create_agent_with_mcp():
    # Connect to AWS MCP server
    aws_mcp = MCPServerStdio(
        name="aws",
        params={
            "command": "uvx",
            "args": ["awslabs.aws-mcp-server@latest"],
            "env": {
                "AWS_REGION": "us-east-1",
                "AWS_ACCESS_KEY_ID": Config.AWS_ACCESS_KEY_ID,
                "AWS_SECRET_ACCESS_KEY": Config.AWS_SECRET_ACCESS_KEY,
            }
        }
    )

    # Connect to Slack MCP server
    slack_mcp = MCPServerStdio(
        name="slack",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {"SLACK_BOT_TOKEN": Config.SLACK_BOT_TOKEN}
        }
    )

    agent = Agent(
        name="DevOps incident responder",
        instructions=Config.get_instructions(),
        model=LitellmModel(model=Config.GEMINI_MODEL, api_key=Config.GEMINI_API_KEY),
        tools=get_simple_tools(),         # @function_tool decorated functions
        mcp_servers=[aws_mcp, slack_mcp], # MCP servers alongside simple tools
    )
    return agent
```

When MCP servers are not configured (no AWS credentials, no Slack token), the tools aren't available and the agent falls back to its simple tools only. Log this clearly so the developer knows what's active.

**The boundary rule:** if you own the code → `@function_tool`. If it's an external service with an MCP server available → MCP. Never write your own Slack API wrapper when an MCP server exists for it.

---

## The Runner Loop

In LangChain, you write the tool-calling loop manually: check for tool calls, execute them, collect results, feed them back, repeat. In the Agents SDK, `Runner.run()` is the loop. You call it and get back `result.final_output`. The loop is invisible.

What happens inside `Runner.run()`:

```
1. Agent receives input + conversation history
2. LLM reasons and either:
   a. Returns a final answer → Runner returns result.final_output
   b. Returns one or more tool calls → Runner executes them
3. Tool results are fed back to the LLM
4. LLM reasons again → goto 2
```

This continues until the LLM produces a final answer with no tool calls. The SDK handles the iteration, the tool execution, and the message formatting. You handle the logic of what happens before and after.

```python
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

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

    async def analyze(self, user_input: str) -> str:
        result = await Runner.run(self.agent, input=user_input)
        return str(result.final_output).strip()
```

One method. No loop code. No tool dispatch. No message formatting. The SDK handles it.

The book's `_tool_loop`, `_execute_tool_call`, and `extract_response_text` functions — all of that disappears. You get the same behavior with none of the plumbing.

---

## Memory

### Short-Term: Session State

Short-term memory is the current conversation. Streamlit's `session_state` handles it — every message is stored in a list, and the full history is passed to the agent with each new input.

```python
# In app.py — building conversation history for the agent
history = "\n".join([
    f"{m['role'].upper()}: {m['content']}"
    for m in st.session_state.messages
])
full_input = f"{history}\nUSER: {user_input}"

result = await agent.analyze(full_input)
```

This works for the current session. It dies when the tab closes. That's acceptable — Temporal captures the durable state of what actually happened, and SQLite captures the patterns learned from it.

### Long-Term: SQLite for Pattern Recognition

SQLite has one job in this architecture: answer the question "have we seen this before, and how did we fix it?"

It does not store conversations. It does not store raw logs. It stores outcomes — what happened, what the problem type was, and what resolved it. This is institutional memory, not session memory.

**Schema:**

```sql
CREATE TABLE IF NOT EXISTS incidents (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT NOT NULL,
    problem_type TEXT NOT NULL,  -- 'OOM', 'connection_exhaustion', 'crashloop', 'disk_full'
    severity     TEXT NOT NULL,  -- 'P1', 'P2', 'P3'
    pod_name     TEXT,
    summary      TEXT,
    resolution   TEXT            -- what actually fixed it
);

CREATE TABLE IF NOT EXISTS patterns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_type TEXT UNIQUE NOT NULL,
    times_seen   INTEGER DEFAULT 1,
    last_seen    TEXT,
    known_fix    TEXT             -- the fix that worked most often
);
```

Two tables. The `incidents` table is the ledger — every resolved incident gets a row. The `patterns` table is the index — aggregated knowledge about each problem type, updated each time a new incident of that type is resolved.

**Two functions the rest of the system uses:**

```python
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/incidents.db")

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS incidents (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                severity     TEXT NOT NULL,
                pod_name     TEXT,
                summary      TEXT,
                resolution   TEXT
            );
            CREATE TABLE IF NOT EXISTS patterns (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_type TEXT UNIQUE NOT NULL,
                times_seen   INTEGER DEFAULT 1,
                last_seen    TEXT,
                known_fix    TEXT
            );
        """)

def save_incident(problem_type: str, severity: str, pod_name: str,
                  summary: str, resolution: str):
    """Called after an incident is resolved. Writes to both tables."""
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO incidents (timestamp, problem_type, severity, pod_name, summary, resolution) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (now, problem_type, severity, pod_name, summary, resolution)
        )
        conn.execute("""
            INSERT INTO patterns (problem_type, times_seen, last_seen, known_fix)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(problem_type) DO UPDATE SET
                times_seen = times_seen + 1,
                last_seen  = excluded.last_seen,
                known_fix  = excluded.known_fix
        """, (problem_type, now, resolution))

def get_context_for_agent(problem_type: str) -> str:
    """Returns a formatted string injected into the agent's input before analysis."""
    with sqlite3.connect(DB_PATH) as conn:
        pattern = conn.execute(
            "SELECT times_seen, last_seen, known_fix FROM patterns WHERE problem_type = ?",
            (problem_type,)
        ).fetchone()

        recent = conn.execute(
            "SELECT timestamp, pod_name, severity, resolution FROM incidents "
            "WHERE problem_type = ? ORDER BY timestamp DESC LIMIT 3",
            (problem_type,)
        ).fetchall()

    if not pattern:
        return ""

    times_seen, last_seen, known_fix = pattern
    context = f"\n--- PATTERN MEMORY ---\n"
    context += f"Problem type '{problem_type}' has occurred {times_seen} time(s).\n"
    context += f"Last seen: {last_seen}\n"
    if known_fix:
        context += f"Known fix: {known_fix}\n"
    if recent:
        context += "Recent incidents:\n"
        for ts, pod, sev, res in recent:
            context += f"  - {ts} | {pod} | {sev} | resolved: {res}\n"
    context += "--- END MEMORY ---\n"
    return context
```

The `get_context_for_agent()` function returns a block of text. That text gets prepended to the agent's input before every analysis. The agent sees it as part of the conversation — not as a special memory system, just as context it can reference.

---

## Temporal — Durable Execution

### The Problem It Solves

Without Temporal, when your agent does something unexpected, your debugging tools are print statements and hope. You don't know which tool was called, what it returned, whether it ran at all, or where in the sequence things went wrong.

With Temporal, every step of every incident response is recorded. Open the Temporal UI at `localhost:8233`, click on any workflow execution, and see the exact input and output of every activity, every signal received, the full event timeline, and precisely where a failure occurred. You can replay any workflow from any point.

This is the audit trail the book chapter describes as important. Temporal provides it automatically — you don't write logging code for it.

### Three Concepts

**Workflows** are the orchestrators. A workflow defines the sequence of steps for one incident: analyze logs, send alert, wait for approval, execute action, save to SQLite. Workflows must be deterministic — no I/O, no random numbers, no direct API calls. All real work happens in Activities.

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class IncidentResponseWorkflow:
    def __init__(self):
        self.approval_decision: str | None = None  # 'approved' or 'rejected'

    @workflow.run
    async def run(self, incident_input: str) -> str:
        # Step 1 — analyze
        diagnosis = await workflow.execute_activity(
            analyze_logs_activity,
            incident_input,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Step 2 — alert team
        await workflow.execute_activity(
            send_slack_alert_activity,
            diagnosis,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Step 3 — wait for human approval (durably — no CPU consumed while waiting)
        await workflow.wait_condition(
            lambda: self.approval_decision is not None,
            timeout=timedelta(minutes=30),
        )

        if self.approval_decision != "approved":
            return f"Incident acknowledged. No action taken. Decision: {self.approval_decision}"

        # Step 4 — execute action
        result = await workflow.execute_activity(
            execute_action_activity,
            diagnosis,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Step 5 — save pattern to SQLite
        await workflow.execute_activity(
            save_incident_activity,
            {"diagnosis": diagnosis, "result": result},
            start_to_close_timeout=timedelta(seconds=10),
        )

        return result
```

**Activities** are where real work happens. Every tool call, every API call, every database write is an activity. They get automatic retries. If Slack is down, Temporal retries the notification without you writing a single retry line. Each activity is a plain async function decorated with `@activity.defn`.

```python
from temporalio import activity

@activity.defn
async def analyze_logs_activity(incident_input: str) -> str:
    """Runs the AI agent. Returns the diagnosis as a string."""
    agent = LogAnalyzerAgent()
    return await agent.analyze(incident_input)

@activity.defn
async def send_slack_alert_activity(diagnosis: str) -> str:
    """Sends a Slack alert. Retried automatically if Slack is unavailable."""
    # MCP Slack tool call or placeholder
    return await send_slack(diagnosis)

@activity.defn
async def execute_action_activity(diagnosis: str) -> str:
    """Executes the remediation action. Retried on transient failures."""
    return await execute_remediation(diagnosis)

@activity.defn
async def save_incident_activity(data: dict) -> str:
    """Writes the resolved incident to SQLite."""
    save_incident(
        problem_type=data["problem_type"],
        severity=data["severity"],
        pod_name=data["pod_name"],
        summary=data["diagnosis"],
        resolution=data["result"],
    )
    return "Saved"
```

**Signals** are how the UI talks to a running workflow. When the user types "yes" in Streamlit, the app sends a signal to the workflow via the Temporal client. The workflow is paused at `wait_condition()`, consuming zero CPU. The signal arrives, the condition becomes true, and the workflow continues.

```python
# In the workflow class — receives the signal
@workflow.signal
async def approval_decision(self, decision: str):
    """Called by the UI when the user approves or rejects."""
    self.approval_decision = decision

# In app.py — sends the signal from the UI
async def send_approval(workflow_id: str, decision: str):
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("approval_decision", decision)
```

### How It Wraps Your Agent

One incident = one Workflow execution. The agent lives inside an Activity. The Workflow orchestrates the sequence around it.

```
Workflow: IncidentResponseWorkflow
    │
    ├─ Activity: analyze_logs          ← Runner.run() happens here
    │       returns: diagnosis string
    │
    ├─ Activity: send_slack_alert      ← MCP Slack tool
    │       retries: 3x on failure
    │
    ├─ Signal wait: approval_decision  ← UI sends "approved" or "rejected"
    │       timeout: 30 minutes        ← auto-resolves if no response
    │
    ├─ Activity: execute_action        ← RDS reboot via MCP / k8s restart
    │       retries: 3x on failure
    │
    └─ Activity: save_incident         ← SQLite pattern memory updated
```

Every box in this diagram is a recorded step in the Temporal UI.

### Running Locally

Temporal's dev server runs with one command. No Docker, no configuration files, no external dependencies. It persists state to an in-memory SQLite database and resets on restart — fine for development.

```bash
# Terminal 1 — start Temporal dev server
temporal server start-dev
# UI available at localhost:8233

# Terminal 2 — start the worker (polls for workflow/activity tasks)
uv run python worker.py

# Terminal 3 — start the Streamlit app
uv run streamlit run app.py
```

The worker is a separate process that registers your workflows and activities with the Temporal server. When a workflow is started, the server assigns tasks to the worker. The worker executes activities and reports results back.

```python
# worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from src.workflows.incident_workflow import IncidentResponseWorkflow
from src.workflows.activities import (
    analyze_logs_activity,
    send_slack_alert_activity,
    execute_action_activity,
    save_incident_activity,
)

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="incident-response",
        workflows=[IncidentResponseWorkflow],
        activities=[
            analyze_logs_activity,
            send_slack_alert_activity,
            execute_action_activity,
            save_incident_activity,
        ],
    )
    print("Worker started. Waiting for tasks...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### What You Can Debug in the Temporal UI

Open `localhost:8233` after starting the dev server. Every workflow execution appears as a row. Click any execution to see:

- **Event history** — every state transition in the workflow, timestamped
- **Activity inputs and outputs** — exactly what each activity received and returned
- **Signal history** — when the approval signal arrived, what value it carried
- **Failure details** — if an activity failed, the full stack trace and retry count
- **Timeline view** — visual representation of the workflow execution

When the agent does something unexpected, this is your first stop. You don't need to add logging code. Temporal records everything.

---

## The Approval Gate — Three Layers

The book chapter uses a string check (`is_confirmation()`) as the approval gate. That works for a prototype. This architecture has three layers, each catching a different failure mode.

**Layer 1 — System prompt.** The agent is instructed never to call dangerous tools without explicit user approval. This is the first line of defense — the LLM's own reasoning.

**Layer 2 — Tool docstring.** The `restart_kubernetes_pod` and RDS reboot tool docstrings both say "IMPORTANT: Only call this after receiving explicit user approval." The agent reads this every time it considers calling the tool. This catches cases where the system prompt context gets diluted in a long conversation.

**Layer 3 — Temporal Signal.** The workflow literally cannot proceed past the `wait_condition()` step until a signal arrives. Even if both Layer 1 and Layer 2 failed — even if the agent called the activity — the workflow is paused. No signal, no action. This is the hard gate.

Three layers because each protects against a different failure: LLM hallucination, context dilution, and code-level bugs.

---

## What's Next

The implementation guide covers the concepts. The project guide gives you the exact file-by-file build spec.

All the patterns here — MCP tools, SQLite memory, Temporal orchestration, the three-layer approval gate — are designed with the future dashboard in mind. The dashboard will feed live log data to the agent as incident input. The Temporal workflow, SQLite memory layer, and approval gate don't change when the dashboard arrives. They plug in as the input layer. Everything else stays the same.
