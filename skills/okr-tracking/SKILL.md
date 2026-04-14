---
name: okr-tracking
description: "Track OKR and KPI progress — query metrics, generate progress reports, and identify at-risk objectives. Use when the user asks about OKR status, goal tracking, or KPI dashboards."
---

# OKR / KPI Tracking

Monitor and report on objectives, key results, and key performance indicators.

## When to Use

- Manager asks "how are we tracking on OKRs?" or "Q2 goal status"
- User wants a progress report for a specific objective
- User needs to identify at-risk key results
- Preparing for a quarterly review or planning session

## Workflow

### Data Sources

OKR data may live in:
1. **Notion** (if MCP connected) — OKR databases, goal pages
2. **SQL Database** (if configured) — metrics tables
3. **Jira/Linear** (if MCP connected) — epics as objectives, tickets as key results
4. **User-provided context** — manual input of current numbers

### Generate OKR Status Report

```markdown
## OKR Status: {Team/Department} — {Period}

### Objective 1: {Objective Title}
**Overall**: 🟢 On Track (72%)

| Key Result | Target | Current | Progress | Status |
|-----------|--------|---------|----------|--------|
| {KR 1}   | 100    | 72      | 72%      | 🟢     |
| {KR 2}   | 50     | 30      | 60%      | 🟡     |
| {KR 3}   | 10     | 3       | 30%      | 🔴     |

### Objective 2: {Objective Title}
**Overall**: 🟡 At Risk (45%)

| Key Result | Target | Current | Progress | Status |
|-----------|--------|---------|----------|--------|
| ...       | ...    | ...     | ...      | ...    |

---

### Summary
- **On Track**: {N} objectives
- **At Risk**: {N} objectives
- **Behind**: {N} objectives

### Action Items
- KR 3 under Objective 1 is at 30% — needs intervention by {owner}
- Objective 2 may not be achievable this quarter — consider scope adjustment
```

### Status Indicators

| Progress | Status | Icon |
|----------|--------|------|
| ≥70%     | On Track | 🟢 |
| 40-69%   | At Risk  | 🟡 |
| <40%     | Behind   | 🔴 |

Adjust thresholds based on time remaining in the period.

### KPI Dashboard

For operational KPIs (response time, uptime, customer satisfaction):

```markdown
## KPI Dashboard — {date}

| KPI | Target | Current | Trend | Status |
|-----|--------|---------|-------|--------|
| API Uptime | 99.9% | 99.95% | ↑ | 🟢 |
| Avg Response Time | <200ms | 185ms | → | 🟢 |
| Customer NPS | >50 | 42 | ↓ | 🟡 |
```

## Notes

- If OKR data isn't in a structured system, ask the user to provide current numbers and track them in a Notion page or spreadsheet
- Progress percentages should account for time elapsed — 50% progress at the midpoint is on track, 50% at 80% through is behind
- Don't just report numbers — provide the "so what" interpretation and recommended actions
- For quarterly reviews, include a comparison with the previous quarter
