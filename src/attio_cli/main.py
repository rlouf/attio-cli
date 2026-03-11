"""Main CLI entry point."""

import click

from attio_cli import __version__
from attio_cli.cli_core import CLI_CONTEXT_SETTINGS, AttioGroup, show_llm_guide
from attio_cli.client import AUTH_SETUP_HINT, AttioClient
from attio_cli.columns import IDENTITY_COLUMNS
from attio_cli.commands.attributes import attributes
from attio_cli.commands.config import config
from attio_cli.commands.entries import entries
from attio_cli.commands.lists import lists
from attio_cli.commands.members import members
from attio_cli.commands.notes import notes
from attio_cli.commands.objects import objects
from attio_cli.commands.records import records
from attio_cli.commands.tasks import tasks
from attio_cli.commands.webhooks import webhooks
from attio_cli.config import get_api_key
from attio_cli.output import output_one


def get_client() -> AttioClient:
    """Get an authenticated API client."""
    api_key = get_api_key()
    if not api_key:
        raise click.ClickException(f"No API key configured. {AUTH_SETUP_HINT}")
    return AttioClient(api_key)


@click.group(cls=AttioGroup, context_settings=CLI_CONTEXT_SETTINGS)
@click.option(
    "--llm",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=show_llm_guide,
    help="Print a machine-oriented usage guide and exit.",
)
@click.version_option(version=__version__)
def cli() -> None:
    """CLI for interacting with Attio CRM API."""


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def whoami(as_json: bool) -> None:
    """Show current workspace and authentication info."""
    with get_client() as client:
        response = client.get("/self")
        output_one(response["data"], IDENTITY_COLUMNS, as_json)


cli.add_command(config)
cli.add_command(objects)
cli.add_command(records)
cli.add_command(lists)
cli.add_command(entries)
cli.add_command(tasks)
cli.add_command(notes)
cli.add_command(attributes)
cli.add_command(members)
cli.add_command(webhooks)


if __name__ == "__main__":
    cli()
