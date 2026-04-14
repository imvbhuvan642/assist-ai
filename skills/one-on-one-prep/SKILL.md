---
name: one-on-one-prep
description: "Prepare agendas for 1:1 meetings by pulling a team member's recent work, blockers, and activity. Use when a manager is preparing for a 1:1 or wants to review a team member's recent contributions."
---

# One-on-One Prep

Generate a data-informed 1:1 meeting agenda for managers.

## When to Use

- Manager says "prep my 1:1 with {name}" or "what has {name} been working on?"
- Before a scheduled 1:1 meeting
- Manager wants context on a team member's recent work

## Workflow

### Step 1: Identify the Team Member

Get the team member's name, and if available, their:
- GitHub username (for PR/commit data)
- Jira/Linear assignee ID (for ticket data)
- Slack handle (for communication patterns)
- Employee ID (for HRIS data)

### Step 2: Pull Recent Activity (last 2 weeks)

From each connected source:

1. **GitHub**: PRs authored, PRs reviewed, commits pushed
2. **Jira/Linear**: Tickets completed, in-progress, newly assigned
3. **Slack**: Key threads they participated in (if relevant)
4. **HRIS**: Upcoming leaves, any pending requests
5. **Calendar**: Upcoming shared meetings, last 1:1 notes

### Step 3: Generate Agenda

```markdown
## 1:1 Agenda: {Manager} ↔ {Team Member}
**Date**: {date} | **Last 1:1**: {previous date}

### Recent Work Summary
- Merged {N} PRs: {list key ones}
- Completed {N} tickets: {list key ones}
- Currently working on: {in-progress items}

### Wins to Acknowledge
- {Specific accomplishment worth recognizing}

### Potential Discussion Topics
- **Blockers**: {Any identified blockers from standup/Jira}
- **Workload**: {Are they overloaded or underutilized based on ticket count?}
- **Growth**: {Any recurring patterns — e.g., doing lots of reviews, taking on new tech}

### Suggested Questions
- How are you feeling about your current workload?
- Is there anything blocking you that I can help unblock?
- What would make your work more effective this sprint?
- Any skills you'd like to develop or projects you're interested in?

### Carry-Over Items
- {Action items from previous 1:1, if available}

### Notes
_{Space for the manager to take notes during the meeting}_
```

## Notes

- This is a prep tool, not a surveillance tool — frame everything positively
- Quantitative data (PR count, ticket velocity) is context, not judgment
- If no data is available from a source, skip that section rather than showing "No data"
- Always include suggested questions — even experienced managers appreciate prompts
- Keep the agenda under 1 page — it's a conversation guide, not a report
