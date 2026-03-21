# OpenAI Agents SDK

> **Note:** The book this project follows teaches these concepts using LangChain. This project replaces LangChain entirely with the OpenAI Agents SDK + LiteLLM + Gemini. The concepts are the same. The code is simpler.

---

## What the Agents SDK Is

The OpenAI Agents SDK is a lightweight framework for building agentic AI applications. It handles the boring parts — tool execution, the reasoning loop, result collection — so you focus on what makes your agent useful.

If you've read the LangChain chapter in the book, the Agents SDK covers the same ground as Models + Chains + Agents + Tools combined. But instead of learning six separate abstractions, you learn three.

---

## The Three Primitives

### Agent

The `Agent` is where you define who the agent is and what it can do.

You give it a name, a set of instructions (the system prompt), a model to use, and a list of tools. That's it. The agent doesn't execute anything — it's just a definition.

The **instructions** field is your system prompt. Write it like you're briefing a junior engineer. Tell it its role, what it should do, what workflow to follow, and what its limitations are.

The **model** is provided through `LitellmModel`. You pass the model name as a string like `"gemini/gemini-3-flash-preview"`. LiteLLM translates this into the correct API call. If you want to switch to Claude or GPT later, you change one string — nothing else changes.

### function_tool

`@function_tool` is a decorator that turns a plain Python function into something the agent can call.

Three things matter when writing a tool:

- **The docstring** — the agent reads this to decide when and how to use the tool. Write it as an instruction, not a description.
- **Type hints** — the SDK uses these to validate inputs before calling your function.
- **The return value** — this is what the agent sees after the tool runs. Make it descriptive so the agent can reason about it.

### Runner

`Runner.run()` executes the agent on a given input and returns the final result.

Internally it handles the complete ReAct loop — the agent reasons, calls a tool, observes the result, reasons again, calls another tool if needed, and eventually produces a final answer. You call `Runner.run()` and get back `result.final_output`. The loop is invisible.

This is the biggest difference from LangChain. In LangChain you manually check for tool calls, execute them, collect results, and feed them back. With the Agents SDK, `Runner.run()` does all of that.

---

## LiteLLM — The Model Bridge

LiteLLM sits between your code and the model provider. You write code once using the Agents SDK interface. LiteLLM handles the translation to Gemini's API, OpenAI's API, Anthropic's API, or any other provider.

The model name format is `"provider/model-name"` — for example `"gemini/gemini-3-flash-preview"` or `"openai/gpt-4o"` or `"anthropic/claude-sonnet-4-6"`.

To switch models you change one environment variable. Your agent code, your tools, your FastAPI routes — none of it changes.

---

## Why Not LangChain

LangChain is a capable framework with a large ecosystem. It makes sense for complex pipelines with many steps and providers.

For an agent that reads logs and answers questions, it introduces more abstraction than the problem requires. The Agents SDK is purpose-built for agentic use cases. The result is less code, fewer moving parts, and easier debugging.

The book uses LangChain. This project uses the Agents SDK. The chapters in this vault rewrite the book's guidance for the actual stack being used.

---

