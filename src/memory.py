"""Memory backends — persistent checkpointer and CompositeBackend factory."""

import logging
from pathlib import Path

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

logger = logging.getLogger(__name__)

# Project root = parent of the src/ directory this file lives in.
# Using an absolute path avoids CWD-relative resolution issues in Jupyter.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MEMORIES_DIR = _PROJECT_ROOT / "memories"
_SKILLS_DIR = _PROJECT_ROOT / "skills"
_DATA_DIR = _PROJECT_ROOT / "data"
_USERS_DIR = _PROJECT_ROOT / "workspace" / "users"


async def create_checkpointer(db_path: str | Path | None = None) -> AsyncSqliteSaver:
    """Return an AsyncSqliteSaver checkpointer that persists conversation threads to disk.

    Uses aiosqlite for fully async I/O — required when the agent is invoked via ainvoke.
    """
    path = Path(db_path) if db_path else _DATA_DIR / "checkpoints.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(path))
    return AsyncSqliteSaver(conn)


def create_backend(memories_dir: str | Path | None = None, user_id: str | None = None):
    """Return a CompositeBackend factory that routes /memories/* and /skills/* to real disk.

    - /memories/ → FilesystemBackend (writes to `memories_dir` on actual disk, persistent)
    - /skills/   → FilesystemBackend (read-only access to skills directory on disk)
    - everything else → StateBackend (ephemeral working files per session)

    When ``user_id`` is provided, /memories/ is scoped to the user's profile directory
    (``workspace/users/{user_id}/memories/``) for per-user memory isolation.

    Uses an absolute path derived from this file's location so it works regardless
    of what directory the Jupyter kernel is started from.
    """
    # Determine the memories directory — user-scoped if user_id provided
    if user_id:
        user_memories = _USERS_DIR / user_id / "memories"
        user_memories.mkdir(parents=True, exist_ok=True)
        resolved = user_memories.resolve()
        logger.info("Memory scoped to user: %s → %s", user_id, resolved)
    elif memories_dir:
        resolved = Path(memories_dir).resolve()
    else:
        resolved = _MEMORIES_DIR
    resolved.mkdir(parents=True, exist_ok=True)

    skills_resolved = _SKILLS_DIR.resolve()
    skills_resolved.mkdir(parents=True, exist_ok=True)

    def _backend(rt):
        return CompositeBackend(
            default=StateBackend(rt),
            # virtual_mode=True: treats incoming paths as virtual paths anchored to
            # root_dir. Without this, "/user_preferences.txt" is treated as an
            # absolute system path (C:\user_preferences.txt) and fails with a
            # permission error.
            routes={
                "/memories/": FilesystemBackend(root_dir=str(resolved), virtual_mode=True),
                "/skills/": FilesystemBackend(root_dir=str(skills_resolved), virtual_mode=True),
            },
        )

    return _backend
