"""Memory backends — persistent checkpointer and CompositeBackend factory."""

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

# Project root = parent of the src/ directory this file lives in.
# Using an absolute path avoids CWD-relative resolution issues in Jupyter.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MEMORIES_DIR = _PROJECT_ROOT / "memories"
_DATA_DIR = _PROJECT_ROOT / "data"


def create_checkpointer(db_path: str | Path | None = None) -> SqliteSaver:
    """Return a SqliteSaver checkpointer that persists conversation threads to disk.

    SqliteSaver.from_conn_string() returns a context manager — to get a plain
    checkpointer instance, open the connection manually and pass it directly.
    check_same_thread=False is required for Jupyter/async usage.
    """
    path = Path(db_path) if db_path else _DATA_DIR / "checkpoints.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    return SqliteSaver(conn)


def create_backend(memories_dir: str | Path | None = None):
    """Return a CompositeBackend factory that routes /memories/* to real disk.

    - /memories/ → FilesystemBackend (writes to `memories_dir` on actual disk, persistent)
    - everything else → StateBackend (ephemeral working files per session)

    Uses an absolute path derived from this file's location so it works regardless
    of what directory the Jupyter kernel is started from.
    """
    resolved = Path(memories_dir).resolve() if memories_dir else _MEMORIES_DIR
    resolved.mkdir(parents=True, exist_ok=True)

    def _backend(rt):
        return CompositeBackend(
            default=StateBackend(rt),
            # virtual_mode=True: treats incoming paths as virtual paths anchored to
            # root_dir. Without this, "/user_preferences.txt" is treated as an
            # absolute system path (C:\user_preferences.txt) and fails with a
            # permission error.
            routes={"/memories/": FilesystemBackend(root_dir=str(resolved), virtual_mode=True)},
        )

    return _backend
