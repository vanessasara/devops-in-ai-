---
title: Observability for Agentic Systems
slug: observability
reading_time: 20
tags: [observability, tracing, logging, debugging]
---

import ChapterContent from '@site/src/components/ChapterContent';

<ChapterContent slug="observability">

# Observability for Agentic Systems



## Why Observability Matters

Agents make autonomous decisions. When something goes wrong, you need visibility into **what** happened, **why** it happened, and **how** to fix it.

## The Three Pillars

```
┌─────────────────────────────────────────────────────────────┐
│                    Observability                             │
├─────────────────────────────────────────────────────────────┤
│  Metrics      │  Logs            │  Traces                 │
│  "How much?"   │  "What happened?"│  "Where did it go?"     │
│  Numbers       │  Events          │  Spans                  │
│  Dashboards    │  Search          │  Visualizations         │
└─────────────────────────────────────────────────────────────┘
```

## Tracing

### Trace Structure

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Span:
    """A single operation within a trace."""
    trace_id: str
    span_id: str
    parent_id: Optional[str]
    name: str
    start_time: datetime
    end_time: Optional[datetime]
    attributes: dict
    events: list["Event"]

    @property
    def duration_ms(self) -> int:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0
```

### Instrumentation

```python
import opentelemetry
from opentelemetry.trace import get_tracer

tracer = get_tracer("agent")

class TracedAgent:
    """Agent with distributed tracing."""

    async def run(self, goal: str) -> Result:
        """Execute goal with tracing."""
        with tracer.start_as_current_span("agent.run") as span:
            # Add attributes
            span.set_attribute("goal", goal)
            span.set_attribute("agent.type", self.__class__.__name__)

            try:
                result = await self._execute(goal)

                span.set_attribute("result.success", result.success)
                span.set_attribute("result.tokens_used", result.tokens_used)

                return result

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
```

### Tool Call Tracing

```python
async def call_tool(self, tool: str, params: dict) -> Result:
    """Call tool with tracing."""
    with tracer.start_as_current_span(f"tool.{tool}") as span:
        # Add input attributes
        for key, value in params.items():
            span.set_attribute(f"input.{key}", str(value)[:256])

        # Execute
        result = await self.tools[tool].execute(params)

        # Add output attributes
        span.set_attribute("output.success", result.success)
        if not result.success:
            span.set_attribute("output.error", result.error)

        return result
```

### Trace Visualization

```
Trace: incident-response-12345
│
├─ agent.run (1523ms)
│  │
│  ├─ agent.reason (45ms)
│  │  └─ llm.generate (42ms)
│  │
│  ├─ tool.kubectl.get_pods (234ms)
│  │  └─ k8s.api.call (230ms)
│  │
│  ├─ agent.reason (38ms)
│  │  └─ llm.generate (35ms)
│  │
│  ├─ tool.kubectl.logs (567ms)
│  │  └─ k8s.api.call (560ms)
│  │
│  ├─ agent.reason (52ms)
│  │  └─ llm.generate (50ms)
│  │
│  └─ agent.respond (12ms)
│
└── Result: "Database connection pool exhausted"
```

## Logging

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

class LoggedAgent:
    """Agent with structured logging."""

    async def run(self, goal: str) -> Result:
        """Execute with logging."""
        log = logger.bind(
            agent=self.__class__.__name__,
            goal=goal[:100],  # Truncate
        )

        log.info("agent_started")

        try:
            result = await self._execute(goal)

            log.info(
                "agent_completed",
                success=result.success,
                tokens=result.tokens_used,
                duration_ms=result.duration_ms,
            )

            return result

        except Exception as e:
            log.error(
                "agent_failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
```

### Log Levels

```python
# DEBUG: Detailed execution trace
logger.debug("tool_call", tool="kubectl", params={"namespace": "default"})

# INFO: Normal operations
logger.info("goal_completed", goal=goal, result=result.success)

# WARNING: Unexpected but handled
logger.warning("retry_attempt", attempt=2, max_attempts=3)

# ERROR: Failures requiring attention
logger.error("tool_failed", tool="kubectl", error="connection refused")
```

### Log Aggregation

```python
# Configure logging to send to aggregator
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# Send to Elasticsearch, Splunk, etc.
handler = logging.handlers.HTTPHandler(
    host="logs.example.com",
    url="/api/logs",
    method="POST",
)
```

## Metrics

### Key Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
AGENT_RUNS = Counter(
    "agent_runs_total",
    "Total agent runs",
    ["agent_type", "status"]
)

TOOL_CALLS = Counter(
    "tool_calls_total",
    "Total tool calls",
    ["tool_name", "status"]
)

TOKENS_USED = Counter(
    "tokens_used_total",
    "Total tokens consumed",
    ["model"]
)

# Histograms
AGENT_LATENCY = Histogram(
    "agent_latency_seconds",
    "Agent execution latency",
    ["agent_type"]
)

TOOL_LATENCY = Histogram(
    "tool_latency_seconds",
    "Tool call latency",
    ["tool_name"]
)

# Gauges
ACTIVE_AGENTS = Gauge(
    "active_agents",
    "Currently running agents"
)
```

### Metric Collection

```python
class MetricsAgent:
    """Agent with metrics collection."""

    async def run(self, goal: str) -> Result:
        """Execute with metrics."""
        AGENT_RUNS.labels(
            agent_type=self.__class__.__name__,
            status="started"
        ).inc()

        ACTIVE_AGENTS.inc()

        start_time = time.time()

        try:
            result = await self._execute(goal)

            AGENT_RUNS.labels(
                agent_type=self.__class__.__name__,
                status="success"
            ).inc()

            TOKENS_USED.labels(model=self.model).inc(result.tokens_used)

            return result

        except Exception as e:
            AGENT_RUNS.labels(
                agent_type=self.__class__.__name__,
                status="error"
            ).inc()
            raise

        finally:
            duration = time.time() - start_time
            AGENT_LATENCY.labels(
                agent_type=self.__class__.__name__
            ).observe(duration)
            ACTIVE_AGENTS.dec()
```

### Dashboards

```yaml
# Grafana dashboard configuration
dashboard:
  title: "Agent Observability"
  panels:
    - title: "Agent Success Rate"
      type: "graph"
      query: 'rate(agent_runs_total{status="success"}[5m]) / rate(agent_runs_total[5m])'

    - title: "Agent Latency P95"
      type: "graph"
      query: 'histogram_quantile(0.95, agent_latency_seconds_bucket)'

    - title: "Token Usage"
      type: "graph"
      query: 'rate(tokens_used_total[5m])'

    - title: "Active Agents"
      type: "gauge"
      query: 'active_agents'
```

## Debugging

### Reasoning Trace

```python
class DebugAgent:
    """Agent with reasoning trace."""

    async def run(self, goal: str) -> Result:
        """Execute with debug trace."""
        self.trace = []

        async for iteration in range(self.max_iterations):
            # Capture state
            state = {
                "iteration": iteration,
                "context": self.context,
                "memory": self.memory,
            }
            self.trace.append(state)

            # Reason
            thought = await self.reason(goal)
            self.trace.append({"thought": thought})

            # Decide action
            action = await self.decide_action(thought)
            self.trace.append({"action": action})

            # Execute
            result = await self.execute_action(action)
            self.trace.append({"observation": result})

        return self.compile_result()

    def export_trace(self) -> str:
        """Export trace for debugging."""
        return json.dumps(self.trace, indent=2)
```

### Debug Endpoint

```python
@app.get("/api/agent/{run_id}/debug")
async def get_debug_trace(run_id: str):
    """Get debug trace for a run."""
    run = await run_store.get(run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "run_id": run_id,
        "goal": run.goal,
        "trace": run.trace,
        "final_result": run.result,
        "metrics": {
            "duration_ms": run.duration_ms,
            "tokens_used": run.tokens_used,
            "tool_calls": len([t for t in run.trace if "action" in t]),
        }
    }
```

### Debugging UI

```javascript
// React component for trace visualization
function TraceViewer({ runId }) {
  const [trace, setTrace] = useState([]);

  useEffect(() => {
    fetch(`/api/agent/${runId}/debug`)
      .then(res => res.json())
      .then(data => setTrace(data.trace));
  }, [runId]);

  return (
    <div className="trace-viewer">
      {trace.map((step, i) => (
        <div key={i} className={`trace-step ${step.type}`}>
          <div className="step-header">
            <span className="step-number">{i}</span>
            <span className="step-type">{Object.keys(step)[0]}</span>
          </div>
          <pre className="step-content">
            {JSON.stringify(step, null, 2)}
          </pre>
        </div>
      ))}
    </div>
  );
}
```

## Summary

- **Tracing**: Follow requests through the system
- **Logging**: Record events for analysis
- **Metrics**: Measure performance and usage
- **Debugging**: Diagnose reasoning failures

Combine all three for complete observability.

---

<Note type="beginner">
Think of observability like a car's dashboard. Tracing is the GPS showing where you went, logging is the dashcam recording what happened, and metrics are the speedometer tracking performance.
</Note>

<CodeExample language="python">
# Quick observability setup
def setup_observability(agent: Agent) -> Agent:
    return (
        TracedAgent(agent)       # Add tracing
        .pipe(LoggedAgent)        # Add logging
        .pipe(MetricsAgent)      # Add metrics
        .pipe(DebugAgent)        # Add debug trace
    )
</CodeExample>

<BusinessValue>
Good observability reduces mean time to resolution (MTTR) by 60-80%. When you can see what happened, you can fix it faster.
</BusinessValue>

</ChapterContent>
