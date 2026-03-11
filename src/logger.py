"""Logging setup — per-session file logging (no console output)."""

import logging
from datetime import datetime
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LOGS_DIR = _PROJECT_ROOT / "logs"


def setup_logging(level: str = "INFO") -> Path:
    """Configure root logger with a session file handler only.

    Creates a new log file for each session named:
        logs/session_YYYYMMDD_HHMMSS.log

    Parameters
    ----------
    level:
        Logging level string (DEBUG | INFO | WARNING | ERROR).

    Returns
    -------
    Path
        The path of the log file created for this session.
    """
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = _LOGS_DIR / f"session_{session_time}.log"

    # Format: timestamp | level | module | message
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove any existing handlers to avoid duplicate output
    root.handlers.clear()

    # File handler only — no console output
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    return log_file
