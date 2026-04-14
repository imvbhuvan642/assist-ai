---
name: release-notes
description: "Generate release notes and changelogs from merged PRs and completed tickets. Use when preparing a product release, writing changelog entries, or communicating what shipped to users or stakeholders."
---

# Release Notes Generation

Auto-generate user-facing release notes and internal changelogs from development data.

## When to Use

- PM says "generate release notes" or "what shipped this release?"
- Preparing for a product release or deployment
- Writing a changelog for documentation
- Communicating shipped features to customers or stakeholders

## Workflow

### Step 1: Gather Shipped Changes

From connected sources (since last release/tag):
1. **GitHub** — Merged PRs, compare with previous release tag
2. **Jira/Linear** — Tickets marked as Done/Shipped in the release window

### Step 2: Categorize Changes

Group into standard categories:
- **New Features** — New capabilities for users
- **Improvements** — Enhancements to existing features
- **Bug Fixes** — Issues resolved
- **Performance** — Speed or reliability improvements
- **Security** — Security patches or improvements
- **Breaking Changes** — Changes that require user action

### Step 3: Generate Two Versions

**User-Facing Release Notes** (for customers):

```markdown
## What's New in v{version} — {date}

### New Features
- **{Feature name}**: {User-benefit description}. No jargon, focus on what the user can now do.

### Improvements
- **{Improvement}**: {How the user experience is better}

### Bug Fixes
- Fixed an issue where {user-visible problem description}
- Resolved {another user-visible issue}

### Coming Soon
- {Teaser for next release if appropriate}
```

**Internal Changelog** (for the engineering team):

```markdown
## Changelog v{version} — {date}

### Added
- {PR title} (#{pr_number}) — @{author}
- {PR title} (#{pr_number}) — @{author}

### Changed
- {PR title} (#{pr_number}) — @{author}

### Fixed
- {PR title} (#{pr_number}) — @{author}
  Fixes {TICKET-123}

### Security
- {PR title} (#{pr_number}) — @{author}

### Contributors
@{author1}, @{author2}, @{author3}
```

## Notes

- User-facing notes should never contain PR numbers, ticket IDs, or technical jargon
- Internal changelogs should link to PRs and tickets for traceability
- If a PR description is poor, infer the change from the diff or ask the PM for context
- Group related PRs into a single user-facing item (e.g., 5 PRs for one feature = 1 release note entry)
- Always distinguish between features that are fully shipped vs. behind a feature flag
