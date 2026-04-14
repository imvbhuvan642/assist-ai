---
name: competitive-analysis
description: "Research competitors — search the web for competitor news, product launches, pricing changes, and market movements. Use when the PM needs competitive intelligence or wants to benchmark against competitors."
---

# Competitive Analysis

Research and synthesize competitive intelligence using web search.

## When to Use

- PM asks "what's {competitor} doing?" or "competitive landscape"
- Preparing for a strategy meeting or board presentation
- A competitor launches a new feature or changes pricing
- Benchmarking the product against alternatives

## Workflow

### Step 1: Research

Use `internet_search` with targeted queries:
- `"{competitor name}" product launch 2026`
- `"{competitor name}" pricing changes`
- `"{competitor name}" vs "{our product}" comparison`
- `"{competitor name}" funding news`
- `"{market category}" market trends`

### Step 2: Compile Intelligence

```markdown
## Competitive Brief: {Competitor Name}

**Last Updated**: {date}

### Overview
- **Product**: {what they do}
- **Target Market**: {who they serve}
- **Positioning**: {how they differentiate}

### Recent Activity
- {date}: {event — product launch, funding, partnership, pricing change}
- {date}: {event}

### Product Comparison

| Feature | Us | {Competitor} | Notes |
|---------|-----|-------------|-------|
| {Feature 1} | ✅ | ✅ | They have X, we have Y |
| {Feature 2} | ✅ | ❌ | Our differentiator |
| {Feature 3} | ❌ | ✅ | Gap to address |

### Pricing Comparison (if public)
| Plan | Us | {Competitor} |
|------|-----|-------------|
| Free | {details} | {details} |
| Pro  | {details} | {details} |

### Strengths & Weaknesses
**Their Strengths**: {what they do well}
**Their Weaknesses**: {where we win}
**Opportunities**: {gaps we can exploit}
**Threats**: {where they might outpace us}

### Implications for Our Product
1. {Specific recommendation based on findings}
2. {Specific recommendation}
```

### Multi-Competitor Landscape

For broader market analysis:

```markdown
## Competitive Landscape — {Category}

| | Us | Competitor A | Competitor B | Competitor C |
|---|---|---|---|---|
| Core Strength | {X} | {X} | {X} | {X} |
| Pricing | {$} | {$} | {$} | {$} |
| Target | {who} | {who} | {who} | {who} |
| Recent Move | {what} | {what} | {what} | {what} |
```

## Notes

- Always cite sources — include URLs where findings come from
- Distinguish between facts (from official announcements) and speculation (from blogs/forums)
- Web search results may be outdated — note the date of each source
- Competitive analysis is most useful when it leads to specific product recommendations
- For ongoing tracking, suggest the PM save key findings and set up periodic re-analysis
