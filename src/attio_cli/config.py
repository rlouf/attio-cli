"""Configuration management for Attio CLI."""

import json
import os
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Get the configuration directory."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # Unix-like
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "attio"


def get_config_path() -> Path:
    """Get the path to the config file."""
    return get_config_dir() / "config.json"


def load_config() -> dict:
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    """Save configuration to file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> Optional[str]:
    """Get API key from environment or config file."""
    # Environment variable takes precedence
    api_key = os.environ.get("ATTIO_API_KEY")
    if api_key:
        return api_key

    # Fall back to config file
    config = load_config()
    return config.get("api_key")


def set_api_key(api_key: str) -> None:
    """Save API key to config file."""
    config = load_config()
    config["api_key"] = api_key
    save_config(config)
