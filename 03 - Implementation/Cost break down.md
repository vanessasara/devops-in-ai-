---
tags: [implementation, cost, roi]
---

# Cost Breakdown

Adding an AI agent means you need more services in your infrastructure. Let's do the math:

| Component | Cost | Status |
|-----------|------|--------|
| Existing logging (Elasticsearch/Kibana) | $500-1000/month | Already paying |
| AI agent LLM costs | $300/month | New |
| AI agent hosting | $75/month | New |
| Engineering time | 4-6 weeks initial | One-time |
| Maintenance | ~5 hours/month | Ongoing |

---

## Is It Worth It?

The choice is yours. Make a clear ROI calculation and discuss with your team:

- How often do incidents occur?
- How long do investigations take?
- How much engineering time is spent debugging?

If AI agents significantly reduce incident resolution time, they may justify the additional cost.

---

> See [[../00 - Introduction/README|Introduction]] for the full context on when AI agents make sense.