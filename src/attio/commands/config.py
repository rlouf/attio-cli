"""Config command group."""

import click

from attio.config import (
    AUTH_SOURCE_CONFIG,
    AUTH_SOURCE_ENV,
    delete_api_key,
    resolve_auth_state,
    set_api_key,
)


@click.group()
def config() -> None:
    """Manage configuration."""


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    auth_state = resolve_auth_state()
    click.echo(f"Config file: {auth_state.config_path}")
    click.echo(f"Auth source: {auth_state.source}")
    click.echo(f"Preferred local storage: {auth_state.preferred_storage}")
    if auth_state.api_key:
        masked = auth_state.api_key[:8] + "..." + auth_state.api_key[-4:]
        click.echo(f"API key: {masked}")
    else:
        click.echo("API key: (not set)")


def _save_api_key_and_echo(api_key: str) -> None:
    """Persist an API key and explain where it was saved."""
    storage = set_api_key(api_key)
    if storage == AUTH_SOURCE_CONFIG:
        click.echo("API key saved to config file because system keychain storage is unavailable.")
        return
    click.echo("API key saved to system keychain.")


@config.command("login")
@click.argument("api_key", required=False)
def config_login(api_key: str | None) -> None:
    """Save an API key for local CLI usage."""
    if not api_key:
        api_key = click.prompt("Attio API key", hide_input=True)
    _save_api_key_and_echo(api_key)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value."""
    if key == "api-key":
        _save_api_key_and_echo(value)
    else:
        raise click.ClickException(f"Unknown config key: {key}")


@config.command("logout")
def config_logout() -> None:
    """Remove locally saved API credentials."""
    removed_sources = delete_api_key()
    if not removed_sources:
        click.echo("No saved API key found.")
    elif len(removed_sources) == 1:
        click.echo(f"Removed saved API key from {removed_sources[0]}.")
    else:
        joined = " and ".join(removed_sources)
        click.echo(f"Removed saved API key from {joined}.")

    if resolve_auth_state().source == AUTH_SOURCE_ENV:
        click.echo("ATTIO_API_KEY is still set in the environment and will continue to be used.")
