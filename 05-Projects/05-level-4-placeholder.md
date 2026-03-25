# Level 4 — Multi-Agent System

**Folder:** `04-multi-agent/`
**Status:** Coming later
**Builds on:** Level 3 (Multi-Source)

---

## What This Level Will Add

Level 4 replaces the single do-everything agent with a team of specialist agents coordinated by an orchestrator.

Instead of one agent that handles application logs, infrastructure logs, and security logs — you have three separate agents, each an expert in their domain. An orchestrator receives the user's question, decides which specialist to involve, dispatches tasks in parallel, collects findings, and synthesises the final answer.

---

## The Agent Team

**Orchestrator** — receives the user question, breaks it into sub-tasks, dispatches to specialists, merges findings

**App Agent** (`app_agent`) — specialist in application-level logs, error patterns, stack traces

**Infra Agent** (`infra_agent`) — specialist in infrastructure logs, system metrics, resource exhaustion

**Security Agent** (`security_agent`) — specialist in authentication failures, anomalous access patterns, threat indicators

---

## How This Uses Claude Code Patterns

Each specialist agent is defined by a `SKILL.md` file — a markdown document describing the agent's persona, available tools, and expected output format. The orchestrator reads the relevant SKILL.md before spawning a subagent.

Subagents run via the Agents SDK's handoff mechanism — the orchestrator passes control to a specialist, the specialist completes its task, and control returns to the orchestrator with the result.

A shared JSON scratchpad (controlled by the orchestrator) stores intermediate findings. Specialists can read from it but only the orchestrator writes final conclusions. This prevents conflicting writes when agents run in parallel.

---

## What Changes vs Level 3

- Three new `Agent` instances in addition to the orchestrator
- New `SKILL.md` files defining each specialist
- Orchestrator logic that routes questions to the right specialist
- Parallel execution where multiple specialists analyse different sources simultaneously
- Frontend gains a workflow view showing which agents ran and what each found

---

## This Folder Will Contain

```
04-multi-agent/
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── orchestrator.py    ← new
│   │   │   ├── app_agent.py       ← new
│   │   │   ├── infra_agent.py     ← new
│   │   │   └── security_agent.py  ← new
│   │   └── skills/
│   │       ├── app_agent.md       ← SKILL.md for app agent
│   │       ├── infra_agent.md     ← SKILL.md for infra agent
│   │       └── security_agent.md  ← SKILL.md for security agent
│   └── main.py
└── frontend/
    └── components/
        └── chat/
            └── agent-trace.tsx    ← shows which agents ran
```

---

## OWASP Security Considerations at This Level

With multiple agents communicating, the attack surface grows. Level 4 must implement:

- **ASI04 Delegated Trust** — validate messages between orchestrator and subagents
- **ASI07 Inter-Agent Comms** — authenticate all agent-to-agent communication
- **ASI10 Rogue Agents** — kill switches on every agent process

See the Level 5 OWASP notes for the full security layer.

---

## Prerequisites Before Starting Level 4

- Level 3 must be fully working with at least two live log sources
- Understanding of the Agents SDK handoff mechanism
- Clear definition of what each specialist agent's domain is for your specific use case
- Monitoring in place to observe agent behaviour before adding autonomy
