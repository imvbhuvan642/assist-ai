---
name: cicd-monitoring
description: "Monitor CI/CD pipelines, check build status, and diagnose workflow failures. Use when the user asks about build status, pipeline failures, workflow runs, or deployment health. Requires GitHub MCP server."
requires_env:
  - GITHUB_TOKEN
---

# CI/CD Monitoring

Monitor GitHub Actions workflows, diagnose failures, and provide build status summaries.

## When to Use

- User asks "is the build passing?" or "what's the CI status?"
- User mentions a failing pipeline or broken build
- User asks about recent deployments or workflow runs
- User wants to check if a specific commit/PR passed CI

## When NOT to Use

- User wants to modify workflow YAML files (use direct tools)
- User is asking about CI concepts without a specific repo

## Workflow

### Check Build Status

1. Identify the repository (ask if not clear from context)
2. List recent workflow runs for the default branch (or specified branch)
3. Summarize status:

```
## CI/CD Status: {owner}/{repo}

**Branch**: {branch} | **Last run**: {timestamp}

| Workflow | Status | Duration | Trigger |
|----------|--------|----------|---------|
| Build    | ✅ Pass | 3m 42s  | push    |
| Tests    | ❌ Fail | 5m 10s  | push    |
| Deploy   | ⏸ Skip  | —       | —       |
```

### Diagnose Failure

When a workflow has failed:

1. Get the failed workflow run details
2. Identify which job(s) failed
3. Get the logs for the failed step(s)
4. Analyze the error and provide:
   - **Root cause**: What went wrong
   - **Failed step**: Which step in which job
   - **Error message**: The key error output
   - **Suggested fix**: What to do about it

### Monitor a PR's Checks

1. Get the PR's check suite / status checks
2. List all checks with their status (pass/fail/pending)
3. If any are failing, diagnose using the failure workflow above

### Proactive Alerts

When the user mentions they just pushed or merged:
- Offer to check the pipeline status after a brief moment
- If a failure is detected, proactively surface the diagnosis

## Output Format

Always include:
- Repository and branch context
- Timestamp of the run
- Clear pass/fail status with visual indicators
- For failures: the specific error and a suggested fix
- Link to the workflow run for manual inspection

## Notes

- GitHub Actions is the primary CI system supported via MCP.
- For other CI systems (Jenkins, CircleCI, GitLab CI), guide the user to check their dashboards and offer to help interpret error logs if pasted.
- Don't re-run workflows without explicit user approval.
- Large log outputs should be summarized — highlight the error, not the full log.
