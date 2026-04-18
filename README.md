# Assist AI

A role-aware digital employee assistant powered by LangChain + DeepAgents. Serves **Developers, HRs, Managers, and Product Managers** with persona-specific skills, per-user profiles, and self-service customization.

Supports persistent memory, skill-based task routing, dynamic subagent creation, RAG-powered policy Q&A, HRIS integration, MCP server integration, and multi-turn conversations via terminal.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env  # add API keys

# Run in terminal (default mode)
python main.py

# Run with a named user profile (per-user skills, memory, preferences)
python main.py --user vaishak

# New user → auto-triggers onboarding wizard
python main.py --user priya
```

### CLI Options

```
python main.py                        # default thread, INFO logging
python main.py --user <id>            # per-user profile, skill filtering, isolated memory
python main.py --thread <id>          # named conversation thread (persists memory)
python main.py --debug                # enable DEBUG logging
python main.py --config path/to.yaml  # custom config file
```

---

## Personas

The agent adapts its personality, skill routing, and subagent access based on the active persona.

| Persona | Primary Skills | Subagent |
|---------|---------------|----------|
| **Developer** | code-review, cicd-monitoring, sprint-management, doc-generation, incident-management, query-writing, schema-exploration | developer-assistant |
| **HR** | leave-management, policy-qa, employee-onboarding, performance-review, recruitment | hr-assistant |
| **Manager** | standup-summary, one-on-one-prep, okr-tracking, resource-allocation, escalation-handling | manager-assistant |
| **Product Manager** | feature-tracking, feedback-analysis, roadmap-management, competitive-analysis, release-notes, stakeholder-comms | pm-assistant |

Universal skills available to all personas: web-search, email-management, calendar-management, preferences, onboarding.

### Setting the Persona

**Global default** — set in `config.yaml`:
```yaml
persona:
  active: "developer"  # developer | hr | manager | product_manager
```

**Per-user** — selected during onboarding and stored in `workspace/users/<id>/profile.yaml`. Overrides the global default when using `--user`.

---

## Per-User Profiles

Each user gets an isolated profile directory under `workspace/users/<id>/`:

```
workspace/users/<id>/
├── profile.yaml              # name, persona, timezone, communication style
├── enabled_skills.yaml       # which skills are active (persona-aware defaults)
├── interrupt_on.yaml         # per-user approval gates
├── integrations.yaml         # per-user service config (Jira project, Slack channel)
└── memories/                 # isolated persistent memory
    └── preferences.txt       # free-form learned preferences
```

Users can customize their setup conversationally:
- *"Disable the web-search skill"*
- *"Add an approval gate for calendar events"*
- *"Switch me to the PM persona"*
- *"Show my config"*

New users are auto-onboarded with role selection, preference setup, and persona-appropriate skill defaults.

---

## Project Structure

```
├── main.py                    # Terminal chat entry point
├── config.yaml                # LLM provider, persona, RAG, HRIS, MCP settings
├── src/
│   ├── agent.py               # Agent assembly — persona overlay, user-scoped prompts
│   ├── load_config.py         # Config loading + Pydantic validation
│   ├── load_tools.py          # Tool discovery and registration
│   ├── load_agents.py         # Subagent discovery (persona-filtered)
│   ├── load_mcp.py            # MCP server connections (stdio + SSE)
│   ├── memory.py              # Persistent checkpointer + user-scoped filesystem backend
│   └── logger.py              # Per-session file logging
├── tools/
│   └── All Tool scripts are stored here.
├── skills/                    # Skill modules (auto-discovered SKILL.md)
│   └── All Skills are Stored here   
├── agents/                    # Persona-specific subagents
│   ├── developer-assistant/   # Code review, CI/CD, sprints, incidents
│   ├── hr-assistant/          # Leave, policy, onboarding, recruitment
│   ├── manager-assistant/     # Standups, 1:1s, OKRs, escalations
│   └── pm-assistant/          # Features, roadmap, releases, stakeholders
├── prompts/personas/          # Persona prompt overlays
│   ├── developer.md
│   ├── hr.md
│   ├── manager.md
│   └── product_manager.md
├── memories/                  # Global agent memory (gitignored)
│   ├── identity.md            # Agent personality/tone
│   ├── agent.md               # Agent capabilities + routing rules
│   └── user_preferences.txt   # Global user preferences
├── workspace/users/           # Per-user profiles and memories
├── data/                      # SQLite checkpoints + policy documents
│   └── policies/              # Company docs for RAG (PDF, TXT, MD)
├── docs/
│   └── EXTENSION_PLAN.md      # Full extension plan documentation
└── logs/                      # Per-session log files (gitignored)
```

---

## Configuration (`config.yaml`)

| Section | Key | Description |
|---------|-----|-------------|
| `provider` | `name` | LLM provider: `openai`, `anthropic`, `google_genai` |
| `provider` | `model` | Model ID (e.g. `gpt-5-mini`, `claude-sonnet-4-6`, `gemini-2.0-flash`) |
| `provider` | `temperature` | Sampling temperature (0.0–2.0) |
| `provider` | `max_tokens` | Max output tokens |
| `persona` | `active` | Default persona: `developer`, `hr`, `manager`, `product_manager` |
| `users` | `dir` | Per-user profile directory (default: `./workspace/users`) |
| `rag` | `enabled` | Enable RAG document search for policy Q&A |
| `rag` | `documents_dir` | Path to company docs (default: `./data/policies`) |
| `hris` | `enabled` | Enable HRIS integration for leave/employee data |
| `hris` | `provider` | HRIS backend: `mock`, `bamboohr`, `keka`, `darwinbox` |
| `agent` | `data_dir` | Directory for SQLite checkpoints |
| `agent` | `timezone` | Timezone string (e.g. `Asia/Kolkata`) |
| `agent` | `interrupt_on` | Tool names requiring human approval |
| `database` | `url` | SQL database URI for SQL tools (optional) |
| `skills` | `enabled` | Enable/disable skill routing |
| `langfuse` | `enabled` | Enable Langfuse tracing |
| `mcp` | `servers` | MCP server definitions (see MCP section below) |

### Switching LLM Provider

Edit `config.yaml` — only one `provider` block should be active:

```yaml
# OpenAI
provider:
  name: openai
  model: gpt-5-mini
  temperature: 0.5
  max_tokens: 8192

# Anthropic Claude
provider:
  name: anthropic
  model: claude-sonnet-4-6
  temperature: 0.5
  max_tokens: 8192

# Google Gemini
provider:
  name: google_genai
  model: gemini-2.0-flash
  temperature: 1.0
  max_tokens: 8192
```

---

## Memory

- **Conversation history** — persisted to `data/checkpoints.db` (SQLite) per `--thread` ID. Pass the same ID across sessions to resume context.
- **User preferences** — stored per-user in `workspace/users/<id>/memories/preferences.txt`; injected fresh on every invocation via dynamic prompt middleware.
- **Global preferences** — `memories/user_preferences.txt` applies to all users as a fallback.
- **Identity + capabilities** — `memories/identity.md`, persona overlay, and `memories/agent.md` are loaded as the static system prompt.

---

## Skills

Skills are Markdown instruction modules in `skills/<name>/SKILL.md`. The agent auto-discovers them at startup and follows their workflows when relevant.

**Frontmatter fields:**

```markdown
---
name: my-skill           # must match directory name
description: "When and why to use this skill"
requires_env:            # optional — skill hidden if env var missing
  - MY_API_KEY
---

# Skill Title
...instructions...
```

**Per-user skill filtering:** Each user's `enabled_skills.yaml` controls which skills are active. Persona defaults are applied on first setup; users can add/remove skills conversationally.

**Adding a skill at runtime:** just tell the agent — it uses the `skill-creation` skill to write a new `skills/<name>/SKILL.md`. Active on the next message, no restart needed.

---

## Subagents

Each persona has a specialized subagent loaded from `agents/<name>/`:

```yaml
# agents/developer-assistant/agent.yaml
name: developer-assistant
personas: [developer]        # only loaded for this persona
description: "When to route to this agent"
system_prompt: "Full system instructions..."
tools: []                    # optional — empty = inherits all tools
model: ""                    # optional — override model
```

**Persona filtering:** Subagents with a `personas` field are only loaded when the active persona matches. Subagents without a `personas` field load for all personas.

**Co-located SKILL.md:** If an `agents/<name>/SKILL.md` exists, its Markdown body (sans frontmatter) is appended to the subagent's `system_prompt` automatically.

**Dynamic creation:** Tell the agent to create a new subagent — it writes `agent.yaml` + `SKILL.md`. Active at next restart.

---

## RAG (Policy Q&A)

Semantic search over company documents for policy questions. Used by the `policy-qa` skill.

**Setup:**

1. Enable in `config.yaml`:
   ```yaml
   rag:
     enabled: true
     documents_dir: "./data/policies"
   ```
2. Place documents in `data/policies/` — supports `.pdf`, `.txt`, `.md`
3. Documents are chunked, embedded, and stored in ChromaDB on first startup

**Usage:** Ask the agent policy questions — *"What's the notice period?"*, *"What's our leave policy?"* — and it searches the documents with source attribution.

---

## HRIS Integration

Leave management and employee data. Supports multiple providers.

**Setup:**

```yaml
hris:
  enabled: true
  provider: "mock"    # mock | bamboohr | keka | darwinbox
```

The `mock` provider includes sample employee data for testing. For production, configure the provider's `base_url` and `api_key`.

**Tools:** `get_leave_balance`, `apply_leave`, `get_employee_info`, `list_team_leaves`, `list_employees`

---

## MCP Servers

MCP (Model Context Protocol) servers expose external tools to the agent. Configured in `config.yaml`:

```yaml
mcp:
  servers:
    # GitHub — PRs, issues, code search, CI/CD workflows
    github:
      transport: stdio
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_TOKEN}"

    # Jira — issues, sprints, boards, JQL search
    jira:
      transport: stdio
      command: npx
      args: ["-y", "@modelcontextprotocol/server-atlassian"]
      env:
        JIRA_HOST: "${JIRA_HOST}"
        JIRA_EMAIL: "${JIRA_EMAIL}"
        JIRA_API_TOKEN: "${JIRA_API_TOKEN}"

    # Slack — channel messages, threads, search
    slack:
      transport: stdio
      command: npx
      args: ["-y", "@anthropic/mcp-server-slack"]
      env:
        SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}"

    # Notion — pages, databases, search
    notion:
      transport: stdio
      command: npx
      args: ["-y", "@notionhq/mcp-server-notion"]
      env:
        NOTION_API_KEY: "${NOTION_API_KEY}"
```

Supports `stdio` (spawns local process) and `sse` (connects to HTTP server) transports. Tools from connected servers are automatically available to the agent.

---

## Human-in-the-Loop (Approval Gates)

Certain tools require explicit approval before the agent executes them. Configure globally in `config.yaml`:

```yaml
agent:
  interrupt_on:
    - send_gmail_message
    - delete_calendar_event
    - move_calendar_event
    - create_pull_request
    - merge_pull_request
    - create_issue
    - apply_leave
```

Per-user overrides are stored in `workspace/users/<id>/interrupt_on.yaml`.

When triggered, the terminal pauses and prompts:

```
[Approval required] Agent wants to call: send_gmail_message
  Arguments: {to: "...", subject: "...", body: "..."}
  Approve? (y/n):
```

---

## Required Environment Variables

| Variable | Used For |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI models |
| `ANTHROPIC_API_KEY` | Anthropic Claude models |
| `GOOGLE_API_KEY` | Google GenAI models |
| `TAVILY_API_KEY` | Web search tool |
| `DATABASE_URL` | SQL database tools (optional) |
| `GITHUB_TOKEN` | GitHub MCP server (optional) |
| `JIRA_HOST`, `JIRA_EMAIL`, `JIRA_API_TOKEN` | Jira MCP server (optional) |
| `SLACK_BOT_TOKEN` | Slack MCP server (optional) |
| `NOTION_API_KEY` | Notion MCP server (optional) |
| `HRIS_BASE_URL`, `HRIS_API_KEY` | HRIS integration (optional) |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | Langfuse tracing (optional) |

Environment variables can also be referenced in `config.yaml` using `${VAR_NAME}` syntax.

---

## Extension Plan

See [docs/EXTENSION_PLAN.md](docs/EXTENSION_PLAN.md) for the full phased extension plan, including Phase 5 (Enterprise Hardening — audit logging, auth, PII redaction).
