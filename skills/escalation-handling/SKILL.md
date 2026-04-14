---
name: escalation-handling
description: "Handle escalations — draft stakeholder communications, create tracking tickets, and schedule emergency meetings. Use when a blocker, incident, or urgent issue needs to be escalated to leadership or cross-team coordination."
---

# Escalation Handling

Structured escalation workflow for blockers, incidents, and urgent cross-team issues.

## When to Use

- A blocker needs management attention
- An issue needs to be escalated to leadership
- Cross-team coordination is needed urgently
- A dependency is at risk and stakeholders need to be notified

## Workflow

### Step 1: Define the Escalation

Gather:
- **What**: The issue or blocker being escalated
- **Impact**: What's affected and the severity (timeline, revenue, users)
- **Who**: Which teams or stakeholders need to be involved
- **Ask**: What specific help or decision is needed
- **Urgency**: How soon does this need resolution

### Step 2: Draft Communication

**Email to stakeholders** (via Gmail):

```
Subject: [Escalation] {Brief title} — Action Needed by {date}

Hi {stakeholder},

I'm escalating {issue} as it's blocking {impact description}.

**Current Status**: {what's been tried, where things stand}
**Impact**: {specific consequences if not resolved}
**Ask**: {what you need from them — a decision, resource, unblock}
**Deadline**: {when this needs to be resolved}

Happy to set up a call to discuss. Let me know your availability.

Best,
{User's name}
```

Adapt tone based on audience:
- **To leadership**: Focus on business impact and decision needed
- **To peer teams**: Focus on the technical dependency and timeline
- **To external parties**: Formal, with clear next steps

### Step 3: Create Tracking Ticket

Create a Jira/Linear issue:
- Title: `[Escalation] {Brief title}`
- Priority: High or Critical
- Description: Full context, impact, ask, and stakeholders involved
- Labels: `escalation`, `blocker`

### Step 4: Schedule Meeting (if needed)

For urgent escalations:
1. Create a calendar event: "Escalation: {title}"
2. Add all relevant stakeholders
3. Include Google Meet link
4. Duration: 30 min (keep escalation meetings tight)
5. Add context in the meeting description

### Step 5: Follow Up

After the escalation meeting or response:
- Update the tracking ticket with the decision/outcome
- Notify the original team of the resolution
- If unresolved, schedule a follow-up

## Notes

- All escalation emails require approval before sending
- Be factual, not emotional — escalations should convey urgency through impact data, not language
- Always include a specific "ask" — vague escalations waste time
- Track resolution time for process improvement
