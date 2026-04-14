---
name: feature-tracking
description: "Track and prioritize feature requests — aggregate from Jira/Linear, categorize by theme, and apply prioritization frameworks (RICE/ICE). Use when the user wants to review feature requests, prioritize the backlog, or assess feature impact."
---

# Feature Tracking & Prioritization

Aggregate, categorize, and prioritize feature requests for product decision-making.

## When to Use

- PM asks "what feature requests do we have?" or "prioritize the backlog"
- User wants to apply RICE/ICE scoring to features
- User needs to categorize features by theme or customer segment
- Preparing for a sprint planning or roadmap review

## Workflow

### Aggregate Feature Requests

Pull from available sources:
1. **Jira/Linear** — issues labeled as feature request, enhancement, or user story
2. **Gmail** — emails from customers or internal stakeholders requesting features
3. **Slack** — messages in product feedback channels

### Categorize by Theme

Group features into product themes:
- User Experience, Performance, Integrations, Security, New Capability, etc.

### Prioritize with RICE Framework

| Feature | Reach | Impact | Confidence | Effort | RICE Score |
|---------|-------|--------|------------|--------|------------|
| {Feature A} | 500 users/mo | 3 (high) | 80% | 2 weeks | {score} |
| {Feature B} | 100 users/mo | 2 (med) | 60% | 1 week | {score} |

**RICE = (Reach x Impact x Confidence) / Effort**

### Alternative: ICE Framework

| Feature | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Score |
|---------|---------------|-------------------|-------------|-----------|
| {Feature A} | 8 | 7 | 4 | 224 |

**ICE = Impact x Confidence x Ease**

### Output

```markdown
## Feature Backlog — Prioritized

### Tier 1: High Priority
1. **{Feature}** — RICE: {score} | Theme: {theme}
   {One-line description}. Requested by: {source}

### Tier 2: Medium Priority
...

### Tier 3: Low Priority / Parking Lot
...

### Rejected / Deferred
- {Feature} — Reason: {why it was deprioritized}
```

## Notes

- Ask the user for Reach and Confidence estimates — these require product judgment, not just data
- Impact and Effort can be estimated from ticket descriptions and historical velocity
- Always show the framework you're using and the raw scores — PMs need transparency in prioritization
- Don't prioritize in a vacuum — consider the current roadmap, team capacity, and strategic goals
