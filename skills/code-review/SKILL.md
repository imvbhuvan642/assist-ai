---
name: code-review
description: "Review pull requests and code changes. Use when the user asks to review a PR, analyze code changes, check a diff, or provide feedback on a pull request. Requires GitHub MCP server."
requires_env:
  - GITHUB_TOKEN
---

# Code Review

Structured code review workflow using GitHub MCP tools to fetch PR data and provide actionable feedback.

## When to Use

- User asks to review a PR (by number, URL, or description)
- User asks to check recent changes on a branch
- User asks for feedback on a diff or code changes
- User mentions a PR and wants a summary

## When NOT to Use

- User wants to write code from scratch (use direct tools)
- User is asking about code concepts without a specific PR

## Workflow

### Step 1: Identify the PR

If the user provides:
- **PR number**: Use it directly with the repo context
- **PR URL**: Extract owner/repo and PR number
- **Branch name**: Search for open PRs on that branch
- **"latest PR"**: List recent PRs and pick the most recent

Ask for the repository (owner/repo) if not obvious from context or user integrations config.

### Step 2: Fetch PR Details

1. Get PR metadata: title, description, author, base/head branches, status
2. Get the diff / changed files list
3. Get any existing review comments

### Step 3: Analyze the Changes

Review each changed file and categorize findings into:

| Category | What to Look For |
|----------|-----------------|
| **Bugs** | Logic errors, off-by-one, null/undefined access, race conditions, missing error handling |
| **Security** | Injection vulnerabilities, hardcoded secrets, missing auth checks, unsafe deserialization |
| **Performance** | N+1 queries, unnecessary allocations, missing indexes, unbounded loops |
| **Style** | Naming conventions, code duplication, dead code, inconsistent patterns |
| **Architecture** | Separation of concerns, coupling, missing abstractions, breaking changes |
| **Tests** | Missing test coverage, untested edge cases, brittle test assumptions |

### Step 4: Present the Review

Structure the output as:

```
## PR Review: #{number} — {title}

**Author**: {author} | **Branch**: {head} → {base} | **Files changed**: {count}

### Summary
One paragraph summarizing what the PR does and the overall quality.

### Findings

#### 🔴 Critical (must fix)
- [file.py:42] Description of the issue

#### 🟡 Suggestions (should consider)
- [file.py:15] Description of the suggestion

#### 🟢 Nitpicks (optional)
- [file.py:8] Minor style note

### Verdict
APPROVE / REQUEST_CHANGES / COMMENT — with reasoning.
```

### Step 5: Post Review (Optional)

If the user asks to post the review:
1. Confirm the action (this posts to GitHub)
2. Post a review with the findings as inline comments
3. Set the review status (APPROVE / REQUEST_CHANGES / COMMENT)

## Notes

- Always read the PR description before reviewing — it provides context for intentional changes.
- If the diff is very large (>20 files), summarize by file group and ask the user which areas to deep-dive into.
- Do not post reviews without explicit user confirmation.
- When reviewing, consider the project's existing patterns (check other files in the same directory for conventions).
