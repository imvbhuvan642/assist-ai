"""Tool loading — discovers and returns all available LangChain tools."""

import logging

from .load_config import AppConfig

logger = logging.getLogger(__name__)


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

    return tools
