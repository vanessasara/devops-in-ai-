# AGENTS.md — Level 4: Complex Agent with Actions, Memory, and Durable Execution

## Project Context

This is Level 4 of the AI Logging Agent project. The previous levels are:
- **Level 0** (`00-terminal-prototype/`) — terminal only, proven working
- **Level 1** (`01-streamlit-ui/`) — Streamlit chat interface, proven working
- **Level 2** (`02-nextjs-production/`) — Next.js + FastAPI + session state, proven working
- **Level 3** (`03-decision-making/`) — severity classification + human approval gate, proven working

**Do not modify any previous level folders.**

This level lives in a new standalone folder: `04-complex-agent/`

---

## What You Are Building

A production-grade incident response agent that handles a complete multi-step workflow:

- Reads and correlates logs across multiple pods
- Detects patterns like connection pool exhaustion across the whole cluster
- Sends structured Slack alerts via MCP before proposing any action
- Reboots AWS RDS instances via MCP after human approval
- Uses Temporal to orchestrate every step durably — every action is recorded, retried on failure, and visible in the Temporal UI
- Uses a Temporal Signal for the human approval gate — the workflow pauses durably until the user types yes
- Writes resolved incidents to SQLite for pattern recognition — the next time the same problem occurs, the agent knows it has seen it before

The scenario is a three-tier AWS application: Java Spring Boot backend on EKS, RDS MySQL, Redis ElastiCache. Three backend pods each have a HikariCP connection pool of 50. The RDS instance is `db.t3.medium` with a max of 150 connections. When all three pods max out simultaneously, the database hits its connection ceiling, orders fail, and the entire pipeline stalls.

---

## Phase 1 — Create the Project Structure

Create the following folder and files. Do not write any logic yet — just the structure with empty files and the pyproject.toml.

```
04-complex-agent/
├── app.py                         # Streamlit UI + Temporal client
├── worker.py                      # Temporal worker process
├── system_prompt.txt              # Agent instructions
├── pyproject.toml
├── .env.example
├── data/                          # SQLite database lives here (gitignored)
├── logs/
│   ├── backend-orders-pod1.log
│   ├── backend-orders-pod2.log
│   └── backend-orders-pod3.log
└── src/
    ├── __init__.py
    ├── config.py
    ├── memory/
    │   ├── __init__.py
    │   └── sqlite_store.py        # save_incident, get_context_for_agent
    ├── tools/
    │   ├── __init__.py
    │   ├── log_tools.py           # @function_tool — log reading
    │   ├── k8s_tools.py           # @function_tool — pod restart
    │   └── mcp_tools.py           # MCP client setup for AWS + Slack
    ├── agents/
    │   ├── __init__.py
    │   └── log_analyzer.py        # Agent + Runner
    └── workflows/
        ├── __init__.py
        ├── activities.py          # @activity.defn functions
        └── incident_workflow.py   # @workflow.defn
```

### pyproject.toml

```toml
[project]
name = "ai-logging-agent-complex"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "temporalio",
    "python-dotenv",
    "streamlit",
]
```

### .env.example

```
# Model
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2.5-flash

# AWS (optional — placeholder mode if not set)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_RDS_INSTANCE_ID=orders-db-prod

# Slack (optional — placeholder mode if not set)
SLACK_BOT_TOKEN=
SLACK_CHANNEL=#devops-alerts

# Kubernetes (optional — simulation mode if false)
K8S_ENABLED=false

# Temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_TASK_QUEUE=incident-response

# Paths
LOG_DIRECTORY=logs
DB_PATH=data/incidents.db
```

After creating the structure, run `uv sync` to verify the environment resolves correctly before moving to Phase 2.

---

## Phase 2 — Create the Log Files

Write the following content to each log file. These simulate the connection exhaustion scenario across three pods.

### logs/backend-orders-pod1.log

```
2024-02-06 09:00:00 INFO  [main] SpringApplication - Starting OrderService v2.1.0 on backend-orders-6f8d7c4b5-n2k8p
2024-02-06 09:00:05 INFO  [main] HikariDataSource - HikariPool-1 - Start completed. Pool size: 10, Max pool size: 50
2024-02-06 09:00:08 INFO  [main] DatabaseConfig - Connected to RDS: orders-db.c9aksj2x.us-east-1.rds.amazonaws.com:3306/orders_prod
2024-02-06 10:00:00 WARN  [http-nio-8080-exec-8] HikariPool - HikariPool-1 - Connection pool nearing capacity (35/50 active)
2024-02-06 10:10:00 WARN  [http-nio-8080-exec-15] HikariPool - HikariPool-1 - Connection pool nearing capacity (45/50 active)
2024-02-06 10:12:45 ERROR [http-nio-8080-exec-18] HikariPool - HikariPool-1 - Connection is not available, request timed out after 30000ms
2024-02-06 10:12:45 ERROR [http-nio-8080-exec-18] OrderService - Failed to process order #ORD-2024-78234: Unable to acquire JDBC Connection
2024-02-06 10:12:45 ERROR [http-nio-8080-exec-18] Caused by: SQLNonTransientConnectionException: Too many connections
2024-02-06 10:13:30 ERROR [connection-monitor] DATABASE CONNECTION EXHAUSTION DETECTED - RDS: orders-db.c9aksj2x.us-east-1.rds.amazonaws.com
2024-02-06 10:13:30 ERROR [connection-monitor] Max connections: 150 (db.t3.medium), Active: 150/150
2024-02-06 10:13:30 ERROR [connection-monitor] Total pods connected: 3 (pod1: 50, pod2: 50, pod3: 50)
2024-02-06 10:13:35 FATAL [main] OrderServiceApplication - Service unable to serve requests. All database connections exhausted.
```

### logs/backend-orders-pod2.log

```
2024-02-06 09:00:01 INFO  [main] SpringApplication - Starting OrderService v2.1.0 on backend-orders-6f8d7c4b5-p9x3q
2024-02-06 09:00:06 INFO  [main] HikariDataSource - HikariPool-1 - Start completed. Pool size: 10, Max pool size: 50
2024-02-06 09:00:09 INFO  [main] DatabaseConfig - Connected to RDS: orders-db.c9aksj2x.us-east-1.rds.amazonaws.com:3306/orders_prod
2024-02-06 10:00:02 WARN  [http-nio-8080-exec-6] HikariPool - HikariPool-1 - Connection pool nearing capacity (33/50 active)
2024-02-06 10:11:00 WARN  [http-nio-8080-exec-12] HikariPool - HikariPool-1 - Connection pool nearing capacity (47/50 active)
2024-02-06 10:12:50 ERROR [http-nio-8080-exec-20] HikariPool - HikariPool-1 - Connection is not available, request timed out after 30000ms
2024-02-06 10:12:50 ERROR [http-nio-8080-exec-20] OrderService - Failed to process order #ORD-2024-78235: Unable to acquire JDBC Connection
2024-02-06 10:12:50 ERROR [http-nio-8080-exec-20] Caused by: SQLNonTransientConnectionException: Too many connections
2024-02-06 10:13:31 ERROR [connection-monitor] All 50 connections exhausted on pod2. Orders failing.
2024-02-06 10:13:36 FATAL [main] OrderServiceApplication - Service unable to serve requests. All database connections exhausted.
```

### logs/backend-orders-pod3.log

```
2024-02-06 09:00:02 INFO  [main] SpringApplication - Starting OrderService v2.1.0 on backend-orders-6f8d7c4b5-r7m2w
2024-02-06 09:00:07 INFO  [main] HikariDataSource - HikariPool-1 - Start completed. Pool size: 10, Max pool size: 50
2024-02-06 09:00:10 INFO  [main] DatabaseConfig - Connected to RDS: orders-db.c9aksj2x.us-east-1.rds.amazonaws.com:3306/orders_prod
2024-02-06 10:00:04 WARN  [http-nio-8080-exec-4] HikariPool - HikariPool-1 - Connection pool nearing capacity (31/50 active)
2024-02-06 10:11:30 WARN  [http-nio-8080-exec-11] HikariPool - HikariPool-1 - Connection pool nearing capacity (48/50 active)
2024-02-06 10:12:55 ERROR [http-nio-8080-exec-22] HikariPool - HikariPool-1 - Connection is not available, request timed out after 30000ms
2024-02-06 10:12:55 ERROR [http-nio-8080-exec-22] OrderService - Failed to process order #ORD-2024-78236: Unable to acquire JDBC Connection
2024-02-06 10:12:55 ERROR [http-nio-8080-exec-22] Caused by: SQLNonTransientConnectionException: Too many connections
2024-02-06 10:13:32 ERROR [connection-monitor] All 50 connections exhausted on pod3. Orders failing.
2024-02-06 10:13:37 FATAL [main] OrderServiceApplication - Service unable to serve requests. All database connections exhausted.
```

---

## Phase 3 — Write system_prompt.txt

```
You are a senior DevOps engineer AI agent. You think and act like an experienced on-call engineer: read logs, correlate evidence across systems, diagnose root causes, take action, and communicate clearly.

You are monitoring a three-tier AWS application:
- Backend: Java Spring Boot pods on EKS with HikariCP connection pools
- Database: RDS MySQL (orders-db-prod, db.t3.medium, 150 max connections)
- Cache: Redis ElastiCache

## Severity Classification

P1 — Critical: service down, orders failing, immediate action required
P2 — High: degraded performance, approaching limits, investigate now
P3 — Medium: warnings, non-critical anomalies, monitor and plan
Info — No action required

## Response Workflow

### Phase 1 — Analysis and Alert
When you detect an issue:
1. Read all available logs before drawing conclusions
2. Correlate evidence across pods — this is often a cluster-wide issue, not a single pod
3. State what you found with specific evidence: timestamps, pod names, error messages, counts
4. Classify severity with reasoning
5. Alert the team via Slack before proposing any remediation
6. State your recommended action and explain why
7. Ask: "Would you like me to proceed? (yes/no)"

### Phase 2 — Execution and Follow-up
After the user approves:
1. Execute the action
2. Confirm exactly what was done with specifics
3. Provide monitoring guidance and permanent fix recommendations

## Tool Usage Rules
- Always read all log files before concluding anything
- Send Slack alert before recommending any infrastructure action
- NEVER call reboot_rds_instance without explicit "yes" from the user
- NEVER call restart_kubernetes_pod without explicit "yes" from the user
- Use exact pod names, namespace, and instance IDs from the logs — never invent them
- If severity is P1, be urgent — every minute of downtime has business impact

## Communication Style
- Evidence-driven: cite timestamps, pod names, error messages, counts
- Concise: this is an incident, not a tutorial
- Specific: "pod1: 50/50, pod2: 50/50, pod3: 50/50, RDS: 150/150" not "all connections used"
- If something is not in the logs, say so — do not speculate
```

---

## Phase 4 — Write src/config.py

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Model
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash")

    # AWS
    AWS_REGION           = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID    = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_RDS_INSTANCE_ID  = os.getenv("AWS_RDS_INSTANCE_ID", "")

    # Slack
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL   = os.getenv("SLACK_CHANNEL", "#devops-alerts")

    # Kubernetes
    K8S_ENABLED = os.getenv("K8S_ENABLED", "false").lower() == "true"

    # Temporal
    TEMPORAL_HOST       = os.getenv("TEMPORAL_HOST", "localhost:7233")
    TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "incident-response")

    # Paths
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
    DB_PATH       = Path(os.getenv("DB_PATH", "data/incidents.db"))

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        if not Path(cls.LOG_DIRECTORY).exists():
            Path(cls.LOG_DIRECTORY).mkdir(parents=True)
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def aws_configured(cls) -> bool:
        return bool(cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY)

    @classmethod
    def slack_configured(cls) -> bool:
        return bool(cls.SLACK_BOT_TOKEN)

    @classmethod
    def get_instructions(cls) -> str:
        prompt_file = Path(__file__).parent.parent / "system_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return "You are a senior DevOps engineer analyzing logs."
```

---

## Phase 5 — Write src/memory/sqlite_store.py

```python
import sqlite3
from datetime import datetime
from ..config import Config


def init_db():
    """Create tables if they don't exist. Call once on startup."""
    with sqlite3.connect(Config.DB_PATH) as conn:
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
    """Write a resolved incident. Updates the patterns table automatically."""
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(Config.DB_PATH) as conn:
        conn.execute(
            "INSERT INTO incidents (timestamp, problem_type, severity, pod_name, summary, resolution) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (now, problem_type, severity, pod_name, summary, resolution),
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
    """Return a formatted string to prepend to the agent's input.
    Returns empty string if no history exists for this problem type.
    """
    with sqlite3.connect(Config.DB_PATH) as conn:
        pattern = conn.execute(
            "SELECT times_seen, last_seen, known_fix FROM patterns WHERE problem_type = ?",
            (problem_type,),
        ).fetchone()

        recent = conn.execute(
            "SELECT timestamp, pod_name, severity, resolution FROM incidents "
            "WHERE problem_type = ? ORDER BY timestamp DESC LIMIT 3",
            (problem_type,),
        ).fetchall()

    if not pattern:
        return ""

    times_seen, last_seen, known_fix = pattern
    lines = [
        "\n--- PATTERN MEMORY ---",
        f"Problem type '{problem_type}' has occurred {times_seen} time(s).",
        f"Last seen: {last_seen}",
    ]
    if known_fix:
        lines.append(f"Known fix: {known_fix}")
    if recent:
        lines.append("Recent incidents:")
        for ts, pod, sev, res in recent:
            lines.append(f"  - {ts} | pod: {pod} | severity: {sev} | fix: {res}")
    lines.append("--- END MEMORY ---\n")
    return "\n".join(lines)
```

---

## Phase 6 — Write src/tools/log_tools.py

Copy from Level 3 unchanged.

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
    """Read the full contents of a log file. Input: filename e.g. backend-orders-pod1.log"""
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
    """Search for a term in a log file. Input: filename, search_term"""
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


def get_log_tools():
    return [list_log_files, read_log_file, search_logs]
```

---

## Phase 7 — Write src/tools/k8s_tools.py

Copy from Level 3 unchanged.

```python
import subprocess
from agents import function_tool
from ..config import Config


@function_tool
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restart a Kubernetes pod by deleting it. The Deployment recreates it automatically.
    IMPORTANT: Only call this after receiving explicit user approval — the user must have said yes.
    Use the exact pod name and namespace from the logs. Never guess these values.
    Input: pod_name (exact name), namespace, reason for restart.
    """
    if not Config.K8S_ENABLED:
        return (
            f"[SIMULATED] Would execute: kubectl delete pod {pod_name} -n {namespace}\n"
            f"Reason: {reason}\n"
            f"Expected: Pod will be recreated by Deployment automatically.\n"
            f"Set K8S_ENABLED=true to enable real execution."
        )
    try:
        result = subprocess.run(
            ["kubectl", "delete", "pod", pod_name, "-n", namespace],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return f"Successfully deleted pod '{pod_name}' in '{namespace}'. Will be recreated automatically."
        return f"Error: {result.stderr}"
    except FileNotFoundError:
        return "Error: kubectl not found. Set K8S_ENABLED=false in .env"
    except subprocess.TimeoutExpired:
        return "Error: kubectl timed out after 30 seconds."
    except Exception as e:
        return f"Error: {e}"
```

---

## Phase 8 — Write src/tools/mcp_tools.py

MCP tools for AWS RDS and Slack. When credentials are not configured, the functions return placeholder strings — the agent still sees a response and can complete its reasoning.

```python
from ..config import Config


async def reboot_rds_instance(instance_id: str, reason: str) -> str:
    """Reboot an AWS RDS instance. Called by the execute_action activity.
    Uses real AWS API if credentials are configured, placeholder otherwise.
    """
    if not Config.aws_configured():
        return (
            f"[SIMULATED] Would reboot RDS instance '{instance_id}'\n"
            f"AWS CLI equivalent: aws rds reboot-db-instance --db-instance-identifier {instance_id}\n"
            f"Reason: {reason}\n"
            f"Expected downtime: 1-3 minutes. All existing connections will be dropped.\n"
            f"Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env for real execution."
        )
    try:
        import boto3
        rds = boto3.client("rds", region_name=Config.AWS_REGION)
        response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
        status = response["DBInstances"][0]["DBInstanceStatus"]
        if status != "available":
            return f"Cannot reboot '{instance_id}'. Current status: {status}. Must be 'available'."
        rds.reboot_db_instance(DBInstanceIdentifier=instance_id)
        return (
            f"Successfully initiated reboot of RDS instance '{instance_id}' in {Config.AWS_REGION}.\n"
            f"Reason: {reason}\n"
            f"Expected downtime: 1-3 minutes. All connections will be dropped and re-established."
        )
    except Exception as e:
        return f"AWS error: {e}"


async def send_slack_notification(channel: str, summary: str,
                                  severity: str, details: str) -> str:
    """Send an incident notification to Slack.
    Uses real Slack API if bot token is configured, placeholder otherwise.
    """
    if not Config.slack_configured():
        print(f"\n[SLACK PLACEHOLDER]")
        print(f"  Channel: {channel}")
        print(f"  Severity: {severity}")
        print(f"  Summary: {summary}")
        print(f"  Details: {details}\n")
        return f"[SIMULATED] Slack notification sent to {channel}. Set SLACK_BOT_TOKEN for real delivery."
    try:
        import httpx
        payload = {
            "channel": channel,
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": f"[{severity}] {summary}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": details}},
            ]
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {Config.SLACK_BOT_TOKEN}"},
                json=payload,
            )
        data = resp.json()
        if data.get("ok"):
            return f"Slack notification sent to {channel}."
        return f"Slack error: {data.get('error', 'unknown')}"
    except Exception as e:
        return f"Slack error: {e}"
```

---

## Phase 9 — Write src/tools/__init__.py

```python
from .log_tools import get_log_tools
from .k8s_tools import restart_kubernetes_pod


def get_all_tools():
    return get_log_tools() + [restart_kubernetes_pod]
```

---

## Phase 10 — Write src/agents/log_analyzer.py

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

    async def analyze(self, user_input: str) -> str:
        """Run the agent on user_input. Returns final_output as a string."""
        try:
            result = await Runner.run(self.agent, input=user_input)
            output = getattr(result, "final_output", None)
            return str(output).strip() if output else "No response."
        except Exception as e:
            return f"Agent error: {e}"
```

---

## Phase 11 — Write src/workflows/activities.py

Each function is a Temporal Activity. All real work happens here — AI analysis, Slack alerts, RDS reboots, SQLite writes. The workflow only sequences them.

```python
from temporalio import activity
from dataclasses import dataclass
from ..agents.log_analyzer import LogAnalyzerAgent
from ..tools.mcp_tools import reboot_rds_instance, send_slack_notification
from ..memory.sqlite_store import save_incident
from ..config import Config


@dataclass
class IncidentData:
    problem_type: str
    severity: str
    pod_name: str
    summary: str
    resolution: str


@activity.defn
async def analyze_logs_activity(incident_input: str) -> str:
    """Run the AI agent on the incident input. Returns diagnosis as a string."""
    agent = LogAnalyzerAgent()
    return await agent.analyze(incident_input)


@activity.defn
async def send_slack_alert_activity(diagnosis: str) -> str:
    """Send a Slack alert with the diagnosis. Retried automatically on failure."""
    return await send_slack_notification(
        channel=Config.SLACK_CHANNEL,
        summary="Production incident detected",
        severity="P1",
        details=diagnosis,
    )


@activity.defn
async def execute_rds_reboot_activity(instance_id: str) -> str:
    """Reboot the RDS instance. Only called after human approval signal is received."""
    return await reboot_rds_instance(
        instance_id=instance_id,
        reason="Connection pool exhaustion — all 150 connections consumed across 3 pods",
    )


@activity.defn
async def save_incident_activity(data: dict) -> str:
    """Write the resolved incident to SQLite. Updates pattern recognition table."""
    save_incident(
        problem_type=data.get("problem_type", "unknown"),
        severity=data.get("severity", "P1"),
        pod_name=data.get("pod_name", ""),
        summary=data.get("summary", ""),
        resolution=data.get("resolution", ""),
    )
    return "Incident saved to pattern memory."
```

---

## Phase 12 — Write src/workflows/incident_workflow.py

This is the orchestrator. It sequences activities, handles the Signal from the UI, and manages the 30-minute approval timeout.

```python
from temporalio import workflow
from datetime import timedelta
from .activities import (
    analyze_logs_activity,
    send_slack_alert_activity,
    execute_rds_reboot_activity,
    save_incident_activity,
)


@workflow.defn
class IncidentResponseWorkflow:

    def __init__(self):
        # Approval decision sent by the UI via Signal.
        # None = not yet received. "approved" or "rejected" = decision made.
        self.approval_decision: str | None = None

    @workflow.signal
    async def approve(self, decision: str):
        """Receives approval decision from the Streamlit UI.
        Called when the user types yes or no in the chat.
        decision: "approved" or "rejected"
        """
        self.approval_decision = decision

    @workflow.run
    async def run(self, incident_input: str) -> str:

        # Step 1 — AI analysis
        diagnosis = await workflow.execute_activity(
            analyze_logs_activity,
            incident_input,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=workflow.RetryPolicy(maximum_attempts=2),
        )

        # Step 2 — Alert team via Slack before any action
        await workflow.execute_activity(
            send_slack_alert_activity,
            diagnosis,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )

        # Step 3 — Wait for human approval (durably — zero CPU consumed while waiting)
        # Workflow pauses here until the UI sends a Signal or 30 minutes elapse.
        try:
            await workflow.wait_condition(
                lambda: self.approval_decision is not None,
                timeout=timedelta(minutes=30),
            )
        except Exception:
            # Timeout reached — no decision received
            return (
                "Incident acknowledged and team alerted. "
                "No action taken — approval timed out after 30 minutes."
            )

        if self.approval_decision != "approved":
            return (
                f"Incident acknowledged and team alerted. "
                f"No action taken — decision: {self.approval_decision}."
            )

        # Step 4 — Execute remediation
        from ..config import Config
        result = await workflow.execute_activity(
            execute_rds_reboot_activity,
            Config.AWS_RDS_INSTANCE_ID,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )

        # Step 5 — Save to SQLite pattern memory
        await workflow.execute_activity(
            save_incident_activity,
            {
                "problem_type": "connection_exhaustion",
                "severity": "P1",
                "pod_name": "backend-orders (3 pods)",
                "summary": diagnosis[:500],
                "resolution": result[:200],
            },
            start_to_close_timeout=timedelta(seconds=10),
        )

        return result
```

---

## Phase 13 — Write worker.py

The worker is a separate process. It registers workflows and activities with Temporal and polls for tasks. Start this before the Streamlit app.

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from src.config import Config
from src.workflows.incident_workflow import IncidentResponseWorkflow
from src.workflows.activities import (
    analyze_logs_activity,
    send_slack_alert_activity,
    execute_rds_reboot_activity,
    save_incident_activity,
)


async def main():
    client = await Client.connect(Config.TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=Config.TEMPORAL_TASK_QUEUE,
        workflows=[IncidentResponseWorkflow],
        activities=[
            analyze_logs_activity,
            send_slack_alert_activity,
            execute_rds_reboot_activity,
            save_incident_activity,
        ],
    )
    print(f"Worker started on task queue '{Config.TEMPORAL_TASK_QUEUE}'")
    print("Waiting for workflow tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Phase 14 — Write app.py

The Streamlit app has two jobs: start new Temporal workflow executions when the user describes an incident, and send approval Signals when the user types yes or no.

```python
import asyncio
import uuid
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from temporalio.client import Client
from src.config import Config
from src.memory.sqlite_store import init_db

st.set_page_config(
    page_title="AI Incident Responder",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

CONFIRMATIONS = {"yes", "y", "confirm", "approve", "go ahead", "do it", "ok", "proceed"}
REJECTIONS    = {"no", "n", "cancel", "reject", "stop", "abort"}


def is_confirmation(text: str) -> bool:
    return text.strip().lower().rstrip("!.,") in CONFIRMATIONS


def is_rejection(text: str) -> bool:
    return text.strip().lower().rstrip("!.,") in REJECTIONS


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "workflow_id" not in st.session_state:
        st.session_state.workflow_id = None
    if "awaiting_approval" not in st.session_state:
        st.session_state.awaiting_approval = False
    try:
        Config.validate()
        init_db()
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.stop()


def sidebar():
    with st.sidebar:
        st.title("🚨 AI Incident Responder")
        st.caption("Agents SDK · LiteLLM · Temporal · SQLite")
        st.markdown("---")

        st.subheader("Status")
        st.success("Gemini API ✓")
        st.success("Temporal ✓") if True else st.error("Temporal ✗")
        st.success("AWS ✓") if Config.aws_configured() else st.warning("AWS ⚠ simulation")
        st.success("Slack ✓") if Config.slack_configured() else st.warning("Slack ⚠ simulation")
        st.success("K8s ✓ live") if Config.K8S_ENABLED else st.warning("K8s ⚠ simulation")

        st.markdown("---")
        st.subheader("Temporal UI")
        st.markdown("[Open localhost:8233](http://localhost:8233)")
        if st.session_state.workflow_id:
            st.caption(f"Current workflow: `{st.session_state.workflow_id[:16]}...`")

        st.markdown("---")
        st.subheader("Try asking")
        examples = [
            "Analyze all backend pod logs for issues",
            "Check backend-orders-pod1.log",
            "Search for connection errors across all pods",
        ]
        for q in examples:
            if st.button(q, use_container_width=True):
                st.session_state.pending_input = q

        st.markdown("---")
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.workflow_id = None
            st.session_state.awaiting_approval = False
            st.rerun()


async def start_workflow(user_input: str) -> tuple[str, str]:
    """Start a new Temporal workflow. Returns (workflow_id, initial_response)."""
    client = await Client.connect(Config.TEMPORAL_HOST)
    workflow_id = f"incident-{uuid.uuid4().hex[:12]}"

    # Import here to avoid circular imports at module level
    from src.workflows.incident_workflow import IncidentResponseWorkflow

    handle = await client.start_workflow(
        IncidentResponseWorkflow.run,
        user_input,
        id=workflow_id,
        task_queue=Config.TEMPORAL_TASK_QUEUE,
    )
    return workflow_id, f"Workflow started: `{workflow_id}`\nAnalyzing incident... (check Temporal UI for live progress)"


async def send_signal(workflow_id: str, decision: str) -> str:
    """Send approval signal to the running workflow."""
    client = await Client.connect(Config.TEMPORAL_HOST)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("approve", decision)
    return f"Signal sent: **{decision}**. Workflow continuing..."


def handle_input(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # If workflow is running and waiting for approval
            if st.session_state.awaiting_approval and st.session_state.workflow_id:
                if is_confirmation(user_input):
                    response = asyncio.run(
                        send_signal(st.session_state.workflow_id, "approved")
                    )
                    st.session_state.awaiting_approval = False
                elif is_rejection(user_input):
                    response = asyncio.run(
                        send_signal(st.session_state.workflow_id, "rejected")
                    )
                    st.session_state.awaiting_approval = False
                else:
                    response = "Waiting for your approval. Type **yes** to proceed or **no** to cancel."
            else:
                # Start a new workflow
                workflow_id, response = asyncio.run(start_workflow(user_input))
                st.session_state.workflow_id = workflow_id
                st.session_state.awaiting_approval = True

        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    init_session()
    sidebar()

    st.title("🚨 AI Incident Responder")
    st.markdown(
        "Describe a production incident. The agent will analyze logs, alert your team, "
        "and ask for your approval before taking any action. "
        "Every step is recorded in Temporal."
    )

    display_messages()

    if "pending_input" in st.session_state and st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = None
        handle_input(pending)

    if prompt := st.chat_input("Describe the incident or ask about your logs..."):
        handle_input(prompt)


if __name__ == "__main__":
    main()
```

---

## Phase 15 — Verify Everything Works

### Prerequisites

Install the Temporal CLI if you haven't already:

```bash
# macOS
brew install temporal

# Or via script
curl -sSf https://temporal.download/cli.sh | sh
```

### Start Everything

Three terminals, in this order:

```bash
# Terminal 1 — Temporal dev server (no Docker needed)
temporal server start-dev
# UI: http://localhost:8233

# Terminal 2 — Worker (must be running before starting workflows)
cd 04-complex-agent
uv sync
uv run python worker.py

# Terminal 3 — Streamlit app
cd 04-complex-agent
uv run streamlit run app.py
```

### Five Tests — All Must Pass

**Test 1 — Full incident detection:**
Type: `Analyze all backend pod logs for issues`
Expected: Agent reads all three log files, correlates the evidence across pods, identifies connection exhaustion as P1, sends Slack alert (simulated), states the RDS reboot recommendation with specific evidence (pod names, connection counts, timestamps), asks "Would you like me to proceed? (yes/no)"
Also verify: Temporal UI at `localhost:8233` shows the workflow execution in progress, `analyze_logs_activity` and `send_slack_alert_activity` both completed.

**Test 2 — Approval executes the action:**
After Test 1, type: `yes`
Expected: Approval signal sent to the workflow. Workflow continues. `execute_rds_reboot_activity` runs (simulated). `save_incident_activity` runs and writes to SQLite. Agent provides confirmation and monitoring guidance.
Also verify: Temporal UI shows all activities completed. Workflow status is Completed.

**Test 3 — Rejection is handled cleanly:**
Start a new analysis, then type: `no`
Expected: Signal sent with "rejected". Workflow ends cleanly. Agent acknowledges and suggests manual steps. No RDS action taken.
Also verify: Temporal UI shows workflow completed with rejection path.

**Test 4 — Pattern recognition on second incident:**
After Tests 1 and 2, type: `Analyze all backend pod logs for issues` again
Expected: Agent's analysis mentions that connection exhaustion has been seen before and includes the known fix from the first incident. The pattern memory context is visible in the response.

**Test 5 — Temporal UI debugging:**
Go to `localhost:8233`. Click on any completed workflow.
Expected: Full event history visible. Each activity shows input and output. Signals show when they arrived and what value they carried. You can see the exact moment the workflow paused at `wait_condition` and the exact moment the approval signal arrived.

All five tests must pass before marking this level complete.

---

## Final Instruction — Cleanup and Summary

After all phases are complete and all tests pass:

1. **Delete this AGENTS.md file** from the `04-complex-agent/` folder
2. **Create DONE.md** with the following content:

```markdown
# Level 4 — What Was Built

## Project
`04-complex-agent/` — standalone project, does not modify any previous level.

## What This Level Added

**Multi-pod log correlation** — the agent reads all three pod logs before drawing any conclusions. Connection exhaustion is a cluster-wide failure, not a single-pod issue. The agent treats it that way.

**MCP tools** — AWS RDS reboot and Slack notifications are connected via MCP. No custom API wrappers. When credentials are not configured, both tools fall back to placeholder mode automatically.

**SQLite pattern memory** — two tables: `incidents` and `patterns`. One job: answer "have we seen this before?" The agent receives relevant pattern history as context before every analysis. Pattern memory is updated after every resolved incident.

**Temporal durable execution** — every incident response is a Temporal Workflow. Every tool call is an Activity with automatic retries. The human approval gate is a Temporal Signal — the workflow pauses durably at `wait_condition()` until the user responds or 30 minutes elapse. Every step is recorded and visible in the Temporal UI at localhost:8233.

**Three-layer approval gate** — system prompt (agent instruction), tool docstring (second enforcement), Temporal Signal (hard gate). The workflow cannot execute the RDS reboot unless the Signal arrives.

**Full audit trail** — open Temporal UI, click any workflow, see every activity input/output, every signal, every failure, the complete event timeline. No logging code required.

## How to Run

Three terminals:
```bash
temporal server start-dev          # Terminal 1
uv run python worker.py            # Terminal 2
uv run streamlit run app.py        # Terminal 3
```

## Files
- `app.py` — Streamlit UI, starts workflows, sends approval signals
- `worker.py` — Temporal worker, registers workflows and activities
- `system_prompt.txt` — agent instructions
- `src/config.py` — all env vars, placeholder detection
- `src/memory/sqlite_store.py` — incident and pattern tables
- `src/tools/log_tools.py` — log reading (@function_tool)
- `src/tools/k8s_tools.py` — pod restart (@function_tool)
- `src/tools/mcp_tools.py` — AWS RDS + Slack (placeholder when not configured)
- `src/agents/log_analyzer.py` — Agent + Runner
- `src/workflows/activities.py` — Temporal activities
- `src/workflows/incident_workflow.py` — Temporal workflow with Signal handler

## What Level 5 Adds
Level 5 promotes the frontend to Next.js with a real-time dashboard that feeds live log streams to the agent as incident inputs. The Temporal workflow, SQLite memory, and approval gate carry forward unchanged.
```
