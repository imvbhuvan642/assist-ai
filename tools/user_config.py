"""User configuration tools — CRUD operations on per-user profile and settings."""

import logging
import shutil
import threading
from pathlib import Path

import yaml
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_USERS_DIR = _PROJECT_ROOT / "workspace" / "users"
_DEFAULTS_DIR = _USERS_DIR / ".defaults"
_SKILLS_DIR = _PROJECT_ROOT / "skills"

# Module-level active user ID — set by the agent factory at startup.
_active_user_id: str = "default"

# File lock — prevents concurrent tool calls (LangGraph's asyncio.gather)
# from corrupting YAML files with simultaneous read/write.
_file_lock = threading.Lock()

# Persona → default enabled skills mapping.
# When a new user profile is created, only persona-relevant skills are enabled.
_PERSONA_SKILLS: dict[str, list[str]] = {
    "developer": [
        "code-review", "cicd-monitoring", "sprint-management", "doc-generation",
        "incident-management", "query-writing", "schema-exploration", "release-notes",
        "web-search", "email-management", "calendar-management",
        "preferences", "skill-creation",
    ],
    "hr": [
        "leave-management", "policy-qa", "employee-onboarding", "performance-review",
        "recruitment", "web-search", "email-management", "calendar-management",
        "preferences", "skill-creation",
    ],
    "manager": [
        "standup-summary", "one-on-one-prep", "okr-tracking", "resource-allocation",
        "escalation-handling", "sprint-management", "web-search", "email-management",
        "calendar-management", "preferences", "skill-creation",
    ],
    "product_manager": [
        "feature-tracking", "feedback-analysis", "roadmap-management",
        "competitive-analysis", "release-notes", "stakeholder-comms",
        "sprint-management", "web-search", "email-management", "calendar-management",
        "content-writer", "preferences", "skill-creation",
    ],
}


def set_active_user(user_id: str) -> None:
    """Set the active user ID for all user_config tools."""
    global _active_user_id
    _active_user_id = user_id


def get_user_dir(user_id: str | None = None, persona: str = "developer") -> Path:
    """Return the profile directory for a user, creating from defaults if needed.

    When creating a new profile, ``persona`` determines which skills are
    pre-enabled.  Only skills relevant to the persona are activated.
    """
    uid = user_id or _active_user_id
    user_dir = _USERS_DIR / uid
    if not user_dir.exists():
        user_dir.mkdir(parents=True, exist_ok=True)
        # Copy default templates (except enabled_skills — we build that below)
        for default_file in _DEFAULTS_DIR.glob("*.yaml"):
            if default_file.name != "enabled_skills.yaml":
                shutil.copy2(default_file, user_dir / default_file.name)
        # Write persona-aware enabled skills
        default_skills = _PERSONA_SKILLS.get(persona, _PERSONA_SKILLS["developer"])
        _write_yaml(user_dir / "enabled_skills.yaml", {"enabled": sorted(default_skills)})
        # Set persona in profile
        profile_path = user_dir / "profile.yaml"
        if profile_path.exists():
            profile = _read_yaml(profile_path)
            profile["persona"] = persona
            _write_yaml(profile_path, profile)
        # Create memories subdirectory
        (user_dir / "memories").mkdir(exist_ok=True)
        (user_dir / "memories" / "preferences.txt").write_text(
            "# User Preferences\n", encoding="utf-8"
        )
        logger.info("Created new user profile directory: %s (persona=%s, skills=%d)",
                     user_dir, persona, len(default_skills))
    return user_dir


def _read_yaml(path: Path) -> dict | list:
    """Read a YAML file, returning empty dict/list on missing or empty."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data is not None else {}


def _write_yaml(path: Path, data) -> None:
    """Write data to a YAML file atomically (write to temp, then rename)."""
    tmp_path = path.with_suffix(".yaml.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    tmp_path.replace(path)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def get_user_profile() -> str:
    """Get the current user's profile settings (name, persona, timezone, style preferences).

    Returns the full profile as a formatted string.
    """
    user_dir = get_user_dir()
    profile = _read_yaml(user_dir / "profile.yaml")
    if not profile:
        return "No profile configured yet. Run onboarding to set up your profile."
    lines = ["## Your Profile"]
    for key, value in profile.items():
        lines.append(f"- **{key}**: {value}")
    return "\n".join(lines)


@tool
def update_user_profile(key: str, value: str) -> str:
    """Update a specific field in the user's profile.

    When the persona is changed, the enabled skills are automatically updated to
    match the new persona's defaults.

    Args:
        key: The profile field to update (name, persona, timezone, communication_style, output_format).
        value: The new value for the field.
    """
    valid_keys = {"name", "persona", "timezone", "communication_style", "output_format"}
    if key not in valid_keys:
        return f"Invalid profile key '{key}'. Valid keys: {', '.join(sorted(valid_keys))}"

    valid_personas = {"developer", "hr", "manager", "product_manager"}
    if key == "persona" and value not in valid_personas:
        return f"Invalid persona '{value}'. Valid personas: {', '.join(sorted(valid_personas))}"

    user_dir = get_user_dir()
    profile_path = user_dir / "profile.yaml"
    with _file_lock:
        profile = _read_yaml(profile_path)
        profile[key] = value
        _write_yaml(profile_path, profile)

    result = f"Updated profile: {key} = {value}"

    # When persona changes, auto-update enabled skills to match the new persona
    if key == "persona":
        new_skills = _PERSONA_SKILLS.get(value, _PERSONA_SKILLS["developer"])
        skills_path = user_dir / "enabled_skills.yaml"
        with _file_lock:
            _write_yaml(skills_path, {"enabled": sorted(new_skills)})
        result += f"\nEnabled skills updated to {value} defaults ({len(new_skills)} skills)."

    return result


@tool
def list_available_skills() -> str:
    """List all globally available skills with their descriptions.

    Shows which skills exist and whether each is currently enabled for this user.
    """
    user_dir = get_user_dir()
    enabled_data = _read_yaml(user_dir / "enabled_skills.yaml")
    enabled_list = enabled_data.get("enabled", []) if isinstance(enabled_data, dict) else []
    all_enabled = len(enabled_list) == 0  # empty = all enabled

    skills = []
    for skill_dir in sorted(_SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        # Parse description from YAML frontmatter
        content = skill_md.read_text(encoding="utf-8")
        description = ""
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                try:
                    frontmatter = yaml.safe_load(content[3:end])
                    description = frontmatter.get("description", "")
                except Exception:
                    pass
        name = skill_dir.name
        status = "enabled" if (all_enabled or name in enabled_list) else "disabled"
        skills.append(f"- **{name}** [{status}]: {description}")

    if not skills:
        return "No skills found."
    return "## Available Skills\n" + "\n".join(skills)


@tool
def set_enabled_skills(skill_names: list[str]) -> str:
    """Set the exact list of enabled skills for the current user, replacing any previous list.

    This is the preferred tool for bulk skill changes (e.g., during onboarding or
    when switching personas). Use this instead of calling enable_skill/disable_skill
    multiple times.

    Args:
        skill_names: The complete list of skill names to enable. All other skills will be disabled.
    """
    # Validate all skill names
    invalid = [s for s in skill_names if not (_SKILLS_DIR / s / "SKILL.md").exists()]
    if invalid:
        return f"Unknown skills: {', '.join(invalid)}. Use list_available_skills to see valid names."

    user_dir = get_user_dir()
    path = user_dir / "enabled_skills.yaml"
    with _file_lock:
        _write_yaml(path, {"enabled": sorted(skill_names)})
    return f"Enabled {len(skill_names)} skills: {', '.join(sorted(skill_names))}"


@tool
def enable_skill(skill_name: str) -> str:
    """Enable a single skill for the current user.

    Args:
        skill_name: The name of the skill to enable (must match a directory in skills/).
    """
    if not (_SKILLS_DIR / skill_name / "SKILL.md").exists():
        return f"Skill '{skill_name}' not found. Use list_available_skills to see available skills."

    user_dir = get_user_dir()
    path = user_dir / "enabled_skills.yaml"
    with _file_lock:
        data = _read_yaml(path)
        if not isinstance(data, dict):
            data = {"enabled": []}
        enabled = data.get("enabled", [])
        if not enabled:
            return f"All skills are currently enabled (no filter active). '{skill_name}' is already available."
        if skill_name in enabled:
            return f"Skill '{skill_name}' is already enabled."
        enabled.append(skill_name)
        data["enabled"] = sorted(enabled)
        _write_yaml(path, data)
    return f"Enabled skill: {skill_name}"


@tool
def disable_skill(skill_name: str) -> str:
    """Disable a single skill for the current user. For bulk changes, prefer set_enabled_skills.

    Args:
        skill_name: The name of the skill to disable.
    """
    if not (_SKILLS_DIR / skill_name / "SKILL.md").exists():
        return f"Skill '{skill_name}' not found. Use list_available_skills to see available skills."

    user_dir = get_user_dir()
    path = user_dir / "enabled_skills.yaml"
    with _file_lock:
        data = _read_yaml(path)
        if not isinstance(data, dict):
            data = {"enabled": []}
        enabled = data.get("enabled", [])

        if not enabled:
            # Switching from all-enabled to explicit list: populate with all skills minus the disabled one
            all_skills = [
                d.name for d in sorted(_SKILLS_DIR.iterdir())
                if (d / "SKILL.md").exists() and d.name != skill_name
            ]
            data["enabled"] = all_skills
            _write_yaml(path, data)
            return f"Disabled skill: {skill_name}. Switched to explicit skill list."

        if skill_name not in enabled:
            return f"Skill '{skill_name}' is already disabled."
        enabled.remove(skill_name)
        data["enabled"] = enabled
        _write_yaml(path, data)
    return f"Disabled skill: {skill_name}"


@tool
def list_enabled_skills() -> str:
    """Show which skills are currently enabled for the user."""
    user_dir = get_user_dir()
    with _file_lock:
        data = _read_yaml(user_dir / "enabled_skills.yaml")
    enabled = data.get("enabled", []) if isinstance(data, dict) else []
    if not enabled:
        return "All skills are enabled (no filter active)."
    return "## Enabled Skills\n" + "\n".join(f"- {s}" for s in enabled)


@tool
def update_approval_gate(tool_name: str, require_approval: bool) -> str:
    """Add or remove an approval gate for a specific tool.

    Args:
        tool_name: The name of the tool to modify approval for.
        require_approval: True to require approval before executing, False to remove the gate.
    """
    user_dir = get_user_dir()
    path = user_dir / "interrupt_on.yaml"
    data = _read_yaml(path)
    if not isinstance(data, list):
        data = []

    if require_approval:
        if tool_name not in data:
            data.append(tool_name)
            _write_yaml(path, data)
            return f"Added approval gate for: {tool_name}"
        return f"Approval gate already exists for: {tool_name}"
    else:
        if tool_name in data:
            data.remove(tool_name)
            _write_yaml(path, data)
            return f"Removed approval gate for: {tool_name}"
        return f"No approval gate exists for: {tool_name}"


def get_user_config_tools() -> list:
    """Return all user configuration tools."""
    return [
        get_user_profile,
        update_user_profile,
        list_available_skills,
        set_enabled_skills,
        enable_skill,
        disable_skill,
        list_enabled_skills,
        update_approval_gate,
    ]
