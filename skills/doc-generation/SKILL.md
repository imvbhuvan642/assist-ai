---
name: doc-generation
description: "Generate technical documentation from code or PRs — README sections, API docs, architecture decision records, changelogs. Use when the user asks to document code, generate API docs, write an ADR, or create a changelog. Requires GitHub MCP server for PR/code access."
---

# Documentation Generation

Generate structured technical documentation from code, PRs, and project context.

## When to Use

- User asks to "document this" or "write docs for X"
- User wants a README section for a module or feature
- User asks for API documentation
- User wants an Architecture Decision Record (ADR)
- User asks for a changelog or migration guide

## When NOT to Use

- User wants a blog post or marketing content (not a technical documentation task)
- User wants meeting notes (not a documentation task)

## Workflow

### README Section

1. Identify the scope (module, feature, project)
2. Fetch relevant code via GitHub MCP (file contents, directory structure)
3. Generate structured README with:
   - **Overview**: What it does, why it exists
   - **Usage**: Code examples, CLI commands
   - **Configuration**: Required env vars, config options
   - **Architecture**: Key files, data flow (if applicable)

### API Documentation

1. Identify the API endpoints (from code or route definitions)
2. For each endpoint, document:
   - Method + path
   - Request parameters (path, query, body) with types
   - Response schema with examples
   - Authentication requirements
   - Error responses
3. Format as Markdown tables or OpenAPI-style blocks

### Architecture Decision Record (ADR)

Follow the standard ADR template:

```markdown
# ADR-{number}: {Title}

**Date**: {date}
**Status**: Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or harder as a result of this change?

### Positive
- ...

### Negative
- ...

### Neutral
- ...
```

Populate from:
- PR description and discussion
- Code changes (what was added/removed/modified)
- User's verbal context about the "why"

### Changelog / Release Notes (Internal)

1. Fetch merged PRs since the last tag/release
2. Categorize changes:
   - **Added**: New features
   - **Changed**: Modifications to existing features
   - **Fixed**: Bug fixes
   - **Removed**: Deprecated or removed features
   - **Security**: Security-related changes
3. Format following Keep a Changelog conventions

## Output Guidelines

- Use clear, imperative-mood headings ("Configure the database", not "Database configuration")
- Include code examples for any non-trivial usage
- Link to source files where relevant
- Keep it concise — docs should be scannable, not exhaustive
- Match the existing documentation style if the project already has docs

## Notes

- Always ask where the user wants the docs saved (file path or just displayed)
- For large codebases, ask the user to scope the documentation request to a specific module or feature
- When generating from PRs, use the PR description as primary context — the diff fills in technical details
- Do not fabricate API endpoints or configuration options — only document what exists in the code
