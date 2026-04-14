---
name: performance-review
description: "Manage performance review cycles — schedule reviews, draft review templates, track completion, and pull work data for evidence-based reviews. Use when HR or managers are preparing for performance reviews."
---

# Performance Review

Support the performance review cycle from scheduling through completion.

## When to Use

- User is preparing for performance reviews
- User asks to schedule review meetings
- User needs a review template or self-assessment form
- User wants to pull work data for evidence-based reviews
- Manager asks to track review completion status

## Workflow

### Schedule Review Meetings

1. Get the list of employees to review (from HRIS or user input)
2. For each employee, schedule a review meeting:
   - Duration: 45-60 minutes
   - Participants: employee + manager (+ HR if requested)
   - Title: "Performance Review — {Employee Name}"
3. Use Calendar tools to create events

### Generate Review Template

Create a structured review form:

```markdown
## Performance Review: {Employee Name}
**Period**: {start_date} to {end_date}
**Reviewer**: {manager_name}
**Date**: {review_date}

### Goals & Achievements
| Goal | Status | Evidence |
|------|--------|----------|
| {Goal 1 from OKRs} | Met / Partially Met / Not Met | {data} |

### Core Competencies (1-5 scale)
- **Technical Skills**: _/5 — {comments}
- **Communication**: _/5 — {comments}
- **Collaboration**: _/5 — {comments}
- **Initiative**: _/5 — {comments}
- **Reliability**: _/5 — {comments}

### Strengths
-

### Areas for Improvement
-

### Goals for Next Period
1.
2.
3.

### Overall Rating
Outstanding / Exceeds Expectations / Meets Expectations / Needs Improvement / Unsatisfactory

### Comments
{Free-form manager comments}
```

### Pull Work Evidence

If GitHub/Jira MCP tools are available, gather evidence:
- **Commits/PRs**: Number of PRs merged, code review participation
- **Tickets**: Tickets completed, story points delivered
- **Patterns**: Consistency, quality, collaboration signals

Present this as supporting data, not as the review itself.

### Track Review Completion

For HR tracking an ongoing review cycle:
1. List all employees due for review
2. Track which reviews are scheduled, completed, or pending
3. Send reminder emails for overdue reviews

```markdown
## Review Cycle Status: {Period}

| Employee | Manager | Status | Scheduled | Completed |
|----------|---------|--------|-----------|-----------|
| {Name}   | {Mgr}   | Done   | Apr 10    | Apr 10    |
| {Name}   | {Mgr}   | Scheduled | Apr 15 | —        |
| {Name}   | {Mgr}   | Pending   | —      | —        |
```

## Notes

- Performance reviews contain sensitive information — never share one employee's review data with another employee
- Review templates should be customized for the role (engineering reviews may emphasize code quality; PM reviews emphasize product outcomes)
- When pulling work evidence, present raw data objectively — don't make performance judgments based on metrics alone
- Reminder emails for overdue reviews require approval before sending
