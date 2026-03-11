"""Skill loading — discovery from SKILL.md files and skill-router subagent factory."""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Absolute path to the skills directory at project root
SKILLS_DIR = str(_PROJECT_ROOT / "skills")


def discover_skills(skills_dir: str = SKILLS_DIR) -> list[dict]:
    """Scan `skills_dir` for SKILL.md files and extract their frontmatter.

    Returns a list of dicts with keys: name, description, path.
    Only skills with both `name:` and `description:` frontmatter fields are included.
    """
    skills = []
    for skill_md in sorted(Path(skills_dir).rglob("SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        if name_match and desc_match:
            skills.append(
                {
                    "name": name_match.group(1).strip(),
                    "description": desc_match.group(1).strip(),
                    "path": str(skill_md.parent),
                }
            )
            logger.debug("Discovered skill: %s", name_match.group(1).strip())
        else:
            logger.warning(
                "Skipping %s — missing name or description frontmatter", skill_md
            )
    return skills


def create_skill_router(skills_dir: str, model) -> dict:
    """Return a SubAgent dict for the skill-router.

    deepagents expects `subagents` to be a list of dicts with at minimum
    `name`, `description`, and `system_prompt` keys — NOT compiled graph objects.
    The framework builds the subagent internally from this spec.
    """
    skill_list = discover_skills(skills_dir)
    if not skill_list:
        logger.warning(
            "No skills found in %s — skill_router subagent will have nothing to route.",
            skills_dir,
        )

    skill_lines = "\n".join(
        f"- **{s['name']}**: {s['description']}" for s in skill_list
    )

    prompt_path = _PROJECT_ROOT / "prompts" / "skill_router_prompt.md"
    base_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

    system_prompt = f"{base_prompt}\n\nAvailable skills:\n{skill_lines}"

    logger.info(
        "Creating skill_router subagent with %d skills: %s",
        len(skill_list),
        [s["name"] for s in skill_list],
    )

    return {
        "name": "skill_router",
        "description": (
            "Routes user requests to the most appropriate skill. "
            "Call this before any complex task to get the right skill name."
        ),
        "system_prompt": system_prompt,
        "model": model,
    }
