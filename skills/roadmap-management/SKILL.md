---
name: roadmap-management
description: "Manage product roadmaps — pull epics and milestones from Jira/Linear, cross-reference with OKRs, identify at-risk items, and generate roadmap status views. Use when the PM needs to review roadmap progress or prepare roadmap updates."
---

# Roadmap Management

Track and communicate product roadmap progress.

## When to Use

- PM asks "roadmap status" or "how's the Q2 roadmap looking?"
- Preparing for a roadmap review meeting
- Identifying which initiatives are on track, at risk, or behind
- Generating a roadmap view for stakeholders

## Workflow

### Step 1: Pull Roadmap Data

From connected sources:
1. **Jira/Linear** — Epics, milestones, their child issues and completion percentage
2. **Notion** (if connected) — Roadmap databases, initiative pages
3. **OKR data** — Cross-reference initiatives with their parent objectives

### Step 2: Calculate Status

For each initiative/epic:
- **Completion** = completed child issues / total child issues
- **Timeline** = compare current progress against planned end date
- **Status** = On Track / At Risk / Behind (based on progress vs. time elapsed)

### Step 3: Generate Roadmap View

```markdown
## Product Roadmap — {Quarter/Period}

### In Progress

| Initiative | Owner | Target | Progress | Status |
|-----------|-------|--------|----------|--------|
| {Epic A}  | {PM}  | Jun 30 | 75% (12/16 issues) | 🟢 On Track |
| {Epic B}  | {PM}  | May 15 | 40% (4/10 issues)  | 🔴 Behind |
| {Epic C}  | {PM}  | Jul 31 | 20% (3/15 issues)  | 🟢 On Track |

### Completed This Quarter
- {Epic D} — Shipped Apr 1
- {Epic E} — Shipped Mar 15

### Upcoming (Not Started)
- {Epic F} — Planned start: May 1
- {Epic G} — Planned start: Jun 1

### At-Risk Items
- **{Epic B}**: 40% complete with 3 weeks remaining. Blocked by {reason}.
  **Recommendation**: Reduce scope to core features only, defer {specific items} to next quarter.

### Dependencies
- {Epic C} depends on {Team X} delivering API by {date}
- {Epic F} requires design sign-off (currently in review)
```

### Stakeholder-Ready Summary

For leadership/board presentations, produce a simplified view:

```markdown
## Q2 Roadmap Summary

**On Track**: 3 of 5 initiatives (60%)
**Shipped**: 2 initiatives completed
**At Risk**: 1 initiative needs scope reduction

Key wins: {highlight}
Key risk: {highlight}
Next quarter preview: {highlight}
```

## Notes

- Roadmap views should adapt to the audience — engineers need ticket-level detail, execs need themes
- Always include dependencies — they're the most common source of roadmap risk
- When an initiative is behind, always recommend a specific action (scope cut, resource shift, timeline extension)
- Track quarter-over-quarter delivery rate for planning accuracy improvement
