"""Tool loading — discovers and returns all available LangChain tools."""

import logging

from .load_config import AppConfig

logger = logging.getLogger(__name__)

AVAILABLE_TOOLS: dict[str, object] = {}


def load_tools(config: AppConfig, model) -> list:
    """Load and return all available tools based on config.

    Each tool is loaded gracefully — missing API keys or packages log a warning
    and are skipped rather than crashing startup.
    """
    tools: list = []

    # Web search (Tavily)
    try:
        from tools.websearch import internet_search
        tools.append(internet_search)
        logger.info("Tool loaded: internet_search (Tavily)")
    except Exception as exc:
        logger.warning("Skipping internet_search: %s", exc)

    # Cover image generation (Google GenAI)
    try:
        from tools.content import generate_cover
        tools.append(generate_cover)
        logger.info("Tool loaded: generate_cover")
    except Exception as exc:
        logger.warning("Skipping generate_cover: %s", exc)

    # Gmail tools
    try:
        from tools.gmail import get_gmail_tools
        gmail_tools = get_gmail_tools()
        tools.extend(gmail_tools)
        logger.info("Tool loaded: Gmail toolkit (%d tools)", len(gmail_tools))
    except ImportError as exc:
        logger.warning("Skipping Gmail toolkit (not installed): %s", exc)

    # Calendar tools
    try:
        from tools.calendar_tools import get_calendar_tools
        calendar_tools = get_calendar_tools()
        tools.extend(calendar_tools)
        logger.info("Tool loaded: Calendar toolkit (%d tools)", len(calendar_tools))
    except ImportError as exc:
        logger.warning("Skipping Calendar toolkit (not installed): %s", exc)

    # Meeting tools
    try:
        from tools.meeting_tools import get_meeting_tools
        meeting_tools = get_meeting_tools()
        tools.extend(meeting_tools)
        logger.info("Tool loaded: Meeting toolkit (%d tools)", len(meeting_tools))
    except ImportError as exc:
        logger.warning("Skipping Meeting toolkit (not installed): %s", exc)

    # SQL database tools
    if config.database.url:
        try:
            from langchain_community.utilities import SQLDatabase
            from langchain_community.agent_toolkits import SQLDatabaseToolkit

            db = SQLDatabase.from_uri(config.database.url, sample_rows_in_table_info=3)
            sql_tools = SQLDatabaseToolkit(db=db, llm=model).get_tools()
            tools.extend(sql_tools)
            logger.info("Tool loaded: SQL toolkit (%d tools)", len(sql_tools))
        except Exception as exc:
            logger.warning("Skipping SQL toolkit: %s", exc)

    # MCP server tools
    if config.mcp.servers:
        from .load_mcp import load_mcp_tools
        mcp_tools = load_mcp_tools(config.mcp.servers)
        tools.extend(mcp_tools)

    # RAG tools (semantic search over company documents)
    if config.rag.enabled:
        try:
            from tools.rag import get_rag_tools
            rag_tools = get_rag_tools(config)
            tools.extend(rag_tools)
            logger.info("Tool loaded: RAG (%d tools)", len(rag_tools))
        except Exception as exc:
            logger.warning("Skipping RAG tools: %s", exc)

    # HRIS tools (leave management, employee data)
    if config.hris.enabled:
        try:
            from tools.hris import get_hris_tools
            hris_tools = get_hris_tools(config)
            tools.extend(hris_tools)
            logger.info("Tool loaded: HRIS (%d tools)", len(hris_tools))
        except Exception as exc:
            logger.warning("Skipping HRIS tools: %s", exc)

    # Agent creation tool
    try:
        from tools.agents import create_agent
        tools.append(create_agent)
        logger.info("Tool loaded: create_agent")
    except Exception as exc:
        logger.warning("Skipping create_agent: %s", exc)

    # User configuration tools (profile, skill toggling, approval gates)
    try:
        from tools.user_config import get_user_config_tools
        user_config_tools = get_user_config_tools()
        tools.extend(user_config_tools)
        logger.info("Tool loaded: user_config (%d tools)", len(user_config_tools))
    except Exception as exc:
        logger.warning("Skipping user_config tools: %s", exc)

    AVAILABLE_TOOLS.clear()
    for t in tools:
        AVAILABLE_TOOLS[t.name] = t

    return tools
