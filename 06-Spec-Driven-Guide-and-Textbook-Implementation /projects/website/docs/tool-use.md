---
title: Tool Use and Integration
slug: tool-use
reading_time: 18
tags: [tools, integration, apis]
---

import ChapterContent from '@site/src/components/ChapterContent';

<ChapterContent slug="tool-use">

# Tool Use and Integration



## Why Tools Matter

Agents without tools are like consultants who can only give advice. **Tools** give agents the ability to actually *do* things in the world.

## Tool Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Agent                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Tool Registry                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │kubectl  │ │terraform│ │ github  │ │  slack  │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  External APIs   │
                    │  & Systems       │
                    └─────────────────┘
```

## Defining Tools

### Tool Schema

Every tool needs a clear schema:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum

class KubectlGetSchema(BaseModel):
    """Schema for kubectl get command."""

    resource: Literal["pods", "deployments", "services", "configmaps", "secrets"]
    name: Optional[str] = Field(None, description="Resource name")
    namespace: str = Field("default", description="Kubernetes namespace")
    selector: Optional[str] = Field(None, description="Label selector")
    output: Literal["json", "yaml", "wide"] = Field("json")

class KubectlTool(Tool):
    """Tool for executing kubectl commands."""

    name = "kubectl"
    description = "Execute kubectl commands against Kubernetes cluster"
    input_schema = KubectlGetSchema
    output_schema = dict

    # Security constraints
    allowed_resources = ["pods", "deployments", "services"]
    denied_resources = ["secrets"]  # Don't allow reading secrets
    requires_approval = ["delete", "apply"]

    async def execute(self, params: KubectlGetSchema) -> ToolResult:
        # Validate permissions
        if params.resource in self.denied_resources:
            return ToolResult.error(f"Access to {params.resource} is denied")

        # Build command
        cmd = self.build_command(params)

        # Execute
        result = await self.run_command(cmd)

        return ToolResult.success(result)
```

### Tool Categories

| Category | Examples | Use Case |
|----------|----------|----------|
| **Infrastructure** | kubectl, terraform, aws-cli | Manage cloud resources |
| **CI/CD** | GitHub Actions, Jenkins, ArgoCD | Build and deploy |
| **Observability** | Prometheus, Datadog, Grafana | Monitor systems |
| **Communication** | Slack, PagerDuty, Jira | Notify and coordinate |
| **Data** | SQL, Redis, S3 | Store and retrieve data |

## Common DevOps Tools

### Kubernetes (kubectl)

```python
class KubectlTool(Tool):
    """Interact with Kubernetes clusters."""

    async def get_pods(
        self,
        namespace: str = "default",
        selector: str | None = None
    ) -> list[dict]:
        """List pods in namespace."""
        cmd = f"kubectl get pods -n {namespace} -o json"
        if selector:
            cmd += f" -l {selector}"

        result = await self.run(cmd)
        return json.loads(result.stdout)["items"]

    async def logs(
        self,
        pod: str,
        namespace: str = "default",
        container: str | None = None,
        tail: int = 100
    ) -> str:
        """Get pod logs."""
        cmd = f"kubectl logs {pod} -n {namespace} --tail={tail}"
        if container:
            cmd += f" -c {container}"

        result = await self.run(cmd)
        return result.stdout

    async def describe(
        self,
        resource: str,
        name: str,
        namespace: str = "default"
    ) -> dict:
        """Describe a resource."""
        cmd = f"kubectl describe {resource} {name} -n {namespace}"
        result = await self.run(cmd)
        return self.parse_describe(result.stdout)
```

### Terraform

```python
class TerraformTool(Tool):
    """Execute Terraform operations."""

    async def plan(self, workspace: str) -> PlanResult:
        """Run terraform plan."""
        # Change to workspace
        os.chdir(workspace)

        # Run plan
        result = await self.run("terraform plan -out=tfplan")

        # Parse plan output
        return self.parse_plan(result.stdout)

    async def apply(self, workspace: str, auto_approve: bool = False) -> ApplyResult:
        """Apply terraform plan."""
        cmd = "terraform apply"
        if auto_approve:
            cmd += " -auto-approve"

        result = await self.run(cmd)
        return self.parse_apply(result.stdout)

    async def show_state(self, workspace: str) -> dict:
        """Show current state."""
        os.chdir(workspace)
        result = await self.run("terraform show -json")
        return json.loads(result.stdout)
```

### GitHub API

```python
class GitHubTool(Tool):
    """Interact with GitHub."""

    def __init__(self, token: str):
        self.token = token
        self.client = github.Github(token)

    async def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> PullRequest:
        """Create a pull request."""
        repository = self.client.get_repo(repo)
        pr = repository.create_pull(
            title=title,
            body=body,
            head=head,
            base=base
        )
        return pr

    async def get_workflow_runs(
        self,
        repo: str,
        workflow: str,
        branch: str = "main"
    ) -> list[WorkflowRun]:
        """Get recent workflow runs."""
        repository = self.client.get_repo(repo)
        workflow = repository.get_workflow(workflow)
        runs = workflow.get_runs(branch=branch)
        return list(runs)[:10]

    async def merge_pr(self, repo: str, pr_number: int) -> bool:
        """Merge a pull request."""
        repository = self.client.get_repo(repo)
        pr = repository.get_pull(pr_number)
        return pr.merge()
```

## Error Handling

### Retry Logic

```python
import asyncio
from functools import wraps

def with_retry(
    max_retries: int = 3,
    backoff_base: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Retry decorator for tool execution."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        backoff = backoff_base * (2 ** attempt)
                        await asyncio.sleep(backoff)
                        continue

            raise ToolError(f"Failed after {max_retries} retries: {last_exception}")

        return wrapper
    return decorator

class KubectlTool(Tool):
    @with_retry(max_retries=3, exceptions=(ConnectionError, TimeoutError))
    async def get_pods(self, namespace: str) -> list[dict]:
        return await self.run(f"kubectl get pods -n {namespace} -o json")
```

### Error Classification

```python
class ToolError(Exception):
    """Base error for tool execution."""
    pass

class PermissionDeniedError(ToolError):
    """User lacks permission for operation."""
    pass

class ResourceNotFoundError(ToolError):
    """Requested resource doesn't exist."""
    pass

class RateLimitError(ToolError):
    """Rate limit exceeded."""
    pass

class TimeoutError(ToolError):
    """Operation timed out."""
    pass

def classify_error(error: Exception) -> str:
    """Classify error for appropriate handling."""
    if "permission denied" in str(error).lower():
        return "permission"
    elif "not found" in str(error).lower():
        return "not_found"
    elif "rate limit" in str(error).lower():
        return "rate_limit"
    elif "timeout" in str(error).lower():
        return "timeout"
    else:
        return "unknown"
```

## Tool Composition

### Chaining Tools

```python
async def diagnose_service(service: str, namespace: str) -> dict:
    """Diagnose issues with a service by chaining tools."""

    # 1. Get pods
    pods = await kubectl.get_pods(namespace, selector=f"app={service}")

    # 2. Check pod status
    issues = []
    for pod in pods:
        if pod["status"]["phase"] != "Running":
            issues.append({
                "pod": pod["metadata"]["name"],
                "issue": pod["status"]["phase"],
            })

    # 3. Get logs for problematic pods
    for issue in issues:
        logs = await kubectl.logs(issue["pod"], namespace)
        issue["logs"] = logs[:500]  # Truncate

    # 4. Get events
    events = await kubectl.get_events(namespace, field_selector=f"involvedObject.name={service}")

    return {
        "service": service,
        "pods": pods,
        "issues": issues,
        "events": events[:10],
    }
```

### Parallel Execution

```python
async def health_check(services: list[str]) -> dict:
    """Run health checks in parallel."""
    results = await asyncio.gather(*[
        check_service_health(service)
        for service in services
    ], return_exceptions=True)

    return {
        service: result if not isinstance(result, Exception) else {"error": str(result)}
        for service, result in zip(services, results)
    }
```

## Security Considerations

### Principle of Least Privilege

```python
class SecureTool(Tool):
    """Tool with security constraints."""

    def __init__(self, permissions: list[str]):
        self.permissions = permissions
        self.audit_log = []

    async def execute(self, action: str, params: dict) -> ToolResult:
        # Check permission
        required_permission = self.get_required_permission(action)
        if required_permission not in self.permissions:
            await self.audit("DENIED", action, params)
            return ToolResult.error(f"Permission denied: {required_permission}")

        # Audit trail
        await self.audit("ALLOWED", action, params)

        # Execute
        result = await self._execute(action, params)

        return result

    async def audit(self, status: str, action: str, params: dict):
        """Record action in audit log."""
        self.audit_log.append({
            "timestamp": datetime.now(),
            "status": status,
            "action": action,
            "params": params,
        })
```

### Input Validation

```python
class ValidatedTool(Tool):
    """Tool with input validation."""

    async def execute(self, params: dict) -> ToolResult:
        # Validate schema
        try:
            validated = self.input_schema(**params)
        except ValidationError as e:
            return ToolResult.error(f"Invalid parameters: {e}")

        # Sanitize inputs
        sanitized = self.sanitize(validated.dict())

        # Check for dangerous patterns
        if self.contains_dangerous_patterns(sanitized):
            return ToolResult.error("Dangerous pattern detected in input")

        return await self._execute(sanitized)

    def contains_dangerous_patterns(self, params: dict) -> bool:
        """Check for command injection patterns."""
        dangerous = [";", "&&", "||", "`", "$(", "|"]
        for value in params.values():
            if isinstance(value, str):
                for pattern in dangerous:
                    if pattern in value:
                        return True
        return False
```

## Testing Tools

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def kubectl_tool():
    return KubectlTool(cluster="test")

@pytest.mark.asyncio
async def test_get_pods(kubectl_tool):
    """Test getting pods."""
    with patch.object(kubectl_tool, 'run') as mock_run:
        mock_run.return_value = AsyncMock(
            stdout='{"items": [{"metadata": {"name": "pod-1"}}]}'
        )

        pods = await kubectl_tool.get_pods("default")

        assert len(pods) == 1
        assert pods[0]["metadata"]["name"] == "pod-1"

@pytest.mark.asyncio
async def test_permission_denied(kubectl_tool):
    """Test permission handling."""
    kubectl_tool.denied_resources = ["secrets"]

    result = await kubectl_tool.get_resource("secrets", "my-secret")

    assert result.success is False
    assert "denied" in result.error.lower()
```

## Summary

- **Tools** extend agent capabilities beyond text generation
- **Schemas** define inputs, outputs, and constraints
- **Error handling** and retries are essential for reliability
- **Security** requires validation, permissions, and auditing
- **Testing** ensures tools work correctly

In the next chapter, we'll cover **Implementation Overview** to build complete agents.

---

<Note type="beginner">
Think of tools like a toolbox. Each tool has a specific purpose, inputs (what you give it), outputs (what it produces), and safety guidelines (when NOT to use it).
</Note>

<CodeExample language="python">
# Tool definition example
class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"

    async def execute(self, params: dict) -> ToolResult:
        # Validate input
        # Check permissions
        # Execute action
        # Handle errors
        # Return result
        return ToolResult.success({"result": "done"})
</CodeExample>

<BusinessValue>
Well-designed tools reduce incident resolution time by 60-80%. Agents can diagnose and fix issues in seconds that would take humans 15-30 minutes.
</BusinessValue>

</ChapterContent>
