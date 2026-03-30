# Assist AI

A proactive employee assistant powered by LangChain + DeepAgents. Supports persistent memory, skill-based task routing, dynamic subagent creation, MCP server integration, and multi-turn conversations via terminal.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env  # add API keys

# Run in terminal
python main.py
```

### CLI Options

```
python main.py                        # default thread, INFO logging
python main.py --thread <id>          # named conversation thread (persists memory)
python main.py --debug                # enable DEBUG logging
python main.py --config path/to.yaml  # custom config file
```

---

## Project Structure

```
├── main.py                    # Terminal chat entry point
├── config.yaml                # LLM provider, agent, database, MCP settings
├── src/
│   ├── agent.py               # Agent assembly — wires all components together
│   ├── load_config.py         # Config loading + Pydantic validation
│   ├── load_tools.py          # Tool discovery and registration
│   ├── load_agents.py         # Subagent discovery from agents/*/agent.yaml
│   ├── load_mcp.py            # MCP server connections (stdio + SSE)
│   ├── memory.py              # Persistent checkpointer + filesystem backend
│   └── logger.py              # Per-session file logging
├── tools/
│   ├── websearch.py           # Tavily web search
│   ├── content.py             # Cover image generation (Google GenAI)
│   ├── agents.py              # create_agent tool (dynamic subagent creation)
│   ├── gmail.py               # Gmail read/send tools
│   ├── calendar_tools.py      # Google Calendar tools
│   └── sqltools.py            # SQL query utilities
├── skills/                    # Main agent skill modules (auto-discovered)
│   ├── web-search/
│   ├── content-writer/
│   ├── query-writing/
│   ├── schema-exploration/
│   ├── email-management/
│   ├── calendar-management/
│   └── skill-creation/        # Skill for creating new skills at runtime
├── agents/                    # Dynamically created subagents
│   └── <agent-name>/
│       ├── agent.yaml         # Subagent config (name, description, system_prompt, tools)
│       └── SKILL.md           # Subagent skill instructions (injected at startup)
├── memories/                  # Persistent agent memory (gitignored)
│   ├── identity.md            # Agent personality/tone
│   ├── agent.md               # Agent capabilities
│   └── user_preferences.txt   # User preferences written by the agent
├── data/                      # SQLite conversation checkpoints (gitignored)
└── logs/                      # Per-session log files (gitignored)
```

---

## Configuration (`config.yaml`)

| Section | Key | Description |
|---------|-----|-------------|
| `provider` | `name` | LLM provider: `openai`, `anthropic`, `google_genai` |
| `provider` | `model` | Model ID (e.g. `gpt-4o`, `claude-sonnet-4-6`, `gemini-2.0-flash`) |
| `provider` | `temperature` | Sampling temperature (0.0–2.0) |
| `provider` | `max_tokens` | Max output tokens |
| `agent` | `data_dir` | Directory for SQLite checkpoints |
| `agent` | `timezone` | Timezone string (e.g. `Asia/Kolkata`) |
| `agent` | `interrupt_on` | Tool names requiring human approval before executing |
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
  model: gpt-4o
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
- **User preferences** — agent writes to `memories/user_preferences.txt` on disk; injected fresh on every invocation via dynamic prompt middleware.
- **Identity + capabilities** — `memories/identity.md` and `memories/agent.md` are loaded as the static system prompt.

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

**Adding a skill at runtime:** just tell the agent — it uses the `skill-creation` skill to write a new `skills/<name>/SKILL.md`. Active on the next message, no restart needed.

---

## Dynamic Agent Creation

You can create specialized subagents at runtime by telling the agent:

> *"Create a new agent called report-writer that specialises in generating executive PDF reports"*

The agent calls the `create_agent` tool, which writes two files:

```
agents/report-writer/
├── agent.yaml    # subagent config — loaded at next restart
└── SKILL.md      # skill instructions — injected into subagent system_prompt
```

**`agent.yaml` schema:**

```yaml
name: report-writer
description: "When to route to this agent (used by the router)"
system_prompt: "Full system instructions for this agent..."
tools:                   # optional — list of tool names to give this agent
  - internet_search      # empty or omitted = inherits all tools
model: anthropic:claude-haiku-4-5-20251001  # optional model override
```

**`SKILL.md`** — co-located with `agent.yaml`, not in the main `skills/` folder. Its Markdown body (without frontmatter) is appended to the subagent's `system_prompt` automatically at startup.

> **Note:** The skill is isolated to the subagent's context and does not appear in the main agent's skill list.

**Lifecycle:**

| Action | When it takes effect |
|--------|----------------------|
| Skill instructions (`SKILL.md`) | Appended to system_prompt at next restart |
| Subagent routing | Active at next restart (compiled into graph) |

To edit an existing agent, update `agents/<name>/agent.yaml` or `agents/<name>/SKILL.md` and restart.

---

## MCP Servers

MCP (Model Context Protocol) servers expose external tools to the agent. Add any number of servers to `config.yaml` under `mcp.servers` — their tools are loaded automatically at startup alongside the built-in tools.

### Supported Transports

#### `stdio` — spawns a local subprocess

```yaml
mcp:
  servers:
    filesystem:
      transport: stdio
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]

    playwright:
      transport: stdio
      command: npx
      args: ["-y", "@playwright/mcp"]

    python-runner:
      transport: stdio
      command: uvx
      args: ["mcp-server-python"]
      env:
        SOME_VAR: "value"
```

#### `sse` — connects to a running HTTP MCP server

```yaml
mcp:
  servers:
    my-remote-server:
      transport: sse
      url: "http://localhost:8080/sse"
```

### How It Works

1. `config.yaml` declares the servers under `mcp.servers`
2. On startup, `src/load_mcp.py` connects via `MultiServerMCPClient` (from `langchain-mcp-adapters`)
3. All tools returned by the servers are added to the agent's tool list — no code changes needed
4. For `stdio` servers, a persistent background event loop keeps the subprocess alive across agent calls
5. On exit, `shutdown_mcp()` terminates subprocesses cleanly

### Required Package

```bash
pip install langchain-mcp-adapters
```

### Adding Tools from an MCP Server

Any tool exposed by a connected MCP server is automatically available to the agent and to any subagent that inherits all tools. To restrict a subagent to only specific MCP tools, list their names in `agent.yaml`:

```yaml
tools:
  - filesystem_read_file
  - filesystem_write_file
```

Tool names are the exact names reported by the MCP server (visible in DEBUG logs on startup).

---

## Human-in-the-Loop (Approval Gates)

Certain tools require explicit approval before the agent executes them. Configure in `config.yaml`:

```yaml
agent:
  interrupt_on:
    - send_gmail_message
    - delete_calendar_event
    - move_calendar_event
```

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
| `GOOGLE_API_KEY` | Google GenAI models + cover image generation |
| `TAVILY_API_KEY` | Web search tool |
| `DATABASE_URL` | SQL database tools (optional) |
| `LANGFUSE_PUBLIC_KEY` | Langfuse tracing (optional) |
| `LANGFUSE_SECRET_KEY` | Langfuse tracing (optional) |

Environment variables can also be referenced in `config.yaml` using `${VAR_NAME}` syntax.
