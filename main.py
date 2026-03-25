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

from src.load_config import load_config
from src.logger import setup_logging
from src.agent import create_agent

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

    print("\n╔══════════════════════════════════════╗")
    print("║         Assist AI — Terminal         ║")
    print("╚══════════════════════════════════════╝")
    print(f"  Thread : {args.thread}")
    print(f"  Log    : {log_file}")
    print("  Type 'exit' or 'quit' to end.\n")

    try:
        config = load_config(args.config)
        print(f"  Model  : {config.provider.name} / {config.provider.model}\n")
    except Exception as exc:
        print(f"[ERROR] Failed to load config: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        print("Loading agent...", flush=True)
        agent = await create_agent(config)
        print("Agent ready.\n")
    except Exception as exc:
        logger.exception("Failed to create agent")
        print(f"[ERROR] Failed to create agent: {exc}", file=sys.stderr)
        sys.exit(1)

    run_config: dict = {"configurable": {
        "thread_id": args.thread,
        "timezone": config.agent.timezone,
    }}

    if config.langfuse.enabled:
        try:
            from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
            langfuse_handler = LangfuseCallbackHandler()
            run_config["callbacks"] = [langfuse_handler]
            logger.info("Langfuse tracing enabled (session_id=%s)", args.thread)
            print("  Tracing: Langfuse enabled\n")
        except ImportError:
            logger.warning("Langfuse enabled in config but 'langfuse' package not installed — skipping")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        logger.info("User [%s]: %s", args.thread, user_input)

        try:
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=run_config,
            )

            # Handle interrupt_on: agent paused waiting for human approval
            while result.get("__interrupt__"):
                interrupt = result["__interrupt__"][0]
                tool_name = interrupt.value.get("tool_name", "unknown tool")
                tool_args = interrupt.value.get("tool_input", {})
                print(f"\n[Approval required] Agent wants to call: {tool_name}")
                print(f"  Arguments: {tool_args}")
                try:
                    approval = input("  Approve? (y/n): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    approval = "n"
                approved = approval in {"y", "yes"}
                logger.info("Interrupt approval for %s: %s", tool_name, approved)
                result = await agent.ainvoke(
                    {"resume": approved},
                    config=run_config,
                )

            response = result["messages"][-1].content
            print(f"\nAssistant: {response}\n")
            logger.info("Assistant [%s]: %s", args.thread, response)
        except Exception as exc:
            logger.exception("Agent error on input: %s", user_input)
            print(f"\n[ERROR] {exc}\n", file=sys.stderr)

    from src.load_mcp import shutdown_mcp
    shutdown_mcp()


if __name__ == "__main__":
    asyncio.run(run())
    # Force-exit: asyncio.run() hangs during cleanup because background threads
    # (MCP stdio subprocesses, aiosqlite) keep the event loop from closing cleanly.
    # os._exit() bypasses Python's cleanup and immediately terminates the process.
    import os
    os._exit(0)
