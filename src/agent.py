"""Agent factory — assembles the Proactive Assist AI agent from modular components."""

import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

from .load_config import AppConfig, load_config
from .memory import create_checkpointer, create_backend
from .load_tools import load_tools

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_PREFS_FILE = _PROJECT_ROOT / "memories" / "user_preferences.txt"

load_dotenv()

logger = logging.getLogger(__name__)


def _build_dynamic_prompt_middleware():
    """Return a @dynamic_prompt middleware that injects user preferences on every call.

    Uses deepagents' dynamic_prompt decorator so the agent sees the *current*
    contents of user_preferences.txt on every invocation — not a snapshot from
    startup.  If the decorator is unavailable (older SDK version), falls back to
    None and preferences are baked into the static system prompt instead.
    """
    try:
        from deepagents.middleware import dynamic_prompt, ModelRequest

        @dynamic_prompt
        def user_preferences(_request: ModelRequest) -> str:
            if _PREFS_FILE.exists():
                content = _PREFS_FILE.read_text(encoding="utf-8").strip()
                if content:
                    return f"## User Preferences\n{content}"
            return ""

        return user_preferences
    except Exception:
        logger.debug("dynamic_prompt unavailable — preferences will be in static system prompt")
        return None


def _build_static_system_prompt(include_prefs: bool = False) -> str | None:
    """Assemble the static system prompt from identity.md + agent.md.

    identity.md  — who the agent is (personality, tone)
    agent.md     — what the agent can do (capabilities, tool/skill logic)

    These are the AGENTS.md equivalent for this project: always-loaded,
    minimal, containing only what must be present on every single call.
    user_preferences.txt is only included here when dynamic_prompt is
    unavailable.
    """
    parts = []

    for path in [
        _PROJECT_ROOT / "memories" / "identity.md",
        _PROJECT_ROOT / "memories" / "agent.md",
    #    _PROJECT_ROOT / "prompts" / "agent_system_prompt.md",
    ]:
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                parts.append(content)

    # Fallback: bake prefs into static prompt if dynamic_prompt isn't available
    if include_prefs and _PREFS_FILE.exists():
        prefs = _PREFS_FILE.read_text(encoding="utf-8").strip()
        if prefs:
            parts.append(f"## User Preferences\n{prefs}")

    return "\n\n".join(parts) if parts else None


async def create_agent(config: AppConfig | None = None):
    """Create and return the Assist-AI proactive agent.

    Parameters
    ----------
    config:
        Pre-loaded AppConfig. If *None*, ``config.yaml`` in the current
        working directory is loaded automatically.

    Returns
    -------
    agent
        A compiled LangGraph agent ready to ``.ainvoke()`` or ``.astream()``.
    """
    if config is None:
        config = load_config()

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
    tools = load_tools(config, model)
    logger.info("Tools loaded: %d", len(tools))

    # ------------------------------------------------------------------
    # Memory: async checkpointer + CompositeBackend
    # - AsyncSqliteSaver → conversation history persists across restarts
    # - CompositeBackend → /memories/* and /skills/* on real disk
    # ------------------------------------------------------------------
    checkpointer = await create_checkpointer()
    backend = create_backend()

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
    dynamic_prefs = _build_dynamic_prompt_middleware()
    system_prompt = _build_static_system_prompt(include_prefs=dynamic_prefs is None)

    middleware = [dynamic_prefs] if dynamic_prefs is not None else []

    # ------------------------------------------------------------------
    # Agent assembly
    # ------------------------------------------------------------------
    agent_kwargs: dict = dict(
        model=model,
        tools=tools,
        backend=backend,
        skills=["/skills/"] if config.skills.enabled else None,
        checkpointer=checkpointer,
        system_prompt=system_prompt,
        middleware=middleware,
        interrupt_on={name: {} for name in config.agent.interrupt_on} if config.agent.interrupt_on else None,
    )
    agent = create_deep_agent(**agent_kwargs)

    logger.info(
        "Agent created | provider=%s model=%s tools=%d skills=%s interrupt_on=%s",
        config.provider.name,
        config.provider.model,
        len(tools),
        "enabled" if config.skills.enabled else "disabled",
        config.agent.interrupt_on,
    )
    return agent
