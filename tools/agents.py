"""Tool for dynamically creating new specialized agents with associated skills."""

import logging
import re
from pathlib import Path

import yaml
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_AGENTS_DIR = _PROJECT_ROOT / "agents"


def _slugify(name: str) -> str:
    """Convert a name to a valid directory slug (lowercase, hyphens only)."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


@tool
def create_agent(
    name: str,
    description: str,
    system_prompt: str,
    skill_instructions: str = "",
    tools: list[str] | None = None,
    model: str = "",
) -> str:
    """Create a new specialized subagent with an associated skill.

    The subagent is registered in agents/<name>/agent.yaml and becomes active
    after the next restart. The associated skill (skills/<name>/SKILL.md) is
    available immediately on the next message.

    Args:
        name: Agent name — lowercase, hyphens only (e.g. "data-analyst").
        description: One-line description of when to route to this agent.
        system_prompt: Full system instructions for the agent.
        skill_instructions: Markdown body for the skill file (optional).
            If omitted, a minimal skill is generated from the description.
        tools: List of tool names this agent should have access to.
            Empty list or omitted = inherits all tools from the main agent.
        model: Model override (e.g. "anthropic:claude-haiku-4-5-20251001").
            Leave empty to use the same model as the main agent.
    """
    slug = _slugify(name)
    if not slug:
        return "Error: could not derive a valid agent slug from the provided name."

    # ------------------------------------------------------------------ #
    # 1. Write agents/<slug>/agent.yaml
    # ------------------------------------------------------------------ #
    agent_dir = _AGENTS_DIR / slug
    agent_dir.mkdir(parents=True, exist_ok=True)

    agent_data: dict = {
        "name": slug,
        "description": description,
        "system_prompt": system_prompt,
    }
    if tools:
        agent_data["tools"] = tools
    if model:
        agent_data["model"] = model

    agent_yaml_path = agent_dir / "agent.yaml"
    with open(agent_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(agent_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    logger.info("Agent config written: %s", agent_yaml_path)

    # ------------------------------------------------------------------ #
    # 2. Write agents/<slug>/SKILL.md (co-located with agent.yaml)
    # ------------------------------------------------------------------ #
    if not skill_instructions.strip():
        skill_instructions = f"""# {name.replace("-", " ").title()} Skill

{description}

## When to Use

- Route to this agent when the user's request matches: {description}

## Notes

- This skill was auto-generated. Update it with more specific instructions as needed.
"""

    skill_content = f"""---
name: {slug}
description: "{description}"
---

{skill_instructions.strip()}
"""
    skill_path = agent_dir / "SKILL.md"
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_content)

    logger.info("Skill written: %s", skill_path)

    # ------------------------------------------------------------------ #
    # 3. Return confirmation
    # ------------------------------------------------------------------ #
    return (
        f"Agent '{slug}' created.\n"
        f"  Config : agents/{slug}/agent.yaml\n"
        f"  Skill  : agents/{slug}/SKILL.md\n\n"
        "Restart the agent for the subagent to become active."
    )
