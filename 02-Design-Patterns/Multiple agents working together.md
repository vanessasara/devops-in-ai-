
---
tags: [patterns, multi-agent, architecture]
---

# Multi-Agent Systems

## Understanding Multi-Agent AI Systems

When working with **multiple AI agents**, there are three important architectural patterns to understand:

1. **Orchestrator Agent**
    
2. **Triage Agent**
    
3. **Agents as Tools**
    

Each plays a different role in how tasks are delegated and executed.

---

# 1. Orchestrator Agent

An **orchestrator agent** acts like a **supervisor** that manages multiple agents simultaneously.

This agent has access to several **specialized agents**, each with different skills. The orchestrator decides:

- Which agent should perform a specific task
    
- How tasks should be distributed
    
- Whether the results produced by worker agents are correct
    

The orchestrator continuously **monitors and evaluates the work** performed by other agents.

If a worker agent fails, produces incorrect output, or cannot complete a task, the **orchestrator remains responsible** for the overall outcome. The task ownership never leaves the orchestrator — it simply coordinates and verifies the work of other agents.

In simple terms:

**Orchestrator = Manager + Quality Controller**

---

# 2. Triage Agent

A **triage agent** acts as the **first point of contact** with the user. Its primary role is to:

- Understand user requests
    
- Handle simple tasks directly
    
- Route complex tasks to the correct specialized agent
    

For example:

1. A user asks general questions about an organization:
    
    - What does the company do?
        
    - Where is it located?
        

The **triage agent can answer these questions itself**.

2. Then the user asks:
    

> “Can you book a meeting with someone from your organization?”

At this point, the triage agent recognizes that **meeting scheduling is outside its responsibility**. It transfers the **entire conversation context** to a specialized **booking agent**.

Once this handoff happens:

- The **booking agent now owns the task**
    
- It handles scheduling
    
- It communicates with the user if needed
    
- It ensures the meeting is successfully scheduled
    

If the meeting fails to schedule, the responsibility lies with the **booking agent**, not the triage agent.

In short:

**Triage Agent = Router / Dispatcher**

---

# 3. Agents as Tools

This is one of the **most powerful multi-agent patterns**.

In this model, the orchestrator agent **does not transfer ownership** of the task. Instead, it **calls other agents as tools**.

This means:

- The orchestrator remains responsible for the task
    
- Worker agents simply perform **specific subtasks**
    
- The orchestrator evaluates their outputs before proceeding
    

Example workflow:

1. Orchestrator receives a complex task.
    
2. It calls a **Research Agent** to gather information.
    
3. It calls a **Code Agent** to generate code.
    
4. It calls a **Review Agent** to validate the solution.
    

However:

- None of these agents own the task.
    
- They are simply **tools being used by the orchestrator**.
    

The orchestrator still:

- Controls the process
    
- Validates outputs
    
- Combines results
    
- Delivers the final answer
    

In simple terms:

**Agents as Tools = Specialized capabilities used by a controlling agent**

---

# Simple Mental Model

|Pattern|Responsibility|Role|
|---|---|---|
|**Orchestrator Agent**|Keeps ownership of the task|Manages and verifies other agents|
|**Triage Agent**|Transfers ownership|Routes requests to the correct agent|
|**Agents as Tools**|Ownership stays with orchestrator|Agents perform subtasks|

---

If you're building **agentic systems with frameworks like**

- OpenAI Agents SDK
    
- LangGraph
    
- AutoGen
    

these **three patterns are the core architectural building blocks** for designing scalable multi-agent systems.

---