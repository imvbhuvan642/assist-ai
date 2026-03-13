"""Configuration management — loads config.yaml and validates with Pydantic."""

import os
import re
import yaml
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Config models
# ---------------------------------------------------------------------------

class AgentConfig(BaseModel):
    data_dir: str = "./data"
    max_iterations: int = 42


class ProviderConfig(BaseModel):
    name: Literal["openai", "google_genai", "anthropic", "groq"]
    model: str
    temperature: Optional[float] = 0.5
    max_tokens: Optional[int] = 8192
    base_url: Optional[str] = None

    @field_validator("temperature")
    @classmethod
    def clamp_temperature(cls, v):
        if v is not None and not (0.0 <= v <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v

    @field_validator("base_url", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        return None if v == "" else v


class DatabaseConfig(BaseModel):
    url: Optional[str] = None


class SkillsConfig(BaseModel):
    enabled: bool = True


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


class AppConfig(BaseModel):
    agent: AgentConfig = AgentConfig()
    provider: ProviderConfig
    database: DatabaseConfig = DatabaseConfig()
    skills: SkillsConfig = SkillsConfig()
    logging: LoggingConfig = LoggingConfig()


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def _expand_env_vars(obj):
    """Recursively replace ${VAR} placeholders with environment variable values."""
    if isinstance(obj, str):
        return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_vars(i) for i in obj]
    return obj


def load_config(path: str = "config.yaml") -> AppConfig:
    """Load and validate configuration from a YAML file.

    Supports ${ENV_VAR} substitution throughout.
    If a config.local.yaml exists alongside, it is deep-merged on top.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path.resolve()}")

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    # Optional local override (gitignored)
    local_path = config_path.parent / (config_path.stem + ".local.yaml")
    if local_path.exists():
        with open(local_path) as f:
            local_data = yaml.safe_load(f) or {}
        data = _deep_merge(data, local_data)

    data = _expand_env_vars(data)
    return AppConfig(**data)


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result
