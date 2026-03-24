---
title: Scaling Patterns
slug: scaling-patterns
reading_time: 18
tags: [scaling, performance, cost-optimization]
---

# Scaling Patterns

<div className="chapter-summary">
<strong>Key Takeaways:</strong>
<ul>
<li>Horizontal scaling distributes workload across agent instances</li>
<li>Caching strategies reduce redundant LLM calls</li>
<li>Queue-based architectures handle burst traffic</li>
<li>Cost optimization balances performance with API expenses</li>
</ul>
</div>

## The Scaling Challenge

As your agent system grows, you'll face:

- **Higher request volumes** - More users, more queries
- **Longer running tasks** - Complex goals take time
- **Resource constraints** - API rate limits, memory, compute
- **Cost pressure** - LLM tokens aren't free

## Horizontal Scaling

### Stateless Agents

```python
class StatelessAgent:
    """Agent without internal state - horizontally scalable."""

    def __init__(self):
        # No instance state
        pass

    async def run(
        self,
        goal: str,
        context: dict | None = None
    ) -> Result:
        """Execute goal using only passed context."""
        # All state comes from arguments
        # Can be called from any instance
        ...
```

### Load Balancing

```python
class AgentPool:
    """Pool of agent workers behind load balancer."""

    def __init__(self, agent_class, pool_size: int = 10):
        self.agents = [agent_class() for _ in range(pool_size)]
        self.current = 0

    async def run(self, goal: str) -> Result:
        """Route to next available agent."""
        agent = self.agents[self.current]
        self.current = (self.current + 1) % len(self.agents)

        return await agent.run(goal)

# Better: Use message queue
class QueueBasedAgent:
    """Agent consumes from queue - naturally load balanced."""

    async def start(self):
        """Start consuming from queue."""
        async for task in self.queue.consume("agent-tasks"):
            result = await self.run(task.goal)
            await self.queue.publish("agent-results", result)
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-worker
spec:
  replicas: 10
  selector:
    matchLabels:
      app: agent-worker
  template:
    spec:
      containers:
      - name: agent
        image: agent:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: QUEUE_URL
          value: "redis://queue:6379"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-worker
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: External
    external:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: 10
```

## Caching Strategies

### Response Caching

```python
from functools import lru_cache
import hashlib

class CachedAgent:
    """Agent with response caching."""

    def __init__(self):
        self.cache = Redis(host="redis")

    def cache_key(self, goal: str, context: dict) -> str:
        """Generate deterministic cache key."""
        content = f"{goal}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def run(self, goal: str, context: dict = None) -> Result:
        """Execute with caching."""
        key = self.cache_key(goal, context)

        # Check cache
        cached = await self.cache.get(key)
        if cached:
            return Result.from_json(cached)

        # Execute
        result = await self._execute(goal, context)

        # Cache result
        await self.cache.setex(
            key,
            ttl=3600,  # 1 hour
            value=result.to_json()
        )

        return result
```

### Semantic Caching

```python
class SemanticCache:
    """Cache based on semantic similarity, not exact match."""

    def __init__(self, embedding_model, threshold: float = 0.95):
        self.model = embedding_model
        self.threshold = threshold
        self.cache: list[dict] = []

    async def get(self, query: str) -> Result | None:
        """Find semantically similar cached query."""
        query_embedding = self.model.encode(query)

        for entry in self.cache:
            similarity = cosine_similarity(
                query_embedding,
                entry["embedding"]
            )

            if similarity >= self.threshold:
                return entry["result"]

        return None

    async def set(self, query: str, result: Result):
        """Cache query and result."""
        embedding = self.model.encode(query)
        self.cache.append({
            "query": query,
            "embedding": embedding,
            "result": result,
        })
```

### Embedding Cache

```python
class EmbeddingCache:
    """Cache expensive embeddings."""

    def __init__(self):
        self.cache = Redis(host="redis")

    async def get_or_compute(
        self,
        text: str,
        compute_fn: Callable
    ) -> list[float]:
        """Get from cache or compute."""
        key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"

        cached = await self.cache.get(key)
        if cached:
            return json.loads(cached)

        # Compute
        embedding = await compute_fn(text)

        # Cache (embeddings are stable, long TTL)
        await self.cache.setex(
            key,
            ttl=86400 * 7,  # 1 week
            value=json.dumps(embedding)
        )

        return embedding
```

## Queue-Based Architecture

### Producer-Consumer Pattern

```python
class TaskProducer:
    """Submit tasks to queue."""

    async def submit(self, goal: str, context: dict = None) -> str:
        """Submit task and return task ID."""
        task_id = str(uuid.uuid4())

        await self.queue.publish("agent-tasks", {
            "task_id": task_id,
            "goal": goal,
            "context": context,
            "submitted_at": datetime.now().isoformat(),
        })

        return task_id

class TaskConsumer:
    """Process tasks from queue."""

    async def start(self):
        """Start consuming tasks."""
        async for task in self.queue.subscribe("agent-tasks"):
            try:
                result = await self.agent.run(
                    task["goal"],
                    task["context"]
                )

                await self.publish_result(task["task_id"], result)

            except Exception as e:
                await self.handle_failure(task["task_id"], e)
```

### Priority Queues

```python
class PriorityTaskQueue:
    """Queue with priority levels."""

    async def submit(
        self,
        goal: str,
        priority: int = 0,  # Higher = more important
        context: dict = None
    ):
        """Submit with priority."""
        await self.queue.zadd(
            "priority-tasks",
            {
                json.dumps({
                    "goal": goal,
                    "context": context,
                    "submitted_at": time.time(),
                }): -priority  # Negative for min-heap behavior
            }
        )

    async def consume(self) -> dict:
        """Get highest priority task."""
        result = await self.queue.zpopmin("priority-tasks")
        if result:
            return json.loads(result[0][0])
        return None
```

## Cost Optimization

### Token Budget Management

```python
class TokenBudget:
    """Track and limit token usage."""

    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def can_afford(self, estimated_tokens: int) -> bool:
        """Check if we have budget for the operation."""
        return self.used_tokens + estimated_tokens <= self.max_tokens

    def record_usage(self, actual_tokens: int):
        """Record actual token usage."""
        self.used_tokens += actual_tokens

    def remaining(self) -> int:
        """Get remaining budget."""
        return self.max_tokens - self.used_tokens

class BudgetAwareAgent:
    """Agent that respects token budgets."""

    async def run(self, goal: str, budget: TokenBudget) -> Result:
        """Execute within budget."""
        # Estimate tokens needed
        estimated = self.estimate_tokens(goal)

        if not budget.can_afford(estimated):
            return Result.error("Insufficient token budget")

        # Execute
        result = await self._execute(goal)

        # Record actual usage
        budget.record_usage(result.tokens_used)

        return result
```

### Model Selection

```python
class ModelSelector:
    """Choose appropriate model based on task complexity."""

    def select_model(self, task: Task) -> str:
        """Select model based on task requirements."""
        complexity = self.assess_complexity(task)

        if complexity == "simple":
            return "gpt-3.5-turbo"  # Fast, cheap
        elif complexity == "moderate":
            return "gpt-4-turbo"    # Balanced
        else:
            return "gpt-4"          # High quality

    def assess_complexity(self, task: Task) -> str:
        """Assess task complexity."""
        factors = {
            "requires_reasoning": self.needs_reasoning(task),
            "requires_creativity": self.needs_creativity(task),
            "requires_precision": self.needs_precision(task),
            "input_length": len(task.goal),
        }

        score = sum(factors.values())
        if score < 3:
            return "simple"
        elif score < 7:
            return "moderate"
        else:
            return "complex"
```

### Cost Tracking

```python
class CostTracker:
    """Track API costs."""

    def __init__(self):
        self.costs = {
            "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
            "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
        }

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for API call."""
        rates = self.costs[model]
        return (
            input_tokens * rates["input"] +
            output_tokens * rates["output"]
        )

    async def record(self, model: str, usage: dict):
        """Record usage for billing."""
        cost = self.calculate_cost(
            model,
            usage["prompt_tokens"],
            usage["completion_tokens"]
        )

        await self.db.insert("usage", {
            "model": model,
            "input_tokens": usage["prompt_tokens"],
            "output_tokens": usage["completion_tokens"],
            "cost": cost,
            "timestamp": datetime.now(),
        })
```

## Summary

- **Horizontal scaling**: Stateless agents + load balancing
- **Caching**: Response, semantic, and embedding caches
- **Queues**: Handle burst traffic gracefully
- **Cost optimization**: Budget management, model selection, tracking

---

<CodeExample language="python">
# Quick scaling recipe
class ProductionAgent:
    def __init__(self):
        self.cache = SemanticCache()
        self.budget = TokenBudget(max_tokens=100000)
        self.queue = TaskQueue()

    async def run(self, goal: str) -> Result:
        # Check cache first
        cached = await self.cache.get(goal)
        if cached:
            return cached

        # Check budget
        if not self.budget.can_afford(1000):
            raise BudgetExceeded()

        # Execute
        result = await self._execute(goal)
        self.budget.record_usage(result.tokens_used)

        # Cache result
        await self.cache.set(goal, result)

        return result
</CodeExample>

<BusinessValue>
Proper scaling reduces infrastructure costs by 40-60% while maintaining performance. Caching alone can reduce API costs by 70-80%.
</BusinessValue>