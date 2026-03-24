"""MCP tool loading — connects to MCP servers and returns LangChain-compatible tools.

Supports both transport types:
  - stdio: spawns a local process (e.g. npx @modelcontextprotocol/server-filesystem)
  - sse:   connects to a running HTTP MCP server

A background thread keeps a persistent asyncio event loop alive so that
stdio subprocess connections are not torn down between agent calls.
"""

import asyncio
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level state — keep the client and loop alive for the process lifetime
_mcp_client = None
_bg_loop: Optional[asyncio.AbstractEventLoop] = None
_bg_thread: Optional[threading.Thread] = None


def _ensure_background_loop() -> asyncio.AbstractEventLoop:
    """Start a background event loop thread if one isn't running yet."""
    global _bg_loop, _bg_thread

    if _bg_loop is not None and _bg_loop.is_running():
        return _bg_loop

    _bg_loop = asyncio.new_event_loop()
    _bg_thread = threading.Thread(
        target=_bg_loop.run_forever,
        name="mcp-event-loop",
        daemon=True,  # dies with the main process
    )
    _bg_thread.start()
    return _bg_loop


def load_mcp_tools(servers: dict) -> list:
    """Connect to configured MCP servers and return their tools as LangChain tools.

    Parameters
    ----------
    servers:
        Dict of server name → MCPServerConfig (from AppConfig.mcp.servers).

    Returns
    -------
    list
        LangChain-compatible tools from all connected servers.
        Returns [] on any failure (graceful degradation).
    """
    if not servers:
        return []

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        logger.warning(
            "Skipping MCP servers: langchain-mcp-adapters not installed. "
            "Run: pip install langchain-mcp-adapters"
        )
        return []

    # Build the dict that MultiServerMCPClient expects
    client_config: dict = {}
    for name, cfg in servers.items():
        if cfg.transport == "sse":
            if not cfg.url:
                logger.warning("MCP server '%s' has transport=sse but no url — skipping", name)
                continue
            client_config[name] = {"url": cfg.url, "transport": "sse"}
        else:  # stdio
            if not cfg.command:
                logger.warning("MCP server '%s' has transport=stdio but no command — skipping", name)
                continue
            entry = {"command": cfg.command, "args": cfg.args, "transport": "stdio"}
            if cfg.env:
                entry["env"] = cfg.env
            client_config[name] = entry

    if not client_config:
        return []

    loop = _ensure_background_loop()

    async def _init():
        global _mcp_client
        _mcp_client = MultiServerMCPClient(client_config)
        return await _mcp_client.get_tools()

    try:
        future = asyncio.run_coroutine_threadsafe(_init(), loop)
        tools = future.result(timeout=30)
        logger.info(
            "MCP tools loaded: %d tool(s) from %d server(s): %s",
            len(tools),
            len(client_config),
            list(client_config.keys()),
        )
        return tools
    except TimeoutError:
        logger.warning("MCP server connection timed out after 30s — skipping")
        return []
    except Exception as exc:
        logger.warning("Skipping MCP servers: %s", exc)
        return []
