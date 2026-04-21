# Assist AI — Digital Employee Assistant Extension Plan

> Turning Assist AI from a single-user terminal assistant into a role-aware, self-service digital employee platform for Developers, HRs, Managers, and Project Managers.

## Implementation Status

| Phase | Status | Summary |
|-------|--------|---------|
| **Phase 0** — Foundation | **Done** | PersonaConfig, 4 persona overlays, agent.py injection, persona-aware routing in agent.md |
| **Phase 0.5** — Self-Service | **Done** | UsersConfig, user profile templates, `tools/user_config.py` (7 tools), preferences + onboarding skills, user-scoped memory, `--user` CLI flag |
| **Phase 1** — Developer | **Done** | GitHub + Jira MCP configs, 5 skills (code-review, cicd-monitoring, sprint-management, doc-generation, incident-management), developer-assistant subagent |
| **Phase 2** — HR | **Done** | RAGConfig + HRISConfig, `tools/rag.py` + `tools/hris.py` (with mock provider), 5 skills (leave-management, policy-qa, employee-onboarding, performance-review, recruitment), hr-assistant subagent |
| **Phase 3** — Manager | **Done** | 5 skills (standup-summary, one-on-one-prep, okr-tracking, resource-allocation, escalation-handling), manager-assistant subagent, Slack + Notion MCP configs |
| **Phase 4** — PM | **Done** | 6 skills (feature-tracking, feedback-analysis, roadmap-management, competitive-analysis, release-notes, stakeholder-comms), pm-assistant subagent |
| **Phase 5** — Enterprise | Planned | Audit logging, auth, PII redaction, admin guardrails |

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Architecture Overview](#architecture-overview)
3. [Phase 0 — Foundation: Persona System](#phase-0--foundation-persona-system)
4. [Phase 0.5 — Employee Self-Service & Customization](#phase-05--employee-self-service--customization)
5. [Phase 1 — Developer Persona](#phase-1--developer-persona)
6. [Phase 2 — HR Persona](#phase-2--hr-persona)
7. [Phase 3 — Manager Persona](#phase-3--manager-persona)
8. [Phase 4 — Project Manager Persona](#phase-4--project-manager-persona)
9. [Phase 5 — Enterprise Hardening](#phase-5--enterprise-hardening)
10. [File Manifest](#file-manifest)
11. [External Dependencies](#external-dependencies)
12. [Dependency Graph](#dependency-graph)

---

## Design Principles

1. **Leverage existing patterns** — new capabilities are added as skills (`SKILL.md`), tools (`tools/*.py`), subagents (`agents/*/agent.yaml`), or MCP servers (`config.yaml`). No core architecture rewrites.
2. **Employee-first customization** — each user can enable/disable skills, set their own approval gates, create personal skills, and configure integrations. The admin sets boundaries; the employee owns their setup.
3. **Incremental rollout** — every phase delivers standalone value. Phases 1 and 2 can be developed in parallel.
4. **Config-driven** — all integrations are togglable via `config.yaml`. Missing API keys or packages degrade gracefully (log warning, skip).
5. **Role-based routing** — the agent adapts personality, skill priorities, and tool access based on the active persona.

---

## Architecture Overview

### Current Extension Points

| Extension Point | Location | How it works |
|----------------|----------|--------------|
| **Skills** | `skills/<name>/SKILL.md` | Auto-discovered Markdown workflows. No Python code needed. Active on next message. |
| **Tools** | `tools/<name>.py` | Python files with `@tool` decorators. Loaded gracefully in `src/load_tools.py`. |
| **Subagents** | `agents/<name>/agent.yaml` + optional `SKILL.md` | Auto-discovered by `src/load_agents.py`. Inherit or filter tools. |
| **MCP Servers** | `config.yaml` → `mcp.servers` | External tool servers (stdio/SSE). Auto-connected at startup. |
| **Dynamic Prompt** | `@dynamic_prompt` middleware in `src/agent.py` | Re-evaluated on every invocation. Injects fresh user context. |
| **Config** | `config.yaml` + Pydantic models in `src/load_config.py` | Env var expansion, local overrides, type validation. |

### Post-Extension Architecture

```
config.yaml
├── persona.active: developer|hr|manager|project_manager
├── users.dir: ./workspace/users
├── rag: { enabled, documents_dir, vector_store, embedding_model }
├── hris: { enabled, provider, base_url, api_key }
├── privacy: { redact_pii, allowed_domains, audit_tool_calls }
└── mcp.servers: { github, jira, slack, notion, ... }

workspace/users/{user_id}/
├── profile.yaml              # role, timezone, communication style
├── enabled_skills.yaml       # which skills are active
├── enabled_tools.yaml        # which tools are allowed
├── interrupt_on.yaml         # per-user approval gates
├── integrations.yaml         # per-user service config (Jira project, Slack channel)
└── memories/                 # isolated persistent memory
    └── preferences.txt

prompts/personas/
├── developer.md
├── hr.md
├── manager.md
└── project_manager.md
```

---

## Phase 0 — Foundation: Persona System

**Goal**: The agent adapts personality, tone, and skill routing based on the user's role. No new tools or dependencies — pure config + prompt engineering.

### 0A. Extend `config.yaml`

Add a `persona` top-level section:

```yaml
persona:
  active: "developer"  # developer | hr | manager | project_manager
```

### 0B. Add `PersonaConfig` to `src/load_config.py`

```python
class PersonaConfig(BaseModel):
    active: Literal["developer", "hr", "manager", "project_manager"] = "developer"
```

Add `persona: PersonaConfig = PersonaConfig()` to `AppConfig`.

### 0C. Create Persona Prompt Overlays

Four files in `prompts/personas/`:

| File | Persona | Key Focus |
|------|---------|-----------|
| `developer.md` | Developer | Code-first, technical depth, debugging mindset |
| `hr.md` | HR | Compliance-aware, empathetic, employee-first |
| `manager.md` | Manager | Strategic/operational, team-first, data-driven |
| `project_manager.md` | Project Manager | User-centric, prioritization frameworks, stakeholder management |

Each overlay is appended to the base `identity.md` + `agent.md`, not a replacement.

### 0D. Inject Persona Overlay in Agent Assembly

Modify `_build_static_system_prompt()` in `src/agent.py` to load `prompts/personas/{config.persona.active}.md` after `identity.md` + `agent.md`.

### 0E. Update `memories/agent.md`

Add a "Persona-Aware Routing" section mapping persona → primary skill categories.

### Files Changed

| File | Action |
|------|--------|
| `config.yaml` | Add `persona` section |
| `src/load_config.py` | Add `PersonaConfig` model + wire into `AppConfig` |
| `src/agent.py` | Load persona overlay in `_build_static_system_prompt()` |
| `memories/agent.md` | Add persona routing rules |
| `prompts/personas/developer.md` | **New** |
| `prompts/personas/hr.md` | **New** |
| `prompts/personas/manager.md` | **New** |
| `prompts/personas/project_manager.md` | **New** |

---

## Phase 0.5 — Employee Self-Service & Customization

**Goal**: Each employee owns their setup — enable/disable skills, set approval gates, create personal skills, configure integrations. The admin sets boundaries; the user customizes within them.

### 0.5A. User Profile Directory Structure

Each employee gets an isolated profile under `workspace/users/{user_id}/`:

```
workspace/users/{user_id}/
├── profile.yaml              # structured preferences
├── enabled_skills.yaml       # skill whitelist (empty = all enabled)
├── enabled_tools.yaml        # tool whitelist (empty = all enabled)
├── interrupt_on.yaml         # per-user approval gates
├── integrations.yaml         # per-user service config
└── memories/                 # user-scoped persistent memory
    └── preferences.txt       # free-form learned preferences
```

#### `profile.yaml` schema:

```yaml
name: "Vaishak Bhuvan"
persona: "developer"
timezone: "Asia/Kolkata"
communication_style: "direct"
output_format: "structured"
```

#### `enabled_skills.yaml` schema:

```yaml
# Empty list = all global skills enabled. Explicit list = only these.
enabled:
  - web-search
  - email-management
  - calendar-management
  - code-review
  - sprint-management
```

#### `interrupt_on.yaml` schema:

```yaml
# Per-user approval overrides. Falls back to global config.yaml if absent.
- send_gmail_message
- create_calendar_event
```

### 0.5B. Config Extension

Add to `config.yaml`:

```yaml
users:
  dir: "./workspace/users"
  default_persona: "developer"
```

Add `UsersConfig` Pydantic model to `src/load_config.py`:

```python
class UsersConfig(BaseModel):
    dir: str = "./workspace/users"
    default_persona: Literal["developer", "hr", "manager", "project_manager"] = "developer"
```

### 0.5C. User Config Management Tool

New file `tools/user_config.py` with tools:

- `get_user_profile()` — read the active user's profile.yaml
- `update_user_profile(key, value)` — update a specific profile field
- `list_available_skills()` — list all global skills with descriptions
- `enable_skill(skill_name)` — add to user's enabled_skills.yaml
- `disable_skill(skill_name)` — remove from user's enabled_skills.yaml
- `list_enabled_skills()` — show what's currently enabled
- `update_interrupt_on(tool_name, enabled)` — add/remove approval gates

### 0.5D. Preferences Management Skill

New file `skills/preferences/SKILL.md`:

Handles conversational preference management:
- "Disable the content-writer skill"
- "I want approval before any calendar event is created"
- "My Jira project key is PLAT"
- "Show me my current configuration"
- "Switch me to the PM persona"

### 0.5E. Onboarding Skill

New file `skills/onboarding/SKILL.md`:

Triggered when a new user starts (no profile directory exists):
1. Ask role (Developer / HR / Manager / PM)
2. Ask about integrations (Gmail, Jira, GitHub, Slack)
3. Ask preferences (communication style, timezone, approval sensitivity)
4. Generate profile directory with role-appropriate defaults
5. Show summary of configuration

### 0.5F. User-Scoped Memory

Update `src/memory.py` `create_backend()` to accept `user_id` and scope `/memories/` to user directory:

```python
routes={
    "/memories/": FilesystemBackend(root_dir=f"./workspace/users/{user_id}/memories"),
    "/skills/": FilesystemBackend(root_dir="./skills"),
}
```

### 0.5G. Filtered Skill & Tool Injection

Update `@dynamic_prompt` middleware in `src/agent.py` to:
1. Load `workspace/users/{user_id}/enabled_skills.yaml`
2. Filter the global skill list to only enabled skills
3. Inject filtered list into system prompt
4. Load `workspace/users/{user_id}/interrupt_on.yaml` for per-user approval gates

### 0.5H. CLI Updates

Update `main.py`:
- Add `--user <id>` argument
- Detect missing profile directory → trigger onboarding
- Pass `user_id` to `create_agent()` for scoped memory/preferences

### Files Changed

| File | Action |
|------|--------|
| `config.yaml` | Add `users` section |
| `src/load_config.py` | Add `UsersConfig` model + wire into `AppConfig` |
| `src/agent.py` | Accept `user_id`, filter skills/tools in dynamic prompt, pass to memory |
| `src/memory.py` | Accept `user_id` for scoped backend routes |
| `src/load_tools.py` | Add user_config tools loading block |
| `main.py` | Add `--user` argument, onboarding detection |
| `tools/user_config.py` | **New** — preference CRUD tools |
| `skills/preferences/SKILL.md` | **New** — conversational config management |
| `skills/onboarding/SKILL.md` | **New** — first-run setup wizard |

---

## Phase 1 — Developer Persona

**Goal**: Code review, PR management, CI/CD monitoring, ticket management, documentation generation, incident handling.

### MCP Servers

| Server | Transport | Package | Env Vars |
|--------|-----------|---------|----------|
| GitHub | stdio | `@modelcontextprotocol/server-github` | `GITHUB_TOKEN` |
| Jira/Linear | stdio | `@modelcontextprotocol/server-atlassian` or Linear MCP | `JIRA_HOST`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |

### New Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Code Review | `skills/code-review/` | Fetch PR diff via GitHub MCP, analyze for bugs/style/security/performance, post review comments |
| CI/CD Monitoring | `skills/cicd-monitoring/` | List workflow runs, summarize failures, proactive build failure alerts |
| Sprint Management | `skills/sprint-management/` | List sprint tickets, summarize status, create/update tickets, generate sprint reports |
| Doc Generation | `skills/doc-generation/` | Generate README sections, API docs, ADRs from code or PRs |
| Incident Management | `skills/incident-management/` | Check CI/CD + error issues, draft incident reports, create follow-up tickets, send notification emails |

### New Subagent

```yaml
# agents/developer-assistant/agent.yaml
name: developer-assistant
description: "Specialist for code review, CI/CD, sprint management, and developer workflows"
system_prompt: "You are the developer-assistant agent..."
```

### Approval Gates

Add to `interrupt_on`: `create_pull_request`, `merge_pull_request`, `create_issue`

### Files Changed

| File | Action |
|------|--------|
| `config.yaml` | Add GitHub + Jira MCP server entries |
| `skills/code-review/SKILL.md` | **New** |
| `skills/cicd-monitoring/SKILL.md` | **New** |
| `skills/sprint-management/SKILL.md` | **New** |
| `skills/doc-generation/SKILL.md` | **New** |
| `skills/incident-management/SKILL.md` | **New** |
| `agents/developer-assistant/agent.yaml` | **New** |
| `agents/developer-assistant/SKILL.md` | **New** |

---

## Phase 2 — HR Persona

**Goal**: Leave management, policy Q&A (RAG), onboarding, performance tracking, recruitment.

### New Tools

| Tool | File | Description |
|------|------|-------------|
| `search_company_docs` | `tools/rag.py` | Semantic search over company documents using ChromaDB + embeddings |
| `get_leave_balance`, `apply_leave`, `get_employee_info`, `list_team_leaves` | `tools/hris.py` | HRIS integration (BambooHR / Keka / Darwinbox) |

### Config Additions

```yaml
rag:
  enabled: true
  documents_dir: "./data/policies"
  vector_store: "chroma"           # chroma | faiss
  embedding_model: "text-embedding-3-small"

hris:
  enabled: true
  provider: "bamboohr"             # bamboohr | keka | darwinbox | mock
  base_url: "${HRIS_BASE_URL}"
  api_key: "${HRIS_API_KEY}"
```

### New Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Leave Management | `skills/leave-management/` | Check balance, apply leave (with approval), team calendar conflicts |
| Policy Q&A | `skills/policy-qa/` | RAG search over company docs, synthesize answer, cite source |
| Employee Onboarding | `skills/employee-onboarding/` | Checklist creation, welcome emails (Gmail), orientation scheduling (Calendar) |
| Performance Review | `skills/performance-review/` | Schedule reviews, pull work data, draft review templates |
| Recruitment | `skills/recruitment/` | Search candidate emails, schedule interviews, pipeline tracking |

### New Subagent

```yaml
# agents/hr-assistant/agent.yaml
name: hr-assistant
description: "Specialist for HR workflows — leave, policy, onboarding, performance, recruitment"
system_prompt: "You are the hr-assistant agent..."
```

### Approval Gates

Add: `apply_leave`

### Dependencies

Add to `requirements.txt`: `chromadb`, `langchain-chroma`

### Files Changed

| File | Action |
|------|--------|
| `config.yaml` | Add `rag` + `hris` sections |
| `src/load_config.py` | Add `RAGConfig`, `HRISConfig` models |
| `src/load_tools.py` | Add RAG + HRIS tool loading blocks |
| `requirements.txt` | Add `chromadb`, `langchain-chroma` |
| `tools/rag.py` | **New** |
| `tools/hris.py` | **New** |
| `skills/leave-management/SKILL.md` | **New** |
| `skills/policy-qa/SKILL.md` | **New** |
| `skills/employee-onboarding/SKILL.md` | **New** |
| `skills/performance-review/SKILL.md` | **New** |
| `skills/recruitment/SKILL.md` | **New** |
| `agents/hr-assistant/agent.yaml` | **New** |
| `agents/hr-assistant/SKILL.md` | **New** |

---

## Phase 3 — Manager Persona

**Goal**: Team dashboards, standup summaries, 1:1 prep, OKR tracking, resource allocation, escalation handling.

### MCP Servers

| Server | Transport | Package | Env Vars |
|--------|-----------|---------|----------|
| Slack | stdio | `@anthropic/mcp-server-slack` | `SLACK_BOT_TOKEN` |
| Notion | stdio | `@notionhq/mcp-server-notion` | `NOTION_API_KEY` |

### New Skills

| Skill | Directory | Description |
|-------|-----------|-------------|
| Standup Summary | `skills/standup-summary/` | Pull Slack standup messages + Jira updates, synthesize team summary |
| 1:1 Prep | `skills/one-on-one-prep/` | Pull team member's commits, tickets, Slack activity → generate agenda |
| OKR Tracking | `skills/okr-tracking/` | Query OKR data (SQL/Notion), generate progress reports |
| Resource Allocation | `skills/resource-allocation/` | Team capacity from HRIS + sprint load → recommendations |
| Escalation Handling | `skills/escalation-handling/` | Draft comms, create tracking ticket, schedule emergency meeting |

### New Subagent

```yaml
# agents/manager-assistant/agent.yaml
name: manager-assistant
description: "Specialist for team management — standups, 1:1s, OKRs, resource planning, escalations"
system_prompt: "You are the manager-assistant agent..."
```

### Files Changed

| File | Action |
|------|--------|
| `config.yaml` | Add Slack + Notion MCP server entries |
| `skills/standup-summary/SKILL.md` | **New** |
| `skills/one-on-one-prep/SKILL.md` | **New** |
| `skills/okr-tracking/SKILL.md` | **New** |
| `skills/resource-allocation/SKILL.md` | **New** |
| `skills/escalation-handling/SKILL.md` | **New** |
| `agents/manager-assistant/agent.yaml` | **New** |
| `agents/manager-assistant/SKILL.md` | **New** |

---

## Phase 4 — Project Manager Persona

**Goal**: Feature tracking, feedback analysis, roadmap management, competitive analysis, release notes, stakeholder communications.

### New Skills (no new infra — reuses Phase 1 + 3 MCP servers)

| Skill | Directory | Description |
|-------|-----------|-------------|
| Feature Tracking | `skills/feature-tracking/` | Aggregate feature requests from Jira/Linear, prioritize via RICE/ICE |
| Feedback Analysis | `skills/feedback-analysis/` | Search Slack + Gmail + DB for feedback, sentiment analysis, theme clustering |
| Roadmap Management | `skills/roadmap-management/` | Pull epics/milestones, cross-ref OKRs, identify at-risk items |
| Competitive Analysis | `skills/competitive-analysis/` | Web search for competitor intel, generate structured briefs |
| Release Notes | `skills/release-notes/` | Pull merged PRs + completed tickets, generate user-facing changelog |
| Stakeholder Comms | `skills/stakeholder-comms/` | Draft status updates adapted for audience (exec vs. engineering) |

### New Subagent

```yaml
# agents/pm-assistant/agent.yaml
name: pm-assistant
description: "Specialist for product management — feature tracking, feedback, roadmap, releases, stakeholder comms"
system_prompt: "You are the pm-assistant agent..."
```

### Files Changed

| File | Action |
|------|--------|
| `skills/feature-tracking/SKILL.md` | **New** |
| `skills/feedback-analysis/SKILL.md` | **New** |
| `skills/roadmap-management/SKILL.md` | **New** |
| `skills/competitive-analysis/SKILL.md` | **New** |
| `skills/release-notes/SKILL.md` | **New** |
| `skills/stakeholder-comms/SKILL.md` | **New** |
| `agents/pm-assistant/agent.yaml` | **New** |
| `agents/pm-assistant/SKILL.md` | **New** |

---

## Phase 5 — Enterprise Hardening

**Goal**: Audit logging, multi-user auth, data privacy, secrets management.

### 5A. Audit Logging

New file `src/audit.py` — middleware that logs every tool call:
- Timestamp, user ID, persona, tool name, arguments (PII-redacted), result status
- Output: `logs/audit/YYYY-MM-DD.jsonl` (structured JSON Lines)

Wire into `src/agent.py` middleware list.

### 5B. Auth & User Management

Add to `config.yaml`:

```yaml
auth:
  enabled: false
  provider: "local"              # local | oauth2 | saml
  users_file: "./data/users.yaml"
```

`data/users.yaml` maps user IDs to personas and tool permissions:

```yaml
users:
  - id: vaishak
    persona: developer
    permissions: [github, jira, gmail, calendar]
  - id: priya
    persona: hr
    permissions: [hris, gmail, calendar, rag]
```

### 5C. Data Privacy

Add to `config.yaml`:

```yaml
privacy:
  redact_pii: true
  allowed_domains: ["company.com"]
  audit_tool_calls: true
```

New file `src/privacy.py` — PII detection and redaction utilities.

### 5D. Admin Guardrails

Admins can:
- Lock certain skills as mandatory (can't be disabled by users)
- Restrict tool access by role
- Require approval for custom skill sharing (user → global)
- Set organization-wide interrupt_on defaults

### Files Changed

| File | Action |
|------|--------|
| `config.yaml` | Add `auth`, `privacy` sections |
| `src/load_config.py` | Add `AuthConfig`, `PrivacyConfig` models |
| `src/agent.py` | Wire audit middleware |
| `main.py` | Auth check on startup |
| `src/audit.py` | **New** — audit logging middleware |
| `src/privacy.py` | **New** — PII redaction utilities |
| `data/users.yaml` | **New** — user-permission mapping |

---

## File Manifest

### Summary

| Category | Count |
|----------|-------|
| Persona overlays | 4 |
| New skills | 23 (21 persona + preferences + onboarding) |
| New subagents | 4 |
| New tool files | 3 (`user_config.py`, `rag.py`, `hris.py`) |
| MCP servers | 4 (GitHub, Jira/Linear, Slack, Notion) |
| Core files modified | 6 (`config.yaml`, `load_config.py`, `agent.py`, `memory.py`, `load_tools.py`, `main.py`) |
| Enterprise modules | 3 (`audit.py`, `privacy.py`, `users.yaml`) |
| Documentation | 1 (this file) |

**Total: ~44 new files, 7 modified files, 0 core rewrites.**

### All New Files

```
docs/EXTENSION_PLAN.md                      # This document
prompts/personas/developer.md               # Phase 0
prompts/personas/hr.md                      # Phase 0
prompts/personas/manager.md                 # Phase 0
prompts/personas/project_manager.md         # Phase 0
tools/user_config.py                        # Phase 0.5
skills/preferences/SKILL.md                 # Phase 0.5
skills/onboarding/SKILL.md                  # Phase 0.5
skills/code-review/SKILL.md                 # Phase 1
skills/cicd-monitoring/SKILL.md             # Phase 1
skills/sprint-management/SKILL.md           # Phase 1
skills/doc-generation/SKILL.md              # Phase 1
skills/incident-management/SKILL.md         # Phase 1
agents/developer-assistant/agent.yaml       # Phase 1
agents/developer-assistant/SKILL.md         # Phase 1
tools/rag.py                                # Phase 2
tools/hris.py                               # Phase 2
skills/leave-management/SKILL.md            # Phase 2
skills/policy-qa/SKILL.md                   # Phase 2
skills/employee-onboarding/SKILL.md         # Phase 2
skills/performance-review/SKILL.md          # Phase 2
skills/recruitment/SKILL.md                 # Phase 2
agents/hr-assistant/agent.yaml              # Phase 2
agents/hr-assistant/SKILL.md                # Phase 2
skills/standup-summary/SKILL.md             # Phase 3
skills/one-on-one-prep/SKILL.md             # Phase 3
skills/okr-tracking/SKILL.md                # Phase 3
skills/resource-allocation/SKILL.md         # Phase 3
skills/escalation-handling/SKILL.md         # Phase 3
agents/manager-assistant/agent.yaml         # Phase 3
agents/manager-assistant/SKILL.md           # Phase 3
skills/feature-tracking/SKILL.md            # Phase 4
skills/feedback-analysis/SKILL.md           # Phase 4
skills/roadmap-management/SKILL.md          # Phase 4
skills/competitive-analysis/SKILL.md        # Phase 4
skills/release-notes/SKILL.md              # Phase 4
skills/stakeholder-comms/SKILL.md           # Phase 4
agents/pm-assistant/agent.yaml              # Phase 4
agents/pm-assistant/SKILL.md                # Phase 4
src/audit.py                                # Phase 5
src/privacy.py                              # Phase 5
data/users.yaml                             # Phase 5
```

---

## External Dependencies

### Service Dependencies by Persona

| Persona | Required Services | Auth Method |
|---------|-------------------|-------------|
| All | Google (Gmail + Calendar via OAuth), Tavily (API key) | Existing |
| Developer | GitHub (PAT), Jira/Linear (API token) | Env vars |
| HR | HRIS API (API key), ChromaDB (local, no auth) | Env vars |
| Manager | Slack (Bot token), Notion (API key) + all Developer services | Env vars |
| PM | All of the above | Env vars |

### Python Packages

| Package | Phase | Purpose |
|---------|-------|---------|
| `chromadb` | 2 | Local vector store for RAG |
| `langchain-chroma` | 2 | LangChain ChromaDB integration |

### MCP Server Packages (via npx)

| Package | Phase |
|---------|-------|
| `@modelcontextprotocol/server-github` | 1 |
| `@modelcontextprotocol/server-atlassian` | 1 |
| `@anthropic/mcp-server-slack` | 3 |
| `@notionhq/mcp-server-notion` | 3 |

---

## Dependency Graph

```
Phase 0 (Foundation)         <- no external deps, pure config + prompts
    |
Phase 0.5 (Self-Service)    <- no external deps, user profile system
    |
    +-- Phase 1 (Developer)  <- GitHub + Jira tokens
    |
    +-- Phase 2 (HR)         <- HRIS API + ChromaDB (parallel with Phase 1)
    |
Phase 3 (Manager)            <- Slack + Notion tokens, reuses Phase 1 MCPs
    |
Phase 4 (PM)                 <- no new infra, reuses Phase 1 + 3 MCPs
    |
Phase 5 (Enterprise)         <- no external deps, internal hardening
```

Each phase delivers standalone value. Phases 1 and 2 can be developed in parallel.
