---
tags: [concepts, agent, react, role]
---

# What Your Agent Needs to Know

A language model on its own is just a tool. An agent has a specific purpose, defined capabilities, and a structured way of working through problems. This note covers the building blocks that make a logging agent actually useful.

---

## Role — Who Is Your Agent?

The role defines your agent's identity and area of expertise. It is set as the **system message** at the start of every conversation with the model, and it acts as the lens through which all log analysis happens.

Examples:

- _"You are a DevOps engineer specializing in application error analysis"_
- _"You are a database reliability expert who investigates performance issues"_
- _"You are a security analyst monitoring for suspicious activity in logs"_

The role matters because it changes what the model looks for. A security-focused agent will notice different patterns in the same logs than a performance-focused agent.

You can create multiple specialized agents on the same underlying model by changing only the role:

- **Error analysis agent** — focuses on application failures
- **Performance agent** — looks for slow queries and bottlenecks
- **Security agent** — monitors for suspicious patterns
- **Cost optimization agent** — identifies wasteful resource usage

---

## Tasks — What Should Your Agent Do?

Tasks are the specific actions the agent performs during an analysis session. The role defines who the agent is — tasks define what it does.

Common tasks for a logging agent:

1. Analyze recent error logs
2. Identify patterns across multiple services
3. Correlate errors with deployment events
4. Suggest likely root causes
5. Recommend remediation steps

Each task is defined with:

- A **name** — for identification
- A **description** — what the task should accomplish
- A **priority** — which order to execute them in

Tasks run in sequence. The output from one task feeds into the next. Error detection feeds into pattern analysis, which feeds into correlation, and so on. This allows the agent to build a complete picture step by step.

---

## Tools — How Your Agent Takes Action

Tools are functions the agent can call to do things beyond analyzing text. They give the agent hands and feet.

Useful tools for a logging agent:

- Query Elasticsearch for specific log patterns
- Check service health endpoints
- Look up recent deployments
- Create Jira tickets
- Send Slack notifications
- Restart services (with appropriate safeguards)

You define what each tool does and what parameters it needs. The model then decides when to use each tool based on what it discovers in the logs.

**Example flow when the agent detects database connection errors:**

1. Call `search_logs` to find more database-related entries
2. Call `check_service_health` to verify the database is actually down
3. Call `notify_team` to alert the on-call engineer

---

## Putting It Together — The Agent Structure

A logging agent typically operates in this sequence:

1. **Initialization** — Set up the role, tasks, and tools
2. **Log Retrieval** — Pull relevant logs from data sources
3. **Context Building** — Start the conversation with the AI model, beginning with the role
4. **Task Execution** — Run through each task in sequence
5. **Result Compilation** — Gather all findings and recommendations

Your agent maintains state throughout this process:

- The **role** — who it is
- The **tasks** — what it does
- The **tools** — its capabilities
- The **conversation history** — context from the current analysis session
- The **AI client** — the connection to the model

---

## Memory — Remembering Past Analysis

Memory is what makes an agent smarter over time rather than starting fresh every session.

**Short-term memory** is the conversation history within a single analysis session. Each task sees the results of previous tasks. This is just a list of messages maintained during the conversation.

**Long-term memory** persists across sessions. The agent stores important findings and can recall them later. Useful things to store:

- Past incidents and their resolutions
- Recurring error patterns
- Service-specific quirks or known issues
- Solutions that worked in the past

Implementation is straightforward — save key findings to a JSON file or database with timestamps and metadata. When analyzing new logs, check memory first. If the same pattern appeared before and was resolved, the agent already knows how.

---

## Applying the ReAct Pattern

ReAct (Reasoning + Acting) is the recommended pattern for a logging agent. The agent alternates between **thinking** and **doing** in a continuous loop until it reaches a conclusion.

This matches how humans debug. You do not know the root cause upfront — you form hypotheses, gather evidence, and refine your understanding iteratively.

---

### The ReAct Loop

Each iteration has three phases:

**1. Thought** The agent analyzes what it currently knows and decides what to do next. It explicitly states its reasoning: _"Based on X, I believe Y. To confirm, I should Z."_

**2. Action** The agent calls a tool to gather more information. The implementation parses the agent's response, validates the action, executes the tool function, and captures the result.

**3. Observation** The results from the action are added to the conversation history. The agent now has new information to reason about in the next iteration.

This repeats until the agent reaches a conclusion or hits a boundary.

---

### Setting Loop Boundaries

The ReAct loop needs exit conditions to prevent it from running indefinitely:

- **Maximum iterations** — typically 5 to 10. If the agent hits this limit without a conclusion, it returns its best assessment with a note that further investigation is needed.
- **Conclusion detection** — watch for the agent to explicitly signal it is done, such as with keywords like `CONCLUSION:` or `FINAL ANSWER:`.
- **Cost limits** — each iteration calls the model. Set a budget per analysis session and stop if it is exceeded.
- **Time limits** — set a wall-clock timeout (e.g., 2 minutes) to handle cases where API calls are slow.

---

### Handling Edge Cases

**No data available** — if a tool returns empty results, the agent should recognize this and try a different approach rather than getting stuck.

**Contradictory information** — when different data sources contradict each other, the agent should state the contradiction explicitly rather than picking one arbitrarily.

**Tool failures** — if a tool call fails (timeout, permission denied), pass that information back to the agent so it can try a different tool or work with incomplete data.

**Circular reasoning** — if the agent uses the same tool with the same parameters twice in a row, intervene and prompt it to try a different approach.

---

## Complete ReAct Example

**Scenario:** Error rate spike in API service

**Initial input:**

```
200 errors in the last 5 minutes
Error type: Connection timeout
Affected service: api-gateway
```

**Iteration 1** Thought: _Connection timeout in api-gateway. Could be network issues, backend problems, or resource exhaustion. Check if backend services are healthy._ Action: `check_service_health(service="payment-service")` Observation: Payment service health check failing. Response time 30000ms (timeout).

**Iteration 2** Thought: _Payment service is timing out. Could be a recent change or resource problem. Check memory usage._ Action: `get_metrics(service="payment-service", metric="memory_usage", time_range="1h")` Observation: Memory started at 40%, now at 98%. Steady increase over the last 45 minutes.

**Iteration 3** Thought: _Memory leak pattern. Rising usage correlates with timeouts. Check for a recent deployment._ Action: `check_deployments(service="payment-service", hours_back=4)` Observation: Deploy 50 minutes ago — version 2.4.1. Changes include a new caching layer implementation.

**Iteration 4** Thought: _Deploy timing matches the memory leak start. New caching layer likely has a memory leak. Check for similar past incidents._ Action: `search_incidents(keywords="payment service memory leak cache")` Observation: No similar incidents found in the past 90 days.

**Conclusion:** Root cause is a memory leak in payment-service version 2.4.1, introduced 50 minutes ago. The new caching layer is not releasing memory properly, causing the service to slow down and timeout requests. This cascades to api-gateway connection timeouts.

Recommendation: Rollback to version 2.4.0 immediately. Investigate the caching implementation for memory leaks before redeploying.

---

## Why ReAct Works for Log Analysis

- **Matches how humans debug** — gather evidence, form hypotheses, test them iteratively
- **Transparent** — you can see exactly what the agent is thinking and why it chose each action
- **Flexible** — if the agent discovers something unexpected, it can change direction mid-analysis
- **Handles uncertainty** — when information is incomplete, the agent seeks more data rather than guessing
- **Cost-effective** — single agent with a simple loop keeps complexity and costs down compared to multi-agent systems