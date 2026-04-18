"""Agent factory — assembles the Proactive Assist AI agent from modular components."""

import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent, FilesystemPermission

from .load_config import AppConfig, load_config
from .memory import create_checkpointer, create_backend
from .load_tools import load_tools
from .load_agents import load_agents

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_PREFS_FILE = _PROJECT_ROOT / "memories" / "user_preferences.txt"
_PERSONAS_DIR = _PROJECT_ROOT / "prompts" / "personas"

load_dotenv()

logger = logging.getLogger(__name__)


def _resolve_interrupt_on(
    default_interrupts: list[str] | None,
    user_id: str | None = None,
) -> list[str] | None:
    """Return the active approval-gated tools for this session.

    When a user-scoped ``interrupt_on.yaml`` exists, it overrides the global
    config list. If the file is missing or invalid, fall back to the global
    ``config.agent.interrupt_on`` value.
    """
    if not user_id:
        return default_interrupts

    try:
        import yaml as _yaml

        user_interrupts_path = _PROJECT_ROOT / "workspace" / "users" / user_id / "interrupt_on.yaml"
        if not user_interrupts_path.exists():
            return default_interrupts

        with open(user_interrupts_path, encoding="utf-8") as f:
            data = _yaml.safe_load(f) or []

        if not isinstance(data, list):
            logger.warning(
                "User interrupt_on file is not a list: %s. Falling back to global config.",
                user_interrupts_path,
            )
            return default_interrupts

        interrupts = [name for name in data if isinstance(name, str) and name.strip()]
        logger.info("Loaded %d user-specific approval gates for %s", len(interrupts), user_id)
        return interrupts
    except Exception as exc:
        logger.warning("Failed to load user-specific approval gates for %s: %s", user_id, exc)
        return default_interrupts


def _build_dynamic_prompt_middleware(user_id: str | None = None):
    """Return @dynamic_prompt middlewares that inject user context on every call.

    Middleware 1 — user preferences:
        Reads user_preferences.txt (global or user-scoped) on every invocation
        so preferences written mid-session take effect immediately.

    Middleware 2 — user profile & enabled skills (only when user_id is set):
        Reads the user's profile.yaml and enabled_skills.yaml to inject
        role context and a filtered skill list into the system prompt.

    Returns a list of middleware (may be empty if dynamic_prompt is unavailable).
    """
    _users_dir = _PROJECT_ROOT / "workspace" / "users"

    try:
        from deepagents.middleware import dynamic_prompt, ModelRequest
    except Exception:
        logger.debug("dynamic_prompt unavailable — preferences will be in static system prompt")
        return []

    middlewares = []

    # Determine which preferences file to read
    if user_id:
        prefs_file = _users_dir / user_id / "memories" / "preferences.txt"
    else:
        prefs_file = _PREFS_FILE

    @dynamic_prompt
    def user_preferences(_request: ModelRequest) -> str:
        if prefs_file.exists():
            content = prefs_file.read_text(encoding="utf-8").strip()
            if content:
                return f"## User Preferences\n{content}"
        return ""

    middlewares.append(user_preferences)

    # User profile & filtered skill list injection
    if user_id:
        import yaml as _yaml

        profile_path = _users_dir / user_id / "profile.yaml"
        enabled_skills_path = _users_dir / user_id / "enabled_skills.yaml"

        @dynamic_prompt
        def user_profile_context(_request: ModelRequest) -> str:
            parts = []

            # Profile
            if profile_path.exists():
                try:
                    with open(profile_path, encoding="utf-8") as f:
                        profile = _yaml.safe_load(f) or {}
                    if profile:
                        lines = [f"- **{k}**: {v}" for k, v in profile.items() if v]
                        if lines:
                            parts.append("## Active User Profile\n" + "\n".join(lines))
                except Exception:
                    pass

            # Enabled skills filter
            if enabled_skills_path.exists():
                try:
                    with open(enabled_skills_path, encoding="utf-8") as f:
                        data = _yaml.safe_load(f) or {}
                    enabled = data.get("enabled", []) if isinstance(data, dict) else []
                    if enabled:
                        parts.append(
                            "## Enabled Skills (user filter)\n"
                            "Only route to these skills for this user:\n"
                            + "\n".join(f"- {s}" for s in enabled)
                        )
                except Exception:
                    pass

            return "\n\n".join(parts)

        middlewares.append(user_profile_context)

    return middlewares


def _build_static_system_prompt(
    include_prefs: bool = False,
    persona: str = "developer",
) -> str | None:
    """Assemble the static system prompt from identity.md + persona overlay + agent.md.

    identity.md             — who the agent is (personality, tone)
    prompts/personas/*.md   — persona-specific overlay (priorities, routing, tone)
    agent.md                — what the agent can do (capabilities, tool/skill logic)

    These are the AGENTS.md equivalent for this project: always-loaded,
    minimal, containing only what must be present on every single call.
    user_preferences.txt is only included here when dynamic_prompt is
    unavailable.
    """
    parts = []

    # 1. Core identity
    identity_path = _PROJECT_ROOT / "memories" / "identity.md"
    if identity_path.exists():
        content = identity_path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)

    # 2. Persona overlay — role-specific tone, priorities, skill routing
    persona_path = _PERSONAS_DIR / f"{persona}.md"
    if persona_path.exists():
        content = persona_path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)
    else:
        logger.warning("Persona overlay not found: %s", persona_path)

    # 3. Agent capabilities & routing
    agent_md_path = _PROJECT_ROOT / "memories" / "agent.md"
    if agent_md_path.exists():
        content = agent_md_path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)

    # Fallback: bake prefs into static prompt if dynamic_prompt isn't available
    if include_prefs and _PREFS_FILE.exists():
        prefs = _PREFS_FILE.read_text(encoding="utf-8").strip()
        if prefs:
            parts.append(f"## User Preferences\n{prefs}")

    return "\n\n".join(parts) if parts else None


def _build_filesystem_permissions() -> list[FilesystemPermission]:
    """Build declarative filesystem permission rules.

    Rules are evaluated in declaration order — first match wins.

    Policy:
      - Hard-deny writes to sensitive project files (.env, config, source code)
      - ``/memories/`` is writable (user-scoped, how the agent learns)
      - ``/skills/`` is writable but guarded by an approval prompt (see SkillWriteGuardMiddleware)
      - Everything else falls through to the default StateBackend (ephemeral)
    """
    return [
        # Hard-deny writes to sensitive project files
        FilesystemPermission(
            operations=["write","read"],
            paths=[
                "/.env",
                "/.env.*",
                "/config.yaml",
                "/config.local.yaml",
                "/main.py",
                "/requirements.txt",
                "/src/**",
                "/tools/**",
                "/creds/**",
                "/.mcp.json",
                "/.gitignore",
            ],
            mode="deny",
        ),
        # Allow writes to /memories/ (user-scoped preferences)
        FilesystemPermission(
            operations=["write"],
            paths=["/memories/**"],
            mode="allow",
        ),
        # Allow writes to /skills/ (guarded by SkillWriteGuardMiddleware below)
        FilesystemPermission(
            operations=["write"],
            paths=["/skills/**"],
            mode="allow",
        ),
    ]


def _build_skill_write_guard_middleware():
    """Middleware that pauses and asks for human approval before writing to /skills/.

    Only interrupts on write_file / edit_file tool calls whose path argument
    starts with /skills/ or skills/. All other tool calls pass through.
    """
    try:
        from langchain.agents.middleware import AgentMiddleware
        from langgraph.types import interrupt
    except Exception as exc:
        logger.warning("Skipping skill-write guard middleware: %s", exc)
        return None

    class SkillWriteGuardMiddleware(AgentMiddleware):
        """Intercepts write_file / edit_file calls targeting /skills/ and asks for approval."""

        _WRITE_TOOLS = {"write_file", "edit_file"}

        def _is_skill_path(self, path: str) -> bool:
            if not isinstance(path, str):
                return False
            p = path.lstrip("/")
            return p.startswith("skills/")

        def wrap_tool_call(self, request, handler):
            tool_name = request.tool_call.get("name", "")
            if tool_name in self._WRITE_TOOLS:
                args = request.tool_call.get("args", {}) or {}
                # write_file uses 'file_path', edit_file also uses 'file_path'
                path = args.get("file_path") or args.get("path") or ""
                if self._is_skill_path(path):
                    decision = interrupt({
                        "type": "skill_write_approval",
                        "tool_name": tool_name,
                        "path": path,
                        "message": f"Agent wants to {tool_name} on shared skill file: {path}",
                        "tool_input": args,
                    })
                    # Accept multiple resume formats: bool, {"approved": bool}, or raw truthy/falsy
                    if isinstance(decision, dict):
                        approved = decision.get("approved", True)
                    else:
                        approved = bool(decision)
                    if not approved:
                        from langchain_core.messages import ToolMessage
                        return ToolMessage(
                            content=f"Skill write denied by user: {path}",
                            tool_call_id=request.tool_call.get("id", ""),
                        )
            return handler(request)

        async def awrap_tool_call(self, request, handler):
            tool_name = request.tool_call.get("name", "")
            if tool_name in self._WRITE_TOOLS:
                args = request.tool_call.get("args", {}) or {}
                path = args.get("file_path") or args.get("path") or ""
                if self._is_skill_path(path):
                    decision = interrupt({
                        "type": "skill_write_approval",
                        "tool_name": tool_name,
                        "path": path,
                        "message": f"Agent wants to {tool_name} on shared skill file: {path}",
                        "tool_input": args,
                    })
                    # Accept multiple resume formats: bool, {"approved": bool}, or raw truthy/falsy
                    if isinstance(decision, dict):
                        approved = decision.get("approved", True)
                    else:
                        approved = bool(decision)
                    if not approved:
                        from langchain_core.messages import ToolMessage
                        return ToolMessage(
                            content=f"Skill write denied by user: {path}",
                            tool_call_id=request.tool_call.get("id", ""),
                        )
            return await handler(request)

    return SkillWriteGuardMiddleware()


async def create_agent(config: AppConfig | None = None, user_id: str | None = None):
    """Create and return the Assist-AI proactive agent.

    Parameters
    ----------
    config:
        Pre-loaded AppConfig. If *None*, ``config.yaml`` in the current
        working directory is loaded automatically.
    user_id:
        Optional user identifier. When provided, memory is scoped to the
        user's profile directory and per-user skill/tool filtering is enabled.

    Returns
    -------
    agent
        A compiled LangGraph agent ready to ``.ainvoke()`` or ``.astream()``.
    """
    if config is None:
        config = load_config()

    # Set the active user for user-scoped tools
    if user_id:
        try:
            from tools.user_config import set_active_user as set_config_user, get_user_dir
            set_config_user(user_id)
            get_user_dir(user_id, persona=config.persona.active)  # ensure profile directory exists
        except Exception as exc:
            logger.warning("Failed to set active user (user_config): %s", exc)
        try:
            from tools.agents import set_active_user as set_agents_user
            set_agents_user(user_id)
        except Exception as exc:
            logger.warning("Failed to set active user (agents): %s", exc)
        try:
            from tools.google_auth import set_active_user as set_google_auth_user
            set_google_auth_user(user_id)
        except Exception as exc:
            logger.warning("Failed to set active user (google_auth): %s", exc)
        logger.info("Active user: %s", user_id)

    # ------------------------------------------------------------------
    # LLM — model-agnostic via langchain.chat_models.init_chat_model
    # ------------------------------------------------------------------
    model_kwargs: dict = {}
    if config.provider.temperature is not None:
        model_kwargs["temperature"] = config.provider.temperature
    if config.provider.max_tokens is not None:
        model_kwargs["max_tokens"] = config.provider.max_tokens
    if config.provider.base_url:
        model_kwargs["base_url"] = config.provider.base_url

    model = init_chat_model(
        f"{config.provider.name}:{config.provider.model}",
        **model_kwargs,
    )
    logger.info("LLM provider: %s / %s", config.provider.name, config.provider.model)

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------
    tools = load_tools(config, model, user_id=user_id)
    logger.info("Tools loaded: %d", len(tools))

    # ------------------------------------------------------------------
    # Memory: async checkpointer + CompositeBackend
    #
    # Checkpointer (AsyncSqliteSaver):
    #   Persists conversation history per thread_id across restarts.
    #
    # Backend (CompositeBackend):
    #   /memories/ → FilesystemBackend (real disk, survives restarts)
    #   /skills/   → FilesystemBackend (real disk, read-only skill discovery)
    #   everything → StateBackend (ephemeral scratch space per session)
    #
    # NOTE: The deepagents docs recommend StoreBackend + InMemoryStore for
    # /memories/ when deploying to LangSmith (store is auto-provisioned there).
    # For local use, FilesystemBackend is equivalent and more persistent
    # (no dependency on a running Postgres/Redis instance).
    # store= is passed as None here; swap in InMemoryStore() or PostgresStore()
    # if switching /memories/ to StoreBackend for LangSmith deployment.
    # ------------------------------------------------------------------
    checkpointer = await create_checkpointer()
    backend = create_backend(user_id=user_id)

    # ------------------------------------------------------------------
    # Context Engineering
    #
    # Static context (loaded once, present on every call):
    #   identity.md + agent.md → always-loaded personality & capability
    #   instructions (AGENTS.md equivalent)
    #
    # Dynamic context (re-evaluated on every invocation):
    #   user_preferences.txt → injected fresh via @dynamic_prompt so
    #   preferences written mid-session take effect immediately.
    #   Falls back to static injection if dynamic_prompt is unavailable.
    #
    # Runtime context (passed at invoke time, NOT auto-shown to model):
    #   thread_id, timezone → read by tools/middleware that need them.
    # ------------------------------------------------------------------
    dynamic_middlewares = _build_dynamic_prompt_middleware(user_id=user_id)
    system_prompt = _build_static_system_prompt(
        include_prefs=len(dynamic_middlewares) == 0,
        persona=config.persona.active,
    )

    middleware = list(dynamic_middlewares)

    # ------------------------------------------------------------------
    # Summarization tool middleware — lets the agent proactively compact
    # context at natural breakpoints (end of a skill workflow) instead of
    # waiting for the automatic 85%-context trigger.
    # The auto-summarizer at 85% still runs — this adds a tool the agent
    # can call voluntarily.
    # ------------------------------------------------------------------
    try:
        from deepagents.middleware.summarization import create_summarization_tool_middleware
        summarization_mw = create_summarization_tool_middleware(model, backend)
        middleware.append(summarization_mw)
        logger.info("Summarization tool middleware enabled")
    except Exception as exc:
        logger.warning("Skipping summarization tool middleware: %s", exc)

    # ------------------------------------------------------------------
    # Skill-write guard — pauses and asks for human approval before
    # writing to /skills/ (shared skill files).  Per-path interrupt that
    # doesn't block unrelated writes.
    # ------------------------------------------------------------------
    skill_guard = _build_skill_write_guard_middleware()
    if skill_guard is not None:
        middleware.append(skill_guard)
        logger.info("Skill-write guard middleware enabled")

    # ------------------------------------------------------------------
    # Subagents — auto-discovered from agents/*/agent.yaml
    # ------------------------------------------------------------------
    subagents = load_agents(_PROJECT_ROOT, tools, persona=config.persona.active, user_id=user_id)
    if subagents:
        logger.info("Subagents loaded: %d", len(subagents))

    # ------------------------------------------------------------------
    # Agent assembly
    # ------------------------------------------------------------------
    active_interrupts = _resolve_interrupt_on(config.agent.interrupt_on, user_id=user_id)

    agent_kwargs: dict = dict(
        model=model,
        tools=tools,
        backend=backend,
        skills=["/skills/"] if config.skills.enabled else None,
        subagents=subagents if subagents else None,
        checkpointer=checkpointer,
        system_prompt=system_prompt,
        middleware=middleware,
        interrupt_on={name: {} for name in active_interrupts} if active_interrupts else None,
        permissions=_build_filesystem_permissions(),
    )
    agent = create_deep_agent(**agent_kwargs)

    logger.info(
        "Agent created | provider=%s model=%s tools=%d skills=%s persona=%s user=%s interrupt_on=%s",
        config.provider.name,
        config.provider.model,
        len(tools),
        "enabled" if config.skills.enabled else "disabled",
        config.persona.active,
        user_id or "global",
        active_interrupts,
    )
    return agent
