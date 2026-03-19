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

load_dotenv()

logger = logging.getLogger(__name__)


def create_agent(config: AppConfig | None = None):
    """Create and return the Assist-AI proactive agent.

    Parameters
    ----------
    config:
        Pre-loaded AppConfig. If *None*, ``config.yaml`` in the current
        working directory is loaded automatically.

    Returns
    -------
    agent
        A compiled LangGraph agent ready to ``.invoke()`` or ``.astream()``.
    """
    if config is None:
        config = load_config()

    # ------------------------------------------------------------------
    # LLM — model-agnostic via langchain.chat_models.init_chat_model
    # Supports: openai | google_genai | anthropic
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

    # ------------------------------------------------------------------
    # Memory: persistent checkpointer + CompositeBackend
    # - SqliteSaver  → conversation history persists across restarts
    # - CompositeBackend → /memories/* and /skills/* on real disk
    # ------------------------------------------------------------------
    checkpointer = create_checkpointer()
    backend = create_backend()

    # ------------------------------------------------------------------
    # System prompt
    # ------------------------------------------------------------------
    system_prompt_parts = []

    identity_path = _PROJECT_ROOT / "memories" / "identity.md"
    if identity_path.exists():
        content = identity_path.read_text(encoding="utf-8").strip()
        if content:
            system_prompt_parts.append(content)

    agent_path = _PROJECT_ROOT / "memories" / "agent.md"
    if agent_path.exists():
        content = agent_path.read_text(encoding="utf-8").strip()
        if content:
            system_prompt_parts.append(content)

    system_prompt_path = _PROJECT_ROOT / "prompts" / "agent_system_prompt.md"
    if system_prompt_path.exists():
        content = system_prompt_path.read_text(encoding="utf-8").strip()
        if content:
            system_prompt_parts.append(content)

    system_prompt = "\n\n".join(system_prompt_parts) if system_prompt_parts else None

    # ------------------------------------------------------------------
    # Assemble agent
    # The SDK's SkillsMiddleware handles skill discovery and prompt
    # injection automatically via the skills= parameter. Skills are
    # read from the /skills/ route in the CompositeBackend.
    # ------------------------------------------------------------------
    agent = create_deep_agent(
        model=model,
        tools=tools,
        backend=backend,
        skills=["/skills/"] if config.skills.enabled else None,
        checkpointer=checkpointer,
        system_prompt=system_prompt,
    )

    logger.info(
        "Agent created | provider=%s model=%s tools=%d skills=%s",
        config.provider.name,
        config.provider.model,
        len(tools),
        "enabled" if config.skills.enabled else "disabled",
    )
    return agent
