"""Shared YAML loading helpers with consistent fallback behavior."""

from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import TypeVar

import yaml

logger = logging.getLogger(__name__)

T = TypeVar("T")


def load_yaml_file(path: Path, default: T, *, context: str | None = None) -> T:
    """Load YAML from disk and fall back to a copy of ``default`` on failure."""
    label = context or str(path)

    if not path.exists():
        return copy.deepcopy(default)

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        logger.warning("Failed to read YAML for %s: %s", label, exc)
        return copy.deepcopy(default)

    if data is None:
        return copy.deepcopy(default)

    return data


def load_yaml_dict(path: Path, *, context: str | None = None) -> dict:
    """Load a YAML mapping from disk or return an empty dict."""
    label = context or str(path)
    data = load_yaml_file(path, {}, context=label)
    if isinstance(data, dict):
        return data

    logger.warning("Expected YAML mapping for %s, got %s", label, type(data).__name__)
    return {}


def load_yaml_list(path: Path, *, context: str | None = None) -> list:
    """Load a YAML sequence from disk or return an empty list."""
    label = context or str(path)
    data = load_yaml_file(path, [], context=label)
    if isinstance(data, list):
        return data

    logger.warning("Expected YAML list for %s, got %s", label, type(data).__name__)
    return []
