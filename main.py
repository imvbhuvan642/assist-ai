"""Assist AI — terminal chat interface.

Usage:
    python main.py
    python main.py --thread my-thread-id
    python main.py --config path/to/config.yaml
    python main.py --debug

Type your message and press Enter to send.
Type 'exit' or 'quit' (or press Ctrl+C) to end the session.
"""

import argparse
import asyncio
import sys
import logging
import uuid
from rich.console import Console
from rich.prompt import Prompt

console = Console()


_PERSONA_CHOICES = {
    "1": "developer",
    "2": "hr",
    "3": "manager",
    "4": "project_manager",
}


def _prompt_new_user_basics(user_id: str) -> dict | None:
    """Collect basic profile info from a new user via an interactive form.

    Returns the collected dict, or None if the user aborts (Ctrl+C / EOF).
    """
    console.print(
        f"\n[bold #4FC3F7]Welcome to Assist AI![/bold #4FC3F7] "
        f"Let's set up your profile ([bold]{user_id}[/bold]).\n"
        f"[dim]Press Ctrl+C at any time to cancel.[/dim]\n"
    )
    try:
        name = Prompt.ask("[bold]Your name[/bold]").strip()
        designation = Prompt.ask("[bold]Your designation[/bold] [dim](e.g. Senior Engineer)[/dim]").strip()
        console.print(
            "\n[bold]Pick your role:[/bold]\n"
            "  1. Developer\n"
            "  2. HR\n"
            "  3. Manager\n"
            "  4. Project Manager"
        )
        choice = Prompt.ask("Choice", choices=list(_PERSONA_CHOICES.keys()), default="1")
        persona = _PERSONA_CHOICES[choice]
        timezone = Prompt.ask(
            "[bold]Your timezone[/bold] [dim](e.g. Asia/Kolkata, UTC, America/Los_Angeles)[/dim]",
            default="Asia/Kolkata",
        ).strip()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Setup cancelled. Run again to start over.[/yellow]")
        return None

    return {
        "name": name,
        "designation": designation,
        "persona": persona,
        "timezone": timezone,
    }


def _bootstrap_new_user(user_id: str, basics: dict) -> None:
    """Create the user's profile directory and write collected form data."""
    from tools.user_config import get_user_dir, _read_yaml, _write_yaml, _sync_managed_preferences, _file_lock

    # Creates the dir + persona-scoped enabled_skills + memories/preferences.txt
    user_dir = get_user_dir(user_id, persona=basics["persona"])

    profile_path = user_dir / "profile.yaml"
    with _file_lock:
        profile = _read_yaml(profile_path) or {}
        profile["name"] = basics["name"]
        profile["designation"] = basics["designation"]
        profile["persona"] = basics["persona"]
        profile["timezone"] = basics["timezone"]
        profile.setdefault("agent_name", "")
        _write_yaml(profile_path, profile)
        _sync_managed_preferences(user_id)

from src.load_config import load_config
from src.logger import setup_logging
from src.agent import create_agent
from src.yaml_utils import load_yaml_dict

_THREAD_ID_DEFAULT = uuid.uuid4().hex


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assist AI — proactive employee assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to config YAML (default: config.yaml)",
    )
    parser.add_argument(
        "--thread",
        default=_THREAD_ID_DEFAULT,
        metavar="ID",
        help=f"Conversation thread ID (default: {_THREAD_ID_DEFAULT!r})",
    )
    parser.add_argument(
        "--user",
        default=None,
        metavar="ID",
        help="User ID for per-user profiles, skill toggles, and isolated memory",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable DEBUG logging",
    )
    return parser.parse_args()


async def run():
    args = parse_args()
    log_level = "DEBUG" if args.debug else "INFO"
    log_file = setup_logging(log_level)

    logger = logging.getLogger(__name__)

    try:
        config = load_config(args.config)
    except Exception as exc:
        print(f"[ERROR] Failed to load config: {exc}", file=sys.stderr)
        sys.exit(1)

    # Detect new user → run interactive form, then trigger agent-driven onboarding
    user_id = args.user
    is_new_user = False
    active_persona = config.persona.active  # default from config.yaml
    agent_name: str = ""
    if user_id:
        from pathlib import Path
        user_profile_dir = Path(config.users.dir).resolve() / user_id
        is_new_user = not user_profile_dir.exists()

        if is_new_user:
            basics = _prompt_new_user_basics(user_id)
            if basics is None:
                sys.exit(0)
            _bootstrap_new_user(user_id, basics)
            active_persona = basics["persona"]
        else:
            profile_path = user_profile_dir / "profile.yaml"
            if profile_path.exists():
                try:
                    profile = load_yaml_dict(profile_path, context=f"user profile for {user_id}")
                    active_persona = profile.get("persona", active_persona)
                    agent_name = profile.get("agent_name") or ""
                except Exception:
                    pass

    # Override config persona with user's actual persona so the system prompt matches
    config.persona.active = active_persona
    assistant_label = agent_name.strip() if agent_name else "Assistant"

    # Namespace thread_id by user so conversation history doesn't bleed between users
    effective_thread_id = f"{user_id}:{args.thread}" if user_id else args.thread

    print("\n╔══════════════════════════════════════╗")
    print("║         Assist AI — Terminal         ║")
    print("╚══════════════════════════════════════╝")
    print(f"  Name    : {assistant_label}")
    if user_id:
        print(f"  User    : {user_id}")
    print(f"  Session : {effective_thread_id}")
    print(f"  Persona : {active_persona}")
    print(f"  Model   : {config.provider.name} / {config.provider.model}")
    print(f"  Log     : {log_file}")
    print("  Type 'exit' or 'quit' to end.\n")

    try:
        with console.status("[bold #4FC3F7]Loading agent...", spinner="dots"):
            agent = await create_agent(config, user_id=user_id)
    except Exception as exc:
        logger.exception("Failed to create agent")
        print(f"[ERROR] Failed to create agent: {exc}", file=sys.stderr)
        sys.exit(1)

    run_config: dict = {"configurable": {
        "thread_id": effective_thread_id,
        "timezone": config.agent.timezone,
    }}

    if config.langfuse.enabled:
        try:
            from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
            langfuse_handler = LangfuseCallbackHandler()
            run_config["callbacks"] = [langfuse_handler]
            logger.info("Langfuse tracing enabled (session_id=%s)", effective_thread_id)
        except ImportError:
            logger.warning("Langfuse enabled in config but 'langfuse' package not installed — skipping")

    if config.langsmith.enabled:
        import os as _os
        _os.environ.setdefault("LANGSMITH_TRACING", "true")
        if config.langsmith.project:
            _os.environ.setdefault("LANGSMITH_PROJECT", config.langsmith.project)
        if _os.environ.get("LANGSMITH_API_KEY"):
            logger.info("LangSmith tracing enabled (project=%s)",
                         config.langsmith.project or "default")
        else:
            logger.warning("LangSmith enabled in config but LANGSMITH_API_KEY not set — skipping")

    if is_new_user:
        console.print(
            "[bold #FFB74D]New user detected![/bold #FFB74D] "
            "Running onboarding to set up your profile...\n"
        )

    # Auto-trigger onboarding for new users
    if is_new_user:
        onboarding_msg = (
            "I'm a new user. My basic profile (name, designation, persona, timezone) "
            "is already filled in via a setup form — do NOT ask for those again. "
            "Start the onboarding skill from the agent-name step: ask me what I'd like "
            "to call you, save it with update_user_profile('agent_name', <chosen_name>), "
            "then continue with the remaining onboarding steps (skill review, approval gates, "
            "Google connect, confirmation)."
        )
        logger.info("Auto-triggering onboarding for new user: %s", user_id)
        try:
            with console.status("[bold cyan]Setting up your profile...", spinner="dots"):
                result = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": onboarding_msg}]},
                    config=run_config,
                )
            response = result["messages"][-1].content
            console.print(f"\n[bold blue]{assistant_label}:[/bold blue] {response}\n")
            # Re-read agent_name in case the onboarding flow just set it
            try:
                new_profile_path = Path(config.users.dir).resolve() / user_id / "profile.yaml"
                if new_profile_path.exists():
                    new_profile = load_yaml_dict(new_profile_path, context=f"post-onboarding profile for {user_id}")
                    new_agent_name = (new_profile.get("agent_name") or "").strip()
                    if new_agent_name:
                        assistant_label = new_agent_name
            except Exception:
                pass
        except Exception as exc:
            logger.warning("Onboarding auto-trigger failed: %s", exc)

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        logger.info("User [%s]: %s", effective_thread_id, user_input)

        try:
            with console.status("[bold cyan]Thinking...", spinner="dots"):
                result = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config=run_config,
                )

            # Handle interrupt_on: agent paused waiting for human approval
            while result.get("__interrupt__"):
                interrupt = result["__interrupt__"][0]
                tool_name = interrupt.value.get("tool_name", "unknown tool")
                tool_args = interrupt.value.get("tool_input", {})
                console.print(f"\n[bold yellow][Approval required][/bold yellow] Agent wants to call: [cyan]{tool_name}[/cyan]")
                print(f"  Arguments: {tool_args}")
                try:
                    approval = console.input("  [bold white]Approve? (y/n): [/bold white]").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    approval = "n"
                approved = approval in {"y", "yes"}
                logger.info("Interrupt approval for %s: %s", tool_name, approved)
                with console.status("[bold cyan]Executing...", spinner="dots"):
                    result = await agent.ainvoke(
                        {"resume": approved},
                        config=run_config,
                    )

            response = result["messages"][-1].content
            console.print(f"\n[bold blue]{assistant_label}:[/bold blue] {response}\n")
            logger.info("Assistant [%s]: %s", args.thread, response)
        except Exception as exc:
            logger.exception("Agent error on input: %s", user_input)
            print(f"\n[ERROR] {exc}\n", file=sys.stderr)

    from src.load_mcp import shutdown_mcp
    from src.memory import close_checkpointer

    shutdown_mcp()
    await close_checkpointer()


if __name__ == "__main__":
    asyncio.run(run())
