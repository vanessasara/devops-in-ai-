
---
title: Understanding the Core Building Blocks
tags: [concepts, fundamentals, llm]
---

# Understanding the Core Building Blocks

Before building an AI agent, define the essential pieces clearly. A reliable system does not come from random components; it comes from intentional design.

---

## How LLMs Work (Practical View)

You do not need deep expertise in neural network internals to build an effective DevOps agent.

What you do need to understand:

- An LLM receives input text (for example, user questions and log excerpts)
- It identifies patterns from its training and provided context
- It generates a response based on that context and prompt instructions

In this project, the model behaves as a reasoning layer that interprets logs and explains likely causes in plain language.

---

## Model Hosting Options

You typically have two deployment options:

1. **Cloud APIs**
   - Fastest way to ship
   - Minimal infrastructure management
   - Data is sent to a provider endpoint

2. **Self-hosted models**
   - Greater control over data residency
   - More infrastructure and operational overhead
   - Useful when privacy or compliance requirements are strict

Both can work. Choose based on budget, latency, governance, and team capability.

---

## How the Model Gets Log Data

An LLM cannot access your logs by itself. You must provide data through a retrieval layer and tool calls.

That is why data retrieval is a core architectural concern:

- Connect to log sources
- Filter and format logs
- Pass relevant context to the model

See [Data Retrieval](../03%20-%20Implementation/Data%20Retrieval.md) for implementation patterns.