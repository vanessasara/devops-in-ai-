---
title: Data Retrieval
tags: [implementation, data, logs]
---

---
tags: [implementation, data, retrieval]
---

# Getting Logs into Your Agent

Your AI model can only analyze logs it actually has. Data retrieval is the layer responsible for pulling logs from wherever they live and feeding them to the agent in a structured, manageable way.

This sounds obvious — but this is where most projects get stuck.

---

## Where Logs Come From

In a typical DevOps environment, logs are spread across multiple sources:

- **Application logs** → Elasticsearch
- **Container logs** → Kubernetes
- **System logs** → CloudWatch
- **Database logs** → RDS
- **Load balancer logs** → S3

Your agent needs to connect to all of these, retrieve what is relevant, and organize it in a way the model can actually process.

---

## Building a Retrieval Layer

The pattern for retrieving logs follows the same steps regardless of which source you are using:

1. Connect to the log source (Elasticsearch, CloudWatch, etc.)
2. Define a time range (e.g., last hour, last 5 minutes)
3. Filter by criteria — severity level, service name, keywords
4. Limit results to a manageable count
5. Extract and format the log messages

The goal is a **consistent interface** that your agent calls the same way, no matter where the logs come from:

```python
retrieve_logs(source, time_range, filters)
```

The agent should not need to know whether logs live in Elasticsearch or CloudWatch. It just calls the function and gets back formatted results.

For Elasticsearch you use their Python client. For CloudWatch you use boto3. For Kubernetes you use the Kubernetes Python client to fetch pod logs. The underlying implementation is hidden behind the same interface every time.

---

## Dealing with Volume

Production systems can generate thousands of log entries per minute. You cannot send all of them to an AI model — it would be slow, expensive, and likely exceed the context window.

Instead, **filter intelligently before anything reaches the model**:

- Retrieve only logs above a certain severity (ERROR, WARN)
- Focus on a narrow time window — start with the last 5 minutes
- Pull logs from services that are actively showing problems
- Sample logs when volume is unusually high
- Aggregate similar entries before sending

**Start narrow, then widen.** Begin with 5 minutes and 50 logs. Expand only if you need more context. This keeps API costs low and response times fast.

---

## Handling Volume Spikes

When incidents happen, log volume can spike from hundreds to thousands of entries per minute. Your agent needs a strategy to handle this without exceeding context limits or making costs unpredictable.

The solution is a **two-layer approach** — filter first, then summarize if filtering alone is not enough.

---

### Layer 1 — Aggressive Pre-Filtering

Before any logs reach the AI model, apply intelligent filtering. Think of this as a bouncer — only the most critical entries get through.

**Priority-based selection** FATAL and ERROR logs always get analyzed first. WARN and INFO are included only when there is room. This ensures serious problems are never skipped, even when logs are flooding in.

**Deduplication** If the same "Connection timeout" error appears 100 times, you do not send all 100 entries. You send it once with metadata attached:

- How many times it occurred
- First and last occurrence timestamps
- Which services were affected

The model understands "this happened 127 times over 5 minutes" just as well as reading 127 individual entries — actually better, because it gets the pattern immediately rather than having to infer it.

**Service-aware filtering** Prioritize logs from services that are actually experiencing issues. If your payment service has a 50% error rate but your auth service is healthy, focus on payment logs first. You determine which services need attention based on error rates, then pull their logs preferentially.

---

### Layer 2 — Progressive Summarization

When filtering alone is not enough to bring log volume down to a manageable level, use a **two-pass approach**.

The key insight here is that you do not need your most capable model for the first pass.

**Pass 1 — Quick Summarization** Take chunks of filtered logs and create one-line summaries using a fast, cheap model. Each summary captures what happened, how often, when, and a brief description:

```
[ERROR] DB timeout (47 times, 10:15-10:18) - payment-db unreachable
[WARN]  High memory (3 times, 10:16-10:17) - api-gateway at 87% usage
[ERROR] API 500s (23 times, 10:17-10:19) - downstream service failures
```

This reduces 200 raw log lines down to roughly 20 structured summaries.

**Pass 2 — Detailed Analysis** Send those summaries — not the raw logs — to your main, more capable model for root cause analysis. The expensive model now works with clean, structured information instead of a raw log dump.

This keeps you within context limits, preserves the critical information, and because the first pass uses a cheaper model, your costs do not spike during incidents.

---

## Summary

|Problem|Solution|
|---|---|
|Logs come from many sources|Build a unified retrieval interface|
|Volume is too high to send everything|Pre-filter by severity, time window, and service|
|Duplicate entries waste context|Deduplicate and attach occurrence metadata|
|Spikes exceed context limits|Use two-pass: cheap model summarizes, main model analyzes|

The goal is consistent analysis quality regardless of log volume — whether it is a quiet Tuesday or a major outage, the agent uses the right strategy to stay within limits while keeping costs predictable.

---

Next: [What Your Agent Needs to Know](../01%20-%20Core%20Concepts/What%20Your%20Agent%20Needs%20to%20Know.md)