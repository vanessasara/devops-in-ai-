# Level 3 — Decision Making & Actions

Level 3 is where the agent stops being passive. Levels 0, 1, and 2 built an agent that reads logs and answers questions. That's useful. But when a pod is in CrashLoopBackOff at 2 AM, you don't just want analysis — you need the agent to tell you exactly what to do and then do it.

This level adds severity classification, action recommendations, a human approval gate, and action execution. The interface is Streamlit — fast to run, easy to demo, no build step.

---

## What It Does

You ask the agent to check a log file. It reads the file, identifies the issue, classifies the severity, shows you the evidence, recommends a specific action, and asks if you want it to proceed. You say yes. It executes. Then it tells you what to monitor next.

A complete incident response workflow — detection, classification, recommendation, execution, and follow-up — in a single conversation.

---

## The Two-Phase Response Pattern

This is the most important concept in Level 3.

**Phase 1** ends with a question:

```
Issue Summary: Pod experiencing OutOfMemoryError in CrashLoopBackOff

Severity: P1 — Critical

Analysis:
- Pod: pod-java-app-7d9f8b6c5-xk2m9 in namespace production
- Root cause: Memory usage (1.02Gi) exceeded limit (1Gi)
- Impact: Complete service outage
- Evidence:
  08:30:00 ERROR OutOfMemoryError: Java heap space
  08:30:06 ERROR Kubernetes detected pod crash: CrashLoopBackOff
  08:30:10 ERROR Container killed by OOM killer (exit code 137)

Recommended Action: Restart the pod to clear memory state and restore service.

Would you like me to proceed? (yes/no)
```

**Phase 2** begins with a confirmation:

```
I have restarted pod-java-app-7d9f8b6c5-xk2m9 in namespace production.

Next Steps:
- Monitor pod memory usage — watch for it approaching 1Gi again
- Investigate memory leak in DataProcessor and CacheService
- Consider increasing memory limit from 1Gi to 2Gi permanently
```

Phase 1 is focused on the decision. Phase 2 is focused on what comes next. They are never mixed.

---

## Severity Levels

| Level | Meaning | Example | Action |
|---|---|---|---|
| 🔴 P1 | Critical — service down | CrashLoopBackOff, OOMKilled | Restart recommended immediately |
| 🟠 P2 | High — degraded | Memory at 92%, elevated error rate | Investigate immediately |
| 🟡 P3 | Medium — warning | Cache miss rate rising, slow queries | Monitor and plan |
| 🔵 Info | No action needed | Normal startup, health checks | None |

---

## The Human Approval Gate

The agent **never** executes an action without an explicit "yes". This is enforced at two layers:

1. The `restart_kubernetes_pod` tool docstring says "Always get explicit user approval before calling this tool"
2. The system prompt says "Do not call restart_kubernetes_pod without explicit yes from the user"

If you tell the agent "restart the pod now" without it first recommending the action, it will still ask for confirmation before doing anything. The gate cannot be bypassed by phrasing.

---

## Stack

| Part | Technology |
|---|---|
| Agent framework | OpenAI Agents SDK |
| Model | Gemini via LiteLLM |
| Interface | Streamlit |
| Package manager | uv |

---

## Project Structure

```
03-decision-making/
├── app.py                 ← Streamlit chat interface
├── system_prompt.txt      ← agent instructions (edit without touching Python)
├── src/
│   ├── config.py          ← env vars, K8s flag, prompt file loader
│   ├── tools/
│   │   ├── log_tools.py   ← read, list, search, save (carried from Level 0)
│   │   └── k8s_tools.py   ← restart_kubernetes_pod with simulation mode
│   └── agents/
│       └── log_analyzer.py
├── logs/
│   └── k8s-java-app.log   ← sample OOM crash log for testing
├── pyproject.toml
└── .env
```

---

## Setup

```bash
cd 03-decision-making
cp .env.example .env
# add your GEMINI_API_KEY to .env
uv sync
uv run streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Environment Variables

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-3-flash-preview
LOG_DIRECTORY=logs
K8S_ENABLED=false
```

`K8S_ENABLED=false` runs all Kubernetes actions in simulation mode — the agent prints exactly what it would do without touching any real infrastructure. Set to `true` only when you have `kubectl` configured and a real cluster available.

---

## Try It

**Full incident response:**
```
You: Check k8s-java-app.log for issues
Agent: [classifies P1, shows evidence, recommends restart, asks approval]
You: yes
Agent: [executes restart, provides next steps]
```

**Rejection flow:**
```
You: Check k8s-java-app.log for issues
Agent: [recommends restart, asks approval]
You: no
Agent: [acknowledges, suggests manual steps instead]
```

**Direct severity question:**
```
You: What is the severity of the issue in k8s-java-app.log?
Agent: [P1 with reasoning from specific log lines]
```

---

## The system_prompt.txt File

Unlike previous levels where the system prompt was a Python string, Level 3 externalises it to `system_prompt.txt`. This means you can iterate on the agent's behaviour — change its tone, adjust severity thresholds, add new decision rules — without touching any Python code.

The file defines the severity classification rules, the two-phase response workflow, the approval requirement, and the constraints the agent must follow.

---

## Simulation vs Live Mode

The `restart_kubernetes_pod` tool has two modes controlled by `K8S_ENABLED` in `.env`.

**Simulation mode** (`K8S_ENABLED=false`):
```
[SIMULATED] Would execute: kubectl delete pod pod-java-app-7d9f8b6c5-xk2m9 -n production
Reason: OutOfMemoryError recovery
Expected outcome: Pod will be recreated by ReplicaSet automatically.
```

**Live mode** (`K8S_ENABLED=true`):
Runs `kubectl delete pod <name> -n <namespace>` for real. Requires `kubectl` installed and configured with access to the target cluster.

Start in simulation mode. Validate the entire workflow. Switch to live only when you trust the agent's judgment.

---

## What Level 4 Adds

Level 4 promotes this project to a Next.js frontend with a FastAPI backend. It adds more action tools — cache clearing, disk cleanup, service health checks — and introduces structured JSON incident responses that the frontend renders as formatted incident cards instead of plain chat text.

The `system_prompt.txt` and `k8s_tools.py` from this level carry forward to Level 4 unchanged.
