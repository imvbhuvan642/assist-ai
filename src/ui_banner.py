"""Startup banner — Hermes-style two-column terminal header.

Renders an ASCII-art title, a left panel with session metadata + brand graphic,
and a right panel with tools/skills grouped by domain.  Dark-blue theme.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pyfiglet
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# --- Dark blue palette -----------------------------------------------------
PRIMARY = "bold #4FC3F7"        # bright cyan-blue (titles, highlights)
ACCENT = "#1E88E5"              # steel blue (borders, section headers)
MUTED = "#7B8FA1"               # slate gray (secondary text)
DIM = "#3A4856"                 # dimmer blue-gray (helper text)
OK = "bold #66BB6A"             # green for "enabled" / positive
BANNER_COLOR = "bold #1E88E5"

# --- Tool & skill categorizers --------------------------------------------
_TOOL_GROUPS: dict[str, list[str]] = {
    "web":         ["internet_search"],
    "content":     ["generate_cover"],
    "gmail":       ["search_gmail", "get_gmail_message", "get_gmail_thread",
                    "create_gmail_draft", "send_gmail_message"],
    "calendar":    ["create_calendar_event", "search_events", "update_calendar_event",
                    "delete_calendar_event", "get_calendars_info", "move_calendar_event",
                    "get_current_datetime"],
    "meeting":     ["create_google_meet"],
    "google_auth": ["connect_google_services", "disconnect_google_services",
                    "google_auth_status"],
    "sql":         ["sql_db_list_tables", "sql_db_schema", "sql_db_query",
                    "sql_db_query_checker"],
    "rag":         ["search_company_docs"],
    "hris":        ["get_leave_balance", "apply_leave", "get_employee_info",
                    "list_team_leaves", "list_employees"],
    "agents":      ["create_agent"],
    "user_config": ["get_user_profile", "update_user_profile", "list_available_skills",
                    "set_enabled_skills", "enable_skill", "disable_skill",
                    "list_enabled_skills", "update_approval_gate"],
}


def _categorize_tool(name: str) -> str:
    for group, names in _TOOL_GROUPS.items():
        if name in names:
            return group
    if name.startswith("sql_"):
        return "sql"
    if name.startswith("gmail") or name.endswith("_gmail_message") or name.endswith("_gmail_thread") or name.endswith("_gmail_draft"):
        return "gmail"
    return "mcp"


_SKILL_GROUPS: dict[str, set[str]] = {
    "developer": {
        "code-review", "cicd-monitoring", "sprint-management",
        "doc-generation", "incident-management", "query-writing",
        "schema-exploration", "release-notes",
    },
    "hr": {
        "leave-management", "policy-qa", "employee-onboarding",
        "performance-review", "recruitment",
    },
    "manager": {
        "standup-summary", "one-on-one-prep", "okr-tracking",
        "resource-allocation", "escalation-handling",
    },
    "product": {
        "feature-tracking", "feedback-analysis", "roadmap-management",
        "competitive-analysis", "stakeholder-comms",
    },
    "general": {
        "web-search", "email-management", "calendar-management",
        "meeting-management", "content-writer",
    },
    "meta": {
        "preferences", "onboarding", "skill-creation",
    },
}


def _categorize_skill(name: str) -> str:
    for group, names in _SKILL_GROUPS.items():
        if name in names:
            return group
    return "other"


# --- Discovery helpers -----------------------------------------------------

def _discover_skills(project_root: Path) -> list[str]:
    skills_dir = project_root / "skills"
    if not skills_dir.exists():
        return []
    return sorted(
        d.name for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )


def _build_tool_panel(tool_names: list[str]) -> Group:
    grouped: dict[str, list[str]] = defaultdict(list)
    for name in tool_names:
        grouped[_categorize_tool(name)].append(name)

    lines: list = [Text("Available Tools", style=PRIMARY)]
    for group in sorted(grouped.keys()):
        names = sorted(grouped[group])
        # Truncate long lists to keep the panel tight
        display = ", ".join(names[:4])
        if len(names) > 4:
            display += f", +{len(names) - 4} more"
        line = Text()
        line.append(f"  {group:<12} ", style=ACCENT)
        line.append(display, style=MUTED)
        lines.append(line)
    return Group(*lines)


def _build_skill_panel(skill_names: list[str], enabled_names: set[str]) -> Group:
    grouped: dict[str, list[str]] = defaultdict(list)
    for name in skill_names:
        grouped[_categorize_skill(name)].append(name)

    lines: list = [Text("\nAvailable Skills", style=PRIMARY)]

    # Custom group order — persona groups first, then meta, then other
    order = ["developer", "hr", "manager", "product", "general", "meta", "other"]
    for group in order:
        if group not in grouped:
            continue
        names = sorted(grouped[group])
        parts = Text()
        parts.append(f"  {group:<12} ", style=ACCENT)
        for i, name in enumerate(names):
            if i > 0:
                parts.append(", ", style=DIM)
            style = OK if name in enabled_names else MUTED
            parts.append(name, style=style)
        lines.append(parts)
    return Group(*lines)


def _build_left_panel(
    *,
    model_label: str,
    persona: str,
    user_id: str | None,
    thread_id: str,
    log_file: Path | str,
    tracing: list[str],
    tool_count: int,
    skill_count: int,
    version: str,
) -> Panel:
    meta = Table.grid(padding=(0, 1))
    meta.add_column(style=MUTED, no_wrap=True)
    meta.add_column(style="bright_white")
    meta.add_row("Version", f"{version}")
    meta.add_row("Model", model_label)
    meta.add_row("Persona", persona)
    meta.add_row("User", user_id or "(default)")
    meta.add_row("Thread", thread_id)
    meta.add_row("Log", str(log_file))
    if tracing:
        meta.add_row("Tracing", ", ".join(tracing))
    meta.add_row("Loaded", f"{tool_count} tools · {skill_count} skills")

    body = meta
    return Panel(
        body,
        border_style=ACCENT,
        padding=(1, 2),
        title=Text("Session", style=PRIMARY),
        title_align="left",
    )


def _build_right_panel(tool_names: list[str], skill_names: list[str], enabled_names: set[str]) -> Panel:
    body = Group(
        _build_tool_panel(tool_names),
        _build_skill_panel(skill_names, enabled_names),
    )
    return Panel(
        body,
        border_style=ACCENT,
        padding=(1, 2),
        title=Text("Capabilities", style=PRIMARY),
        title_align="left",
    )


# --- Public entry ----------------------------------------------------------

def render_banner(
    console: Console,
    *,
    project_root: Path,
    tool_names: list[str],
    enabled_skill_names: set[str] | None = None,
    model_label: str,
    persona: str,
    user_id: str | None,
    thread_id: str,
    log_file: Path | str,
    tracing: list[str] | None = None,
    version: str = "v1.0.0",
) -> None:
    """Print the Hermes-style startup banner to the provided Rich console."""

    # --- ASCII title ------------------------------------------------------
    ascii_art = pyfiglet.figlet_format("ASSIST-AI", font="ansi_shadow").rstrip()
    console.print(Text(ascii_art, style=BANNER_COLOR))

    # --- Two-column body --------------------------------------------------
    skill_names = _discover_skills(project_root)
    enabled = enabled_skill_names or set(skill_names)  # empty filter = all enabled

    left = _build_left_panel(
        model_label=model_label,
        persona=persona,
        user_id=user_id,
        thread_id=thread_id,
        log_file=log_file,
        tracing=tracing or [],
        tool_count=len(tool_names),
        skill_count=len(skill_names),
        version=version,
    )
    right = _build_right_panel(tool_names, skill_names, enabled)

    layout = Table.grid(padding=(0, 1), expand=True)
    layout.add_column(ratio=2)
    layout.add_column(ratio=3)
    layout.add_row(left, right)
    console.print(layout)

    # --- Footer tip -------------------------------------------------------
    tip = Text()
    tip.append("  Tip: ", style=PRIMARY)
    tip.append("type ", style=MUTED)
    tip.append("exit", style="bold")
    tip.append(" or ", style=MUTED)
    tip.append("quit", style="bold")
    tip.append(" to end the session.\n", style=MUTED)
    console.print(tip)
