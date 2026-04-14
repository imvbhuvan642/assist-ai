---
name: stakeholder-comms
description: "Draft stakeholder communications — status updates, project reports, and executive summaries adapted for different audiences. Use when the PM needs to communicate progress, decisions, or updates to leadership, engineering, customers, or cross-functional teams."
---

# Stakeholder Communications

Draft professional communications adapted for audience and context.

## When to Use

- PM needs to send a project status update to leadership
- PM wants to communicate a decision or change to the engineering team
- PM needs to draft a customer-facing announcement
- PM is preparing a weekly/monthly stakeholder update

## Workflow

### Step 1: Determine Audience and Purpose

| Audience | Tone | Focus | Detail Level |
|----------|------|-------|-------------|
| Executive / Board | Strategic | Outcomes, metrics, risks | High-level summary |
| Engineering | Technical | Specs, decisions, timeline | Detailed |
| Cross-functional | Collaborative | Dependencies, asks, timeline | Medium |
| Customers | Professional | Value, changes, actions | User-oriented |

### Step 2: Gather Data

Pull relevant context from:
- **Jira/Linear** — project progress, milestone completion
- **GitHub** — shipped changes, open work
- **OKR data** — goal progress
- **Calendar** — upcoming milestones, deadlines

### Step 3: Draft the Communication

**Executive Status Update**:

```markdown
Subject: {Project} Status Update — {Date}

## Summary
{One paragraph: where we are, key highlight, key risk}

## Progress
- {Milestone 1}: ✅ Complete
- {Milestone 2}: 🟡 In progress (70%)
- {Milestone 3}: 🔴 At risk — {brief reason}

## Key Metrics
| Metric | Target | Current |
|--------|--------|---------|
| {metric} | {target} | {current} |

## Decisions Needed
- {Decision 1}: {Context and options}

## Next Steps
1. {Action} — by {date}
2. {Action} — by {date}
```

**Engineering Update**:

```markdown
Subject: {Project} Engineering Update — {Date}

## What Shipped
- {Feature/change} (PR #{number})

## In Progress
- {Work item} — ETA: {date}, Owner: @{name}

## Decisions Made
- {Decision}: {Rationale}

## Open Questions
- {Question needing team input}

## Upcoming
- {Next sprint priorities}
```

**Customer Announcement**:

```markdown
Subject: {Product} Update — {What's new}

Hi {customer/team},

We're excited to share some updates to {product}:

**{Feature 1}**: {User-benefit description}
**{Feature 2}**: {User-benefit description}

{Any action needed from the customer}

These changes are live now. Let us know if you have any questions.

Best,
{Name}
```

## Notes

- All external communications (email to customers, Slack to stakeholders) require approval
- Adapt detail level strictly based on audience — exec summaries should be <1 page
- Lead with outcomes and impact, not activity
- Include "decisions needed" prominently — that's often why the update is being sent
- For recurring updates, maintain a consistent format so stakeholders know where to look
