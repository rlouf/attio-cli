"""Configuration management for Attio CLI."""

import importlib
import importlib.util
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

keyring: Any = (
    importlib.import_module("keyring") if importlib.util.find_spec("keyring") is not None else None
)

KEYRING_SERVICE = "attio"
KEYRING_USERNAME = "default"
AUTH_SOURCE_ENV = "environment variable"
AUTH_SOURCE_KEYCHAIN = "system keychain"
AUTH_SOURCE_CONFIG = "config file"
AUTH_SOURCE_NONE = "not set"


@dataclass
class AuthState:
    """Resolved authentication state for the CLI."""

    api_key: str | None
    source: str
    preferred_storage: str
    config_path: Path


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


def _remove_api_key_from_config() -> bool:
    """Remove the API key from the config file if present."""
    config = load_config()
    if "api_key" not in config:
        return False
    del config["api_key"]
    save_config(config)
    return True


def is_keyring_available() -> bool:
    """Return whether system keychain support is available."""
    if keyring is None:
        return False
    try:
        keyring.get_password(KEYRING_SERVICE, "__attio_probe__")
    except Exception:
        return False
    return True


def _get_keyring_api_key() -> Optional[str]:
    """Read the API key from the system keychain if available."""
    if not is_keyring_available():
        return None
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except Exception:
        return None


def _set_keyring_api_key(api_key: str) -> bool:
    """Save the API key to the system keychain if available."""
    if not is_keyring_available():
        return False
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
    except Exception:
        return False
    return True


def _delete_keyring_api_key() -> bool:
    """Delete the API key from the system keychain if present."""
    if not is_keyring_available():
        return False
    try:
        existing = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if not existing:
            return False
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except Exception:
        return False
    return True


def get_preferred_storage() -> str:
    """Return the preferred local storage backend for saved credentials."""
    if is_keyring_available():
        return AUTH_SOURCE_KEYCHAIN
    return AUTH_SOURCE_CONFIG


def resolve_auth_state() -> AuthState:
    """Resolve the active API key and where it came from."""
    env_api_key = os.environ.get("ATTIO_API_KEY")
    if env_api_key:
        return AuthState(
            api_key=env_api_key,
            source=AUTH_SOURCE_ENV,
            preferred_storage=get_preferred_storage(),
            config_path=get_config_path(),
        )

    keyring_api_key = _get_keyring_api_key()
    if keyring_api_key:
        return AuthState(
            api_key=keyring_api_key,
            source=AUTH_SOURCE_KEYCHAIN,
            preferred_storage=get_preferred_storage(),
            config_path=get_config_path(),
        )

    config_api_key = load_config().get("api_key")
    if config_api_key:
        return AuthState(
            api_key=config_api_key,
            source=AUTH_SOURCE_CONFIG,
            preferred_storage=get_preferred_storage(),
            config_path=get_config_path(),
        )

    return AuthState(
        api_key=None,
        source=AUTH_SOURCE_NONE,
        preferred_storage=get_preferred_storage(),
        config_path=get_config_path(),
    )


def get_api_key() -> Optional[str]:
    """Get the API key from environment, keychain, or config file."""
    return resolve_auth_state().api_key


def set_api_key(api_key: str) -> str:
    """Save the API key to the preferred local storage backend."""
    if _set_keyring_api_key(api_key):
        _remove_api_key_from_config()
        return AUTH_SOURCE_KEYCHAIN

    config = load_config()
    config["api_key"] = api_key
    save_config(config)
    return AUTH_SOURCE_CONFIG


def delete_api_key() -> list[str]:
    """Delete saved API keys from local storage backends."""
    removed = []
    if _delete_keyring_api_key():
        removed.append(AUTH_SOURCE_KEYCHAIN)
    if _remove_api_key_from_config():
        removed.append(AUTH_SOURCE_CONFIG)
    return removed
