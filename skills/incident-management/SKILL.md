---
name: incident-management
description: "Handle production incidents — diagnose failures, coordinate response, draft incident reports, and create follow-up tickets. Use when the user reports a production issue, outage, or needs to coordinate incident response."
---

# Incident Management

Structured incident response workflow: diagnose, communicate, track, and follow up.

## When to Use

- User reports a production issue or outage
- User asks to create an incident report or post-mortem
- User needs to coordinate incident response (notify team, schedule war room)
- User mentions alerts, errors, or degraded service

## When NOT to Use

- User is asking about test failures (use cicd-monitoring skill)
- User wants to review code changes (use code-review skill)

## Workflow

### Step 1: Triage

Gather key information:
- **What's broken?** — Service, feature, or endpoint affected
- **Impact scope** — How many users/systems affected? Is it total outage or degraded?
- **When did it start?** — Timestamp or "since last deploy"
- **Severity** — P0 (full outage), P1 (major degradation), P2 (partial issue), P3 (minor)

If the user doesn't provide all of this, ask focused clarifying questions.

### Step 2: Diagnose

Use available tools to gather context:
1. **CI/CD status** — Check if a recent deployment coincides with the issue (GitHub Actions via MCP)
2. **Recent changes** — List recent merged PRs or commits to the affected service
3. **Error patterns** — If the user shares logs or error messages, analyze root cause
4. **Related issues** — Search for similar past incidents in the issue tracker (Jira/Linear)

### Step 3: Communicate

Draft incident communications using the appropriate channel:

**Internal notification** (Slack or email):
```
🚨 [P{severity}] {Service} — {Brief description}

Impact: {who/what is affected}
Status: Investigating / Identified / Mitigating / Resolved
Lead: {user's name}
War room: {meeting link if created}

Last update: {timestamp} — {current status}
```

**Stakeholder update** (for managers/executives):
- Impact in business terms (users affected, revenue impact)
- Current status and ETA to resolution
- What's being done

Use Gmail tools to send notifications, Calendar tools to schedule war rooms.

### Step 4: Track

Create a tracking ticket:
1. Create an incident issue in Jira/Linear with:
   - Title: `[P{severity}] {Service} — {Brief description}`
   - Description: timeline, impact, diagnosis so far
   - Priority: Maps from severity
   - Labels: `incident`, `p{severity}`
2. Link related PRs or issues if identified

### Step 5: Post-Mortem / Incident Report

After resolution, generate a structured post-mortem:

```markdown
## Incident Report: {Title}

**Date**: {date}
**Duration**: {start_time} → {resolution_time} ({total duration})
**Severity**: P{severity}
**Lead**: {name}

### Summary
One paragraph describing what happened and the impact.

### Timeline
| Time | Event |
|------|-------|
| HH:MM | Issue first reported / alert fired |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Service restored |

### Root Cause
What specifically caused the issue.

### Resolution
What was done to fix it.

### Impact
- Users affected: {number/scope}
- Duration: {time}
- Data loss: None / {description}

### Follow-up Actions
- [ ] {Action item 1} — Owner: @{name}, Due: {date}
- [ ] {Action item 2} — Owner: @{name}, Due: {date}

### Lessons Learned
- What went well
- What could be improved
```

Create follow-up tickets for each action item.

## Notes

- Speed matters during incidents. Keep responses concise and actionable.
- Always confirm before sending external communications (emails, Slack messages).
- The goal is to reduce time-to-resolution, not to produce perfect documentation during the incident — the post-mortem can be refined later.
- If the user is clearly stressed, match their urgency — skip pleasantries, focus on diagnosis and actions.
