# Level 3 — What Was Built

## Project

`03-multi-source/` — standalone Streamlit project. Does not modify Level 0–2 folders.

## What This Level Added

**Decision-making** — the agent classifies severity, recommends a specific action, and asks for human approval before executing anything.

**Severity classification** — P1 critical, P2 high, P3 medium, Info. The agent reasons from log evidence and states justification.

**Human approval gate** — `restart_kubernetes_pod` is only used after an explicit “yes”. The tool docstring and `system_prompt.txt` both enforce this.

**Two-phase response pattern** — Phase 1 ends with “Would you like me to proceed? (yes/no)”. Phase 2 confirms what was done and gives monitoring guidance.

**Kubernetes action tool** — `src/tools/k8s_tools.py`. Default is simulation (`K8S_ENABLED=false`). Set `K8S_ENABLED=true` with a real cluster for live `kubectl`.

**Externalised system prompt** — `system_prompt.txt` at the project root.

## Files Created

- `app.py` — Streamlit UI with severity legend and K8s status in the sidebar
- `system_prompt.txt` — agent instructions (severity rules, two-phase workflow, tools)
- `src/config.py` — loads prompt from file, `K8S_ENABLED`
- `src/tools/log_tools.py` — list/read/search/save (same pattern as Level 0)
- `src/tools/k8s_tools.py` — `restart_kubernetes_pod` with simulation mode
- `src/tools/__init__.py` — `get_all_tools()`
- `src/agents/log_analyzer.py` — `LogAnalyzerAgent` with `get_all_tools()`
- `logs/k8s-java-app.log` — sample OOM / CrashLoopBackOff log

## How to Run

```bash
cd 03-multi-source
# Edit .env and set GEMINI_API_KEY
uv sync
uv run streamlit run app.py
```

## What Level 4 Adds (from notes)

Promote to Next.js + FastAPI, more action tools, structured JSON incident responses. `system_prompt.txt` and `k8s_tools.py` can carry forward.
