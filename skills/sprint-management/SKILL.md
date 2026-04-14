---
name: sprint-management
description: "Manage sprints, track tickets, and generate sprint reports. Use when the user asks about sprint status, ticket progress, backlog grooming, or sprint planning. Requires Jira or Linear MCP server."
---

# Sprint Management

Track sprint progress, manage tickets, and generate reports using Jira/Linear MCP tools.

## When to Use

- User asks "what's in the current sprint?" or "sprint status"
- User wants to create, update, or move tickets
- User asks about backlog or upcoming work
- User wants a sprint report or burndown summary
- User mentions specific ticket IDs (e.g., PLAT-123)

## When NOT to Use

- User is asking about code changes (use code-review skill)
- User wants calendar/meeting management (use calendar-management skill)

## Workflow

### Sprint Status Summary

1. Identify the project/board (check user's integrations config for default project key)
2. Get the active sprint
3. List all issues in the sprint with status
4. Generate summary:

```
## Sprint: {sprint_name} ({start_date} → {end_date})

**Progress**: {completed}/{total} issues ({percentage}%)

### By Status
| Status | Count | Issues |
|--------|-------|--------|
| Done       | 5 | PLAT-101, PLAT-103, ... |
| In Progress| 3 | PLAT-105, PLAT-107, ... |
| To Do      | 4 | PLAT-110, PLAT-112, ... |

### Blockers
- PLAT-107: Blocked by API dependency (assigned: @dev)

### At Risk
- PLAT-112: Not started, due in 2 days
```

### Ticket Operations

**View a ticket**: Fetch issue details — summary, description, status, assignee, priority, comments.

**Create a ticket**:
1. Ask for: summary, description, type (bug/task/story), priority, assignee (optional)
2. Create the issue in the active sprint or backlog
3. Return the ticket ID and link

**Update a ticket**:
1. Identify the ticket (by ID or search)
2. Update the requested fields (status, assignee, priority, description)
3. Confirm the change

**Move a ticket**: Change status (To Do → In Progress → In Review → Done)

### Sprint Report

Generate an end-of-sprint summary:

1. Fetch all issues from the sprint
2. Categorize: completed, carried over, added mid-sprint
3. Calculate velocity (story points completed)
4. Highlight blockers and delays
5. Format as a shareable report

```
## Sprint Report: {sprint_name}

**Velocity**: {points} story points
**Completion Rate**: {completed}/{total} ({percentage}%)

### Completed
- PLAT-101: Feature X (3 pts)
- PLAT-103: Bug fix Y (2 pts)

### Carried Over
- PLAT-112: Task Z — reason for carryover

### Key Metrics
- Avg cycle time: X days
- Blockers encountered: N
```

## Notes

- Always check the user's integrations config for their default Jira project key.
- When creating tickets, default to the user's project unless specified otherwise.
- Ticket creation and status changes don't require approval gates (they're reversible).
- For large sprints (>20 issues), summarize by epic or category rather than listing every ticket.
- Support both Jira (JQL queries) and Linear (GraphQL) based on which MCP is connected.
