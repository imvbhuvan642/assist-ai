---
name: standup-summary
description: "Generate team standup summaries by pulling updates from Slack, Jira/Linear, and GitHub. Use when a manager asks for a standup summary, team status update, or daily sync overview."
---

# Standup Summary

Synthesize a team standup from multiple data sources.

## When to Use

- Manager asks "what's the team status?" or "standup summary"
- Before a daily sync meeting
- Manager wants to catch up on team progress without reading every Slack message

## Workflow

### Step 1: Gather Data

Pull from available sources (use what's connected):

1. **Slack** (if MCP connected): Search the standup channel for today's messages
2. **Jira/Linear** (if MCP connected): Get tickets updated in the last 24 hours for the team
3. **GitHub** (if MCP connected): Get PRs opened, merged, or reviewed by team members

### Step 2: Synthesize

For each team member, compile:
- **Done**: What they completed since last standup
- **Doing**: What they're working on now
- **Blockers**: Anything blocking progress

### Step 3: Present

```markdown
## Team Standup — {date}

### {Team Member 1}
- **Done**: Merged PR #45 (auth refactor), closed PLAT-123
- **Doing**: Working on PLAT-130 (API rate limiting)
- **Blockers**: None

### {Team Member 2}
- **Done**: Completed design review for onboarding flow
- **Doing**: PLAT-128 (dashboard redesign)
- **Blockers**: Waiting on API spec from backend team

---

### Highlights
- 3 PRs merged, 2 new PRs opened
- Sprint is 65% complete (7/12 issues done)

### Blockers Needing Attention
- {Member 2} blocked on API spec — may need escalation
```

## Notes

- If Slack is not connected, rely on Jira/GitHub data and note that standup messages weren't included
- Keep summaries concise — managers want the signal, not the noise
- Highlight blockers prominently — that's the most actionable part
- If a team member has no updates in any source, note them as "No updates found"
