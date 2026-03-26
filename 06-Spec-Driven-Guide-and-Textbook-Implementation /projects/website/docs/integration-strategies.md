---
title: Integration Strategies
slug: integration-strategies
reading_time: 22
tags: [integration, apis, events]
---

import ChapterContent from '@site/src/components/ChapterContent';

<ChapterContent slug="integration-strategies">

# Integration Strategies



## Integration Patterns

Agents need to interact with existing systems. Choosing the right integration pattern is crucial for reliability and maintainability.

## API-First Integration

### REST APIs

```python
class APIClient:
    """Base client for REST API integration."""

    def __init__(self, base_url: str, auth: Auth):
        self.base_url = base_url
        self.auth = auth
        self.session = aiohttp.ClientSession()

    async def get(self, path: str, params: dict = None) -> dict:
        """GET request with auth."""
        headers = await self.auth.get_headers()
        async with self.session.get(
            f"{self.base_url}{path}",
            params=params,
            headers=headers,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def post(self, path: str, data: dict) -> dict:
        """POST request with auth."""
        headers = await self.auth.get_headers()
        async with self.session.post(
            f"{self.base_url}{path}",
            json=data,
            headers=headers,
        ) as response:
            response.raise_for_status()
            return await response.json()
```

### GraphQL Integration

```python
class GraphQLClient:
    """Client for GraphQL APIs."""

    async def query(self, query: str, variables: dict = None) -> dict:
        """Execute GraphQL query."""
        payload = {
            "query": query,
            "variables": variables or {},
        }

        async with self.session.post(
            self.endpoint,
            json=payload,
            headers=self.headers,
        ) as response:
            result = await response.json()

        if "errors" in result:
            raise GraphQLError(result["errors"])

        return result["data"]

# Usage
result = await client.query("""
    query GetDeploymentStatus($name: String!) {
        deployment(name: $name) {
            status
            pods {
                name
                ready
            }
        }
    }
""", {"name": "my-service"})
```

## Event-Driven Integration

### Event Bus Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Event Bus                                │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────────────┐ │
│  │ Events  │  │ Events  │  │ Events  │  │    Events      │ │
│  │ Topic A │  │ Topic B │  │ Topic C │  │    Topic D     │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └───────┬────────┘ │
│       │            │            │                │         │
└───────┼────────────┼────────────┼────────────────┼─────────┘
        │            │            │                │
        ▼            ▼            ▼                ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐    ┌─────────────┐
   │Agent A  │ │Agent B  │ │Agent C  │    │  Agent D    │
   │(Triage) │ │(Build)  │ │(Deploy) │    │  (Monitor)  │
   └─────────┘ └─────────┘ └─────────┘    └─────────────┘
```

### Event Publisher

```python
class EventPublisher:
    """Publishes events to message bus."""

    def __init__(self, bus: MessageBus):
        self.bus = bus

    async def publish(self, event: Event):
        """Publish event to bus."""
        await self.bus.publish(
            topic=event.topic,
            key=event.key,
            value=event.to_dict(),
            headers={
                "event_type": event.type,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
            }
        )

# Usage
await publisher.publish(IncidentCreated(
    incident_id="inc-123",
    severity="high",
    service="payment-api",
))
```

### Event Consumer

```python
class AgentConsumer:
    """Consumes events and triggers agent actions."""

    def __init__(self, agent: Agent):
        self.agent = agent

    @handler(IncidentCreated)
    async def handle_incident(self, event: IncidentCreated):
        """Handle new incident event."""
        result = await self.agent.run(f"Triage incident {event.incident_id}")

        if result.needs_escalation:
            await self.publish(IncidentEscalated(
                incident_id=event.incident_id,
                reason=result.reason,
            ))

    @handler(DeploymentCompleted)
    async def handle_deployment(self, event: DeploymentCompleted):
        """Handle deployment completion."""
        await self.agent.run(f"Verify deployment {event.deployment_id}")
```

## Hybrid Integration

### Request-Reply with Events

```python
async def deploy_service(service: str, version: str) -> dict:
    """Deploy using hybrid pattern."""

    # 1. Synchronous request to initiate
    result = await api_client.post("/deploy", {
        "service": service,
        "version": version,
    })

    deployment_id = result["deployment_id"]

    # 2. Asynchronous monitoring via events
    async for event in event_stream.subscribe(f"deployment.{deployment_id}"):
        if event.status == "completed":
            return {"status": "success", "deployment_id": deployment_id}
        elif event.status == "failed":
            return {"status": "failed", "error": event.error}

        # Emit progress
        yield {"status": event.status, "progress": event.progress}
```

## Security Considerations

### Authentication

```python
class AuthService:
    """Central authentication service."""

    def __init__(self, provider: AuthProvider):
        self.provider = provider

    async def authenticate(self, credentials: Credentials) -> Token:
        """Authenticate and return token."""
        user = await self.provider.validate(credentials)

        if not user:
            raise AuthenticationError("Invalid credentials")

        token = self.create_token(user)
        return token

    async def validate_token(self, token: str) -> User:
        """Validate token and return user."""
        payload = self.decode_token(token)

        if payload.expired:
            raise AuthenticationError("Token expired")

        return User.from_payload(payload)
```

### Authorization

```python
class Authorization:
    """Role-based access control."""

    def __init__(self):
        self.permissions = self.load_permissions()

    def check(self, user: User, action: str, resource: str) -> bool:
        """Check if user can perform action on resource."""
        role = user.role

        if role not in self.permissions:
            return False

        allowed_actions = self.permissions[role].get(resource, [])
        return action in allowed_actions

    def require(self, action: str, resource: str):
        """Decorator to require permission."""
        def decorator(func):
            @wraps(func)
            async def wrapper(user: User, *args, **kwargs):
                if not self.check(user, action, resource):
                    raise AuthorizationError(
                        f"User lacks permission: {action} on {resource}"
                    )
                return await func(user, *args, **kwargs)
            return wrapper
        return decorator

# Usage
@auth.require("deploy", "services")
async def deploy_service(user: User, service: str):
    ...
```

### Audit Trail

```python
class AuditLogger:
    """Logs all agent actions for compliance."""

    async def log(
        self,
        user: User,
        action: str,
        resource: str,
        result: str,
        metadata: dict = None
    ):
        """Log action to audit system."""
        await self.db.insert("audit_log", {
            "user_id": user.id,
            "action": action,
            "resource": resource,
            "result": result,
            "metadata": metadata,
            "timestamp": datetime.now(),
            "ip_address": user.ip_address,
        })

# Usage
await audit.log(
    user=current_user,
    action="deploy",
    resource=f"service/{service_name}",
    result="success",
    metadata={"version": version, "environment": "production"},
)
```

## Integration Testing

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_api_integration():
    """Test agent can call API."""
    api_client = MockAPIClient()
    agent = Agent(tools=[APITool(api_client)])

    # Setup mock response
    api_client.get = AsyncMock(return_value={"status": "ok"})

    # Run agent
    result = await agent.run("Check service status")

    assert result.success
    assert api_client.get.called

@pytest.mark.asyncio
async def test_event_integration():
    """Test agent publishes and consumes events."""
    event_bus = MockEventBus()
    agent = Agent(event_bus=event_bus)

    # Subscribe to topic
    events = []
    event_bus.subscribe(lambda e: events.append(e))

    # Run agent
    await agent.run("Deploy service X")

    # Verify event was published
    assert len(events) > 0
    assert events[0].type == "DeploymentStarted"
```

## Summary

- **API-first**: RESTful endpoints for synchronous operations
- **Event-driven**: Kafka/RabbitMQ for async workflows
- **Hybrid**: Combine both for complex processes
- **Security**: Auth, authorization, and audit trails
- **Testing**: Verify integrations work correctly

In the next chapter, we'll cover **Observability for Agentic Systems**.

---

<Note type="beginner">
APIs are like ordering at a restaurant - you make a request and wait for a response. Events are like a buffet notification - you subscribe and get notified when something interesting happens.
</Note>

<CodeExample language="python">
# Quick integration pattern selector
def select_pattern(use_case: str) -> str:
    patterns = {
        "query_data": "api",       # Need response now
        "long_process": "event",    # Can wait for result
        "notification": "event",    # Just need to know it happened
        "user_action": "api",       # User is waiting
    }
    return patterns.get(use_case, "api")
</CodeExample>

<BusinessValue>
Event-driven architectures reduce coupling between services by 70-90%, making systems more resilient to change and easier to scale.
</BusinessValue>

</ChapterContent>
