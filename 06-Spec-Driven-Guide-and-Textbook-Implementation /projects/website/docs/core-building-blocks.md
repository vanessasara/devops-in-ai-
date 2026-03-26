---
title: Core Building Blocks of Agentic Systems
slug: core-building-blocks
reading_time: 15
tags: [architecture, orchestration, tools]
---

import ChapterContent from '@site/src/components/ChapterContent';

<ChapterContent slug="core-building-blocks">

# Core Building Blocks of Agentic Systems



## Architecture Overview

Agentic systems are built from composable blocks. Understanding these components is essential for designing effective agents.

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Memory    │  │   Planner   │  │   Tool Registry     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Worker Agent  │    │ Worker Agent  │    │ Worker Agent  │
│   (Triage)    │    │   (Build)     │    │   (Deploy)    │
│               │    │               │    │               │
│  ┌─────────┐  │    │  ┌─────────┐  │    │  ┌─────────┐  │
│  │  Tools  │  │    │  │  Tools  │  │    │  │  Tools  │  │
│  └─────────┘  │    │  └─────────┘  │    │  └─────────┘  │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Orchestrator Agents

The **orchestrator** is the brain of the system. It:

1. Receives high-level goals
2. Decomposes goals into subtasks
3. Delegates to specialized worker agents
4. Monitors progress and handles failures
5. Aggregates results

### Orchestrator Responsibilities

```python
class OrchestratorAgent:
    """Coordinates multiple specialized agents."""

    def __init__(self):
        self.memory = MemorySystem()
        self.planner = Planner()
        self.workers = WorkerRegistry()

    async def execute(self, goal: str) -> Result:
        # 1. Plan decomposition
        plan = await self.planner.create_plan(goal)

        # 2. Execute plan with worker agents
        results = []
        for task in plan.tasks:
            worker = self.workers.get(task.agent_type)
            result = await worker.execute(task)
            results.append(result)

            # 3. Handle failures
            if not result.success:
                recovery_plan = await self.planner.recover(result.error)
                results.append(await self.execute(recovery_plan))

        # 4. Aggregate and return
        return self.aggregate(results)
```

### Decision Making

Orchestrators decide:

- **Which agent** should handle each task
- **When** to retry vs. escalate
- **How** to handle dependencies between tasks
- **What** to report to humans

## Worker Agents

**Worker agents** are specialists. They have narrow scope but deep capability in their domain.

### Worker Agent Pattern

```python
class WorkerAgent:
    """Specialized agent for a specific domain."""

    def __init__(self, domain: str, tools: list[Tool]):
        self.domain = domain
        self.tools = {tool.name: tool for tool in tools}

    async def execute(self, task: Task) -> Result:
        # 1. Validate task is in domain
        if not self.can_handle(task):
            return Result.error(f"Task outside {self.domain} domain")

        # 2. Select appropriate tools
        selected_tools = self.select_tools(task)

        # 3. Execute tool sequence
        context = {}
        for tool_name in selected_tools:
            tool = self.tools[tool_name]
            context = await tool.execute(task, context)

        return Result.success(context)
```

### Worker Examples

| Worker Type | Domain | Tools | Example Task |
|-------------|--------|-------|--------------|
| **Triage** | Incident classification | PagerDuty API, log parser | "Classify this alert" |
| **Build** | CI/CD build stage | Docker, package managers | "Build the service" |
| **Deploy** | Deployment operations | kubectl, Helm, ArgoCD | "Deploy to staging" |
| **Monitor** | Observability | Prometheus, Grafana API | "Check service health" |

## Memory Systems

Agents need **memory** to maintain context, learn from experience, and make better decisions.

### Types of Memory

```
┌─────────────────────────────────────────────────────────┐
│                    Memory Types                         │
├─────────────────────────────────────────────────────────┤
│  Working Memory    │  Current conversation/task context │
├─────────────────────────────────────────────────────────┤
│  Episodic Memory   │  Past interactions and outcomes     │
├─────────────────────────────────────────────────────────┤
│  Semantic Memory   │  Facts and knowledge about systems  │
├─────────────────────────────────────────────────────────┤
│  Procedural Memory │  How to perform specific tasks      │
└─────────────────────────────────────────────────────────┘
```

### Memory Implementation

```python
class MemorySystem:
    """Manages different types of agent memory."""

    def __init__(self):
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()

    def add_observation(self, observation: str):
        """Add to working memory."""
        self.working.add(observation)

    def recall_similar(self, situation: str) -> list[Episode]:
        """Find similar past situations."""
        return self.episodic.search(situation)

    def learn_procedure(self, task: str, steps: list):
        """Store how to accomplish a task."""
        self.semantic.store(task, steps)
```

### Memory in Action

```python
# Agent using memory to improve decisions
async def handle_incident(self, alert: Alert):
    # Check working memory for current context
    context = self.memory.working.get_context()

    # Recall similar past incidents
    similar_incidents = self.memory.recall_similar(
        alert.description
    )

    if similar_incidents:
        # Use learned procedures
        procedure = self.memory.semantic.get_procedure(
            similar_incidents[0].resolution_type
        )
        return await self.execute_procedure(procedure)
    else:
        # Novel situation - use reasoning
        return await self.reason_and_act(alert)
```

## Tool Use

**Tools** are how agents interact with the world. Every tool has:

1. **Name**: Identifier for the tool
2. **Schema**: Input/output specification
3. **Execute**: The actual operation
4. **Constraints**: Limitations and requirements

### Tool Schema Definition

```python
from pydantic import BaseModel
from typing import Literal

class KubectlToolSchema(BaseModel):
    """Schema for kubectl tool."""

    command: Literal["get", "describe", "logs", "apply", "delete"]
    resource: str
    namespace: str = "default"
    output: Literal["json", "yaml", "wide"] = "json"

class KubectlTool(Tool):
    name = "kubectl"
    description = "Execute kubectl commands against Kubernetes cluster"
    input_schema = KubectlToolSchema

    async def execute(self, params: KubectlToolSchema) -> ToolResult:
        # Validate permissions
        if not self.has_permission(params.command):
            return ToolResult.error("Insufficient permissions")

        # Execute command
        result = await self.run_kubectl(params)

        return ToolResult.success(result)
```

### Tool Registry

Agents maintain a **registry** of available tools:

```python
class ToolRegistry:
    """Manages available tools for an agent."""

    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.permissions: dict[str, list[str]] = {}

    def register(self, tool: Tool, allowed_actions: list[str]):
        self.tools[tool.name] = tool
        self.permissions[tool.name] = allowed_actions

    def get(self, tool_name: str) -> Tool:
        return self.tools.get(tool_name)

    def list_available(self) -> list[ToolInfo]:
        return [
            ToolInfo(
                name=tool.name,
                description=tool.description,
                schema=tool.input_schema,
            )
            for tool in self.tools.values()
        ]
```

## State Management

Agents maintain **state** across their execution:

```python
class AgentState:
    """Tracks agent execution state."""

    def __init__(self):
        self.task_stack: list[Task] = []
        self.completed: list[TaskResult] = []
        self.failed: list[TaskResult] = []
        self.context: dict = {}

    def push_task(self, task: Task):
        self.task_stack.append(task)

    def pop_task(self) -> Task:
        return self.task_stack.pop()

    def record_result(self, result: TaskResult):
        if result.success:
            self.completed.append(result)
        else:
            self.failed.append(result)
```

## Communication Patterns

Agents communicate through well-defined patterns:

### Request-Response

```python
# Synchronous communication
result = await worker.execute(task)
```

### Event-Based

```python
# Asynchronous communication
await event_bus.publish(IncidentDetected(alert))
await event_bus.subscribe(RemediationApplied, self.handle_remediation)
```

### Shared State

```python
# Agents share context through state
shared_state["incident_context"] = alert_context
shared_state["deployment_plan"] = plan
```

## Putting It Together

A complete agentic system combines all these components:

```python
class AgenticSystem:
    """Complete agentic system for DevOps."""

    def __init__(self):
        # Orchestrator
        self.orchestrator = OrchestratorAgent()

        # Memory
        self.memory = MemorySystem()

        # Worker agents
        self.workers = {
            "triage": TriageWorker(),
            "build": BuildWorker(),
            "deploy": DeployWorker(),
            "monitor": MonitorWorker(),
        }

        # Tool registry
        self.tools = ToolRegistry()
        self.register_default_tools()

    async def handle_goal(self, goal: str):
        # Orchestrator creates plan
        plan = await self.orchestrator.plan(goal, self.memory)

        # Execute through workers
        for task in plan.tasks:
            worker = self.workers[task.worker_type]
            result = await worker.execute(task, self.tools)
            self.memory.add_observation(result)

        return plan.results
```

## Summary

The core building blocks of agentic systems are:

- **Orchestrator Agents**: Coordinate and delegate
- **Worker Agents**: Execute specialized tasks
- **Memory Systems**: Maintain context and learning
- **Tool Use**: Interface with external systems

Understanding these components enables you to design and build effective agents for your DevOps workflows.

In the next chapter, we'll explore **Agent Patterns** in depth, including ReAct, Triage, and Orchestration patterns.

---

<Note type="beginner">
Think of this like a restaurant kitchen. The orchestrator is the head chef who coordinates everything. The workers are the line cooks, each specializing in different stations. Memory is like the recipes and experience they carry. Tools are the knives, pans, and equipment they use.
</Note>

<CodeExample language="python">
# Quick example: Building a worker agent
class DeployWorker(WorkerAgent):
    def __init__(self):
        super().__init__(
            domain="deployment",
            tools=[
                KubectlTool(),
                HelmTool(),
                ArgoCDTool(),
            ]
        )

    async def deploy_service(self, service: Service) -> Result:
        # Use Helm to template
        helm_result = await self.tools["helm"].execute(
            command="template",
            chart=service.chart,
            values=service.values,
        )

        # Apply with kubectl
        apply_result = await self.tools["kubectl"].execute(
            command="apply",
            manifest=helm_result.output,
        )

        return apply_result
</CodeExample>

<BusinessValue>
Well-designed orchestrator/worker architectures reduce system complexity by 40-60%. Each component has clear boundaries, making testing, debugging, and scaling much easier.
</BusinessValue>

</ChapterContent>
