"""Agent discovery — loads subagent definitions from agents/*/agent.yaml."""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def load_agents(project_root: Path, all_tools: list) -> list[dict]:
    """Scan agents/*/agent.yaml and return a list of SubAgent dicts.

    Each returned dict has the keys expected by create_deep_agent(subagents=...):
        name, description, system_prompt
    and optionally:
        model, tools, middleware

    Parameters
    ----------
    project_root:
        Absolute path to the project root (used to locate the agents/ dir).
    all_tools:
        Full list of loaded LangChain tools from load_tools().
        Used to resolve tool names declared in agent.yaml → actual tool objects.
    """
    agents_dir = project_root / "agents"
    if not agents_dir.exists():
        return []

    tool_registry: dict[str, object] = {t.name: t for t in all_tools}

    subagents: list[dict] = []

    for yaml_path in sorted(agents_dir.glob("*/agent.yaml")):
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
            system_prompt = data.get("system_prompt", "").strip()

            if not name or not description or not system_prompt:
                logger.warning("Skipping %s — missing required fields (name/description/system_prompt)", yaml_path)
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
            logger.info("Subagent loaded: %s", name)

        except Exception as exc:
            logger.warning("Failed to load agent from %s: %s", yaml_path, exc)

    return subagents
