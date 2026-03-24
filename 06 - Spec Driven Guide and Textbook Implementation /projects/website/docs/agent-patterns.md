---
title: Agent Patterns for DevOps
slug: agent-patterns
reading_time: 20
tags: [patterns, react, triage, orchestration]
---

# Agent Patterns for DevOps

<div className="chapter-summary">
<strong>Key Takeaways:</strong>
<ul>
<li>ReAct pattern combines reasoning with action selection</li>
<li>Triage agents route requests to appropriate specialists</li>
<li>Orchestrator patterns manage complex multi-step workflows</li>
<li>Feedback loops enable continuous improvement</li>
</ul>
</div>

## The Pattern Language

Just as software engineering has design patterns, agentic systems have **interaction patterns** that capture proven solutions to common problems.

## ReAct: Reason + Act

The **ReAct pattern** is the most fundamental agent pattern. It interleaves reasoning and action in a tight loop.

### How ReAct Works

```
┌──────────────────────────────────────────────────────┐
│                    ReAct Loop                        │
│                                                      │
│  ┌─────────────┐     ┌─────────────┐                │
│  │   Thought   │────▶│   Action    │                │
│  │  (Reason)   │     │  (Execute)  │                │
│  └─────────────┘     └──────┬──────┘                │
│         ▲                    │                       │
│         │                    ▼                       │
│         │            ┌─────────────┐                │
│         │            │ Observation │                │
│         └────────────│   (Result)  │                │
│                      └─────────────┘                │
└──────────────────────────────────────────────────────┘
```

### ReAct Implementation

```python
class ReActAgent:
    """ReAct pattern implementation."""

    def __init__(self, tools: list[Tool], llm):
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.memory = []

    async def run(self, goal: str, max_iterations: int = 10):
        """
        Execute ReAct loop until goal achieved or max iterations.

        Each iteration:
        1. Think about current state
        2. Decide action
        3. Execute action
        4. Observe result
        5. Update understanding
        """
        for i in range(max_iterations):
            # Reason about next step
            thought = await self.reason(goal)
            self.memory.append(("thought", thought))

            # Check if done
            if "I have the answer" in thought:
                return self.extract_answer(thought)

            # Decide action
            action = await self.decide_action(thought)
            self.memory.append(("action", action))

            # Execute
            observation = await self.execute_action(action)
            self.memory.append(("observation", observation))

        return {"status": "max_iterations_reached", "memory": self.memory}

    async def reason(self, goal: str) -> str:
        """Generate thought about current state."""
        prompt = f"""
Goal: {goal}

Memory:
{self.format_memory()}

What should I think about next? Express your reasoning.
"""
        return await self.llm.generate(prompt)

    async def decide_action(self, thought: str) -> dict:
        """Decide which action to take."""
        prompt = f"""
Based on thought: {thought}

Available tools: {list(self.tools.keys())}

Which tool should I use and with what parameters?
Output format: {{ "tool": "...", "params": {{...}} }}
"""
        return await self.llm.generate_json(prompt)

    async def execute_action(self, action: dict) -> str:
        """Execute the selected action."""
        tool = self.tools.get(action["tool"])
        if not tool:
            return f"Error: Unknown tool {action['tool']}"

        result = await tool.execute(action["params"])
        return result.output if result.success else f"Error: {result.error}"
```

### ReAct Example: Incident Triage

```python
# ReAct agent triaging an incident
goal = "Determine root cause of high error rate in payment service"

# Iteration 1
thought = """
The payment service has high error rates. I should first check
the current state of the service to understand the scope.
"""
action = {"tool": "kubectl", "params": {"command": "logs", "service": "payment"}}
observation = "Error: connection refused to database port 5432"

# Iteration 2
thought = """
The database connection is failing. Let me check if the database
pod is running.
"""
action = {"tool": "kubectl", "params": {"command": "get", "resource": "pods", "selector": "app=postgres"}}
observation = "postgres-0 0/1 CrashLoopBackOff 3 5m"

# Iteration 3
thought = """
Database pod is crashing. Let me check the logs to see why.
"""
action = {"tool": "kubectl", "params": {"command": "logs", "pod": "postgres-0"}}
observation = "OOMKilled: Container exceeded memory limit"

# Iteration 4
thought = """
The database is running out of memory. I have the answer:
the root cause is insufficient memory allocation for the postgres container.
"""
```

### When to Use ReAct

Use ReAct when:
- The path to solution is **unknown**
- You need to **explore** before acting
- The environment is **dynamic**
- **Feedback** is available after each action

## Triage Pattern

**Triage agents** classify and route incoming requests to appropriate handlers.

### Triage Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Triage Agent                         │
│                                                         │
│  Input: Alert/Request/Incident                          │
│  Output: Route + Priority + Context                      │
│                                                         │
└────────────────────┬─────────────────────────────────────┘
                     │
         ┌───────────┼───────────┬───────────────┐
         ▼           ▼           ▼               ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
   │Infra     │ │App       │ │Security  │ │Human     │
   │Team      │ │Team      │ │Team      │ │Escalation│
   └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Triage Implementation

```python
from enum import Enum
from pydantic import BaseModel

class Category(Enum):
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    SECURITY = "security"
    NETWORK = "network"
    UNKNOWN = "unknown"

class Priority(Enum):
    P1_CRITICAL = 1
    P2_HIGH = 2
    P3_MEDIUM = 3
    P4_LOW = 4

class TriageResult(BaseModel):
    category: Category
    priority: Priority
    confidence: float
    context: dict
    suggested_handler: str

class TriageAgent:
    """Routes incidents to appropriate handlers."""

    def __init__(self, llm):
        self.llm = llm
        self.handlers = self.load_handlers()

    async def triage(self, incident: Incident) -> TriageResult:
        """
        Analyze incident and determine routing.

        Returns category, priority, and suggested handler.
        """
        # Extract features
        features = await self.extract_features(incident)

        # Classify
        classification = await self.classify(features)

        # Prioritize
        priority = await self.prioritize(incident, classification)

        # Find handler
        handler = self.find_handler(classification.category)

        return TriageResult(
            category=classification.category,
            priority=priority,
            confidence=classification.confidence,
            context={"features": features, "incident_id": incident.id},
            suggested_handler=handler,
        )

    async def extract_features(self, incident: Incident) -> dict:
        """Extract relevant features from incident."""
        return {
            "error_patterns": self.find_patterns(incident.logs),
            "affected_services": incident.affected_services,
            "error_rate": incident.metrics.error_rate,
            "recent_changes": incident.recent_changes,
            "time_of_day": incident.timestamp.hour,
        }

    async def classify(self, features: dict) -> Classification:
        """Use LLM to classify the incident."""
        prompt = f"""
Classify this incident into one of: infrastructure, application, security, network

Features:
- Error patterns: {features['error_patterns']}
- Affected services: {features['affected_services']}
- Error rate: {features['error_rate']}
- Recent changes: {features['recent_changes']}

Output: {{ "category": "...", "confidence": 0.0-1.0 }}
"""
        return await self.llm.generate_structured(prompt, Classification)

    def find_handler(self, category: Category) -> str:
        """Find appropriate handler for category."""
        return self.handlers.get(category, "oncall")
```

### Triage with Learning

```python
class LearningTriageAgent(TriageAgent):
    """Triage agent that learns from feedback."""

    def __init__(self, llm):
        super().__init__(llm)
        self.training_data = []

    async def record_feedback(
        self,
        incident_id: str,
        triage_result: TriageResult,
        actual_category: Category,
        was_correct: bool,
    ):
        """Record human feedback for improvement."""
        self.training_data.append({
            "incident_id": incident_id,
            "predicted": triage_result.category,
            "actual": actual_category,
            "correct": was_correct,
        })

        # Periodically retrain
        if len(self.training_data) % 100 == 0:
            await self.retrain()

    async def retrain(self):
        """Retrain classifier with accumulated feedback."""
        # Use training_data to improve classification
        accuracy = sum(1 for d in self.training_data if d["correct"])
        accuracy /= len(self.training_data)
        print(f"Retraining with {len(self.training_data)} samples, accuracy: {accuracy:.2%}")
```

## Orchestrator Pattern

**Orchestrator agents** coordinate multiple workers to accomplish complex goals.

### Orchestrator Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                       │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ Planner  │ │ Monitor  │ │ Recover  │ │ Aggregator     │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘ │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐     ┌─────────┐     ┌─────────┐
   │Worker A │     │Worker B │     │Worker C │
   │(Triage) │     │ (Build) │     │(Deploy) │
   └─────────┘     └─────────┘     └─────────┘
```

### Orchestrator Implementation

```python
from dataclasses import dataclass
from typing import Callable, Awaitable

@dataclass
class Task:
    id: str
    worker: str
    action: str
    params: dict
    dependencies: list[str] = None

@dataclass
class Plan:
    tasks: list[Task]
    parallel_groups: list[list[str]]  # Tasks that can run in parallel

class OrchestratorAgent:
    """Coordinates multiple workers to accomplish goals."""

    def __init__(self):
        self.planner = Planner()
        self.workers: dict[str, Worker] = {}
        self.monitor = Monitor()

    async def execute_goal(self, goal: str) -> Result:
        """
        Execute a high-level goal.

        1. Create plan
        2. Execute tasks (respecting dependencies)
        3. Handle failures
        4. Aggregate results
        """
        # Create execution plan
        plan = await self.planner.create_plan(goal, self.workers)

        # Track execution state
        completed: dict[str, Result] = {}
        failed: dict[str, Result] = {}

        # Execute in dependency order
        for task_group in plan.parallel_groups:
            # Run tasks in this group in parallel
            results = await asyncio.gather(*[
                self.execute_task(task, completed)
                for task in task_group
            ], return_exceptions=True)

            for task, result in zip(task_group, results):
                if isinstance(result, Exception):
                    failed[task.id] = Result.error(str(result))
                elif result.success:
                    completed[task.id] = result
                else:
                    failed[task.id] = result

                    # Try recovery
                    recovered = await self.recover(task, result.error)
                    if recovered:
                        completed[task.id] = recovered
                    else:
                        # Escalate to human
                        await self.escalate(task, result.error)

        return self.aggregate_results(completed, failed)

    async def execute_task(
        self,
        task: Task,
        completed: dict[str, Result]
    ) -> Result:
        """Execute a single task with its worker."""
        worker = self.workers[task.worker]
        context = self.build_context(task, completed)

        return await worker.execute(task.action, task.params, context)

    async def recover(self, task: Task, error: str) -> Result | None:
        """Attempt to recover from failure."""
        recovery_plan = await self.planner.create_recovery(task, error)

        if recovery_plan:
            for recovery_task in recovery_plan.tasks:
                result = await self.execute_task(recovery_task, {})
                if result.success:
                    # Retry original task
                    return await self.execute_task(task, {})

        return None

    async def escalate(self, task: Task, error: str):
        """Escalate to human operators."""
        await self.monitor.alert(
            level="critical",
            message=f"Task {task.id} failed: {error}",
            context={"task": task, "error": error},
        )
```

### Plan Creation

```python
class Planner:
    """Creates execution plans from goals."""

    async def create_plan(
        self,
        goal: str,
        available_workers: dict[str, Worker]
    ) -> Plan:
        """
        Decompose goal into tasks.

        Uses LLM to:
        1. Understand the goal
        2. Identify required steps
        3. Assign workers to steps
        4. Determine dependencies
        """
        # LLM-based planning
        plan_prompt = f"""
Goal: {goal}

Available workers: {list(available_workers.keys())}

Create an execution plan:
1. List tasks needed
2. Assign each task to a worker
3. Identify dependencies between tasks

Output format:
{{
  "tasks": [
    {{"id": "...", "worker": "...", "action": "...", "params": {{}}}},
    ...
  ],
  "dependencies": {{"task_id": ["depends_on_ids"]}}
}}
"""
        plan_data = await self.llm.generate_json(plan_prompt)

        # Convert to Plan object
        return self.build_plan(plan_data)
```

## Feedback Loops

Effective agents incorporate **feedback loops** for continuous improvement.

### Types of Feedback

```python
class FeedbackType(Enum):
    EXPLICIT = "explicit"      # Human provides feedback
    IMPLICIT = "implicit"      # Observed from outcomes
    SELF = "self"             # Agent evaluates its own performance
```

### Feedback Implementation

```python
class FeedbackSystem:
    """Collects and applies feedback."""

    def __init__(self):
        self.feedback_store = []
        self.performance_metrics = defaultdict(list)

    async def record(
        self,
        action: str,
        result: Result,
        feedback: Feedback | None = None
    ):
        """Record action outcome and feedback."""
        self.feedback_store.append({
            "action": action,
            "result": result,
            "feedback": feedback,
            "timestamp": datetime.now(),
        })

        # Update performance metrics
        self.performance_metrics[action].append({
            "success": result.success,
            "latency": result.latency,
        })

    async def get_improvement_suggestions(self) -> list[str]:
        """Analyze feedback for improvements."""
        suggestions = []

        for action, metrics in self.performance_metrics.items():
            success_rate = sum(1 for m in metrics if m["success"]) / len(metrics)
            if success_rate < 0.8:
                suggestions.append(
                    f"Action '{action}' has low success rate ({success_rate:.0%})"
                )

        return suggestions
```

## Pattern Selection Guide

| Pattern | Use When | Characteristics |
|---------|----------|-----------------|
| **ReAct** | Unknown solution path | Exploratory, flexible |
| **Triage** | High-volume classification | Fast routing, clear categories |
| **Orchestrator** | Complex multi-step workflows | Structured, reliable |
| **Feedback** | Continuous improvement needed | Learning, adaptive |

## Summary

- **ReAct** interweaves reasoning and action for exploratory problem-solving
- **Triage** classifies and routes requests efficiently
- **Orchestrator** coordinates multiple workers for complex goals
- **Feedback loops** enable continuous improvement

In the next chapter, we'll explore **Tool Use and Integration** in depth.

---

<Note type="beginner">
Think of ReAct like debugging: you think about the problem, try something, see what happens, and adjust. Triage is like a receptionist directing calls. Orchestrator is like a project manager coordinating team members.
</Note>

<CodeExample language="python">
# Quick pattern selector
def select_pattern(task_type: str) -> str:
    patterns = {
        "incident_response": "react",  # Need to explore
        "alert_routing": "triage",      # Need to route fast
        "deployment": "orchestrator",   # Need coordination
    }
    return patterns.get(task_type, "react")
</CodeExample>

<BusinessValue>
Using the right pattern for the task reduces incident resolution time by 30-50%. ReAct for novel issues, Triage for known categories, Orchestrator for complex workflows.
</BusinessValue>