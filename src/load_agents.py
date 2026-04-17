"""Agent discovery — loads subagent definitions from agents/*/agent.yaml.

Scans two directories:
  1. Global agents:  ``<project_root>/agents/``  (persona-filtered, shared)
  2. User agents:    ``<project_root>/workspace/users/<user_id>/agents/``  (user-only)

Global agents are filtered by persona (``personas`` field in agent.yaml).
User agents are always loaded — they belong to the active user.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def load_agents(
    project_root: Path,
    all_tools: list,
    persona: str | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """Scan global and user agent directories, return SubAgent dicts.

    Each returned dict has the keys expected by create_deep_agent(subagents=...):
        name, description, system_prompt
    and optionally:
        model, tools, middleware

    Parameters
    ----------
    project_root:
        Absolute path to the project root.
    all_tools:
        Full list of loaded LangChain tools from load_tools().
    persona:
        Active persona.  Global subagents with a ``personas`` field that
        does not include this value are skipped.
    user_id:
        Active user ID.  When set, also scans
        ``workspace/users/<user_id>/agents/`` for user-created agents.
    """
    # Collect agent.yaml paths from both directories
    yaml_paths: list[tuple[Path, bool]] = []  # (path, is_user_agent)

    global_dir = project_root / "agents"
    if global_dir.exists():
        for p in sorted(global_dir.glob("*/agent.yaml")):
            yaml_paths.append((p, False))

    if user_id:
        user_dir = project_root / "workspace" / "users" / user_id / "agents"
        if user_dir.exists():
            for p in sorted(user_dir.glob("*/agent.yaml")):
                yaml_paths.append((p, True))

    if not yaml_paths:
        return []

    tool_registry: dict[str, object] = {t.name: t for t in all_tools}

    subagents: list[dict] = []

    for yaml_path, is_user_agent in yaml_paths:
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
            system_prompt = data.get("system_prompt", "").strip()

            if not name or not description or not system_prompt:
                logger.warning("Skipping %s — missing required fields (name/description/system_prompt)", yaml_path)
                continue

            # Persona filter: only applies to global agents, user agents always load
            if not is_user_agent:
                agent_personas: list[str] = data.get("personas") or []
                if persona and agent_personas and persona not in agent_personas:
                    logger.info("Skipping subagent '%s' — not in persona '%s' (requires %s)", name, persona, agent_personas)
                    continue

            # Resolve tools: names → objects; missing names are warned and skipped
            requested_tools: list[str] = data.get("tools") or []
            if requested_tools:
                resolved = []
                for tname in requested_tools:
                    if tname in tool_registry:
                        resolved.append(tool_registry[tname])
                    else:
                        logger.warning("Agent '%s': tool '%s' not found — skipping", name, tname)
                agent_tools = resolved
            else:
                # No filter → inherit all tools
                agent_tools = list(all_tools)

            # Append co-located SKILL.md to system_prompt if present
            skill_path = yaml_path.parent / "SKILL.md"
            if skill_path.exists():
                skill_content = skill_path.read_text(encoding="utf-8").strip()
                # Strip YAML frontmatter before appending
                if skill_content.startswith("---"):
                    end = skill_content.find("---", 3)
                    skill_content = skill_content[end + 3:].strip() if end != -1 else skill_content
                system_prompt = f"{system_prompt}\n\n{skill_content}"

            subagent: dict = {
                "name": name,
                "description": description,
                "system_prompt": system_prompt,
                "tools": agent_tools,
            }

            # Optional model override
            if data.get("model"):
                subagent["model"] = data["model"]

            subagents.append(subagent)
            scope = "user" if is_user_agent else "global"
            logger.info("Subagent loaded: %s (%s)", name, scope)

        except Exception as exc:
            logger.warning("Failed to load agent from %s: %s", yaml_path, exc)

    return subagents
