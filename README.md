# Assist AI

A proactive employee assistant powered by LangChain + DeepAgents. Supports persistent memory, skill-based task routing, and multi-turn conversations via terminal.

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
python main.py --thread <id>          # named conversation thread
python main.py --debug                # enable DEBUG logging
python main.py --config path/to.yaml  # custom config file
```

---

## Project Structure

```
├── main.py                  # Terminal chat entry point
├── config.yaml              # LLM provider, agent, database settings
├── src/
│   ├── agent.py             # Agent assembly (thin orchestrator)
│   ├── load_config.py       # Config loading + validation (Pydantic)
│   ├── load_tools.py        # Tool discovery and registration
│   ├── load_skills.py       # Skill discovery + skill-router subagent
│   ├── memory.py            # Persistent checkpointer + filesystem backend
│   └── logger.py            # Per-session file logging
├── tools/
│   ├── websearch.py         # Tavily web search tool
│   └── content.py           # Cover image generation (Google GenAI)
├── skills/
│   ├── web-search/          # Web search skill
│   ├── content-writer/      # Content writing skill
│   ├── query-writing/       # SQL query writing skill
│   └── schema-exploration/  # Database schema exploration skill
├── prompts/
│   ├── agent_system_prompt.md     # Main agent instructions
│   └── skill_router_prompt.md     # Skill router subagent instructions
├── memories/                # Persistent agent memory (gitignored)
├── data/                    # SQLite checkpoints (gitignored)
└── logs/                    # Per-session logs (gitignored)
```

---

## Configuration (`config.yaml`)

| Section | Key | Description |
|---------|-----|-------------|
| `provider` | `name` | LLM provider: `openai`, `anthropic`, `google_genai` |
| `provider` | `model` | Model ID (e.g. `gpt-4o`, `claude-sonnet-4-6`) |
| `agent` | `data_dir` | Where to store SQLite checkpoints |
| `database` | `url` | Optional SQL database URI for SQL tools |
| `skills` | `enabled` | Enable/disable skill routing |

---

## Memory

- **Conversation history** — persisted to `data/checkpoints.db` (SQLite) per thread ID
- **User preferences** — agent writes to `/memories/user_preferences.txt` (real disk at `memories/`)
- Restart the process and memory is retained; use the same `--thread` ID to resume

---

## Skills

Each skill lives in `skills/<name>/SKILL.md` with `name:` and `description:` frontmatter. The agent uses a `skill_router` subagent to pick the right skill before executing complex tasks.

To add a skill: create `skills/my-skill/SKILL.md` — it's auto-discovered on startup.

---

## Required Environment Variables

| Variable | Used For |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI models |
| `GOOGLE_API_KEY` | Google GenAI models |
| `TAVILY_API_KEY` | Web search tool |
| `DATABASE_URL` | SQL database tools (optional) |
