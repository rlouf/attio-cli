"""Shared helpers for command modules."""

import click

from attio_cli.client import AUTH_SETUP_HINT, AttioClient
from attio_cli.config import get_api_key


def get_client() -> AttioClient:
    """Get an authenticated API client."""
    api_key = get_api_key()
    if not api_key:
        raise click.ClickException(f"No API key configured. {AUTH_SETUP_HINT}")
    return AttioClient(api_key)


def attribute_path(target: str, identifier: str, suffix: str = "") -> str:
    """Build an attributes API path for objects or lists."""
    base = f"/{target}/{identifier}/attributes"
    return f"{base}{suffix}"
