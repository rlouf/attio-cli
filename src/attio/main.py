"""Main CLI entry point."""

import click

from attio import __version__
from attio.cli_core import CLI_CONTEXT_SETTINGS, AttioGroup, show_llm_guide
from attio.client import AUTH_SETUP_HINT, AttioClient
from attio.columns import IDENTITY_COLUMNS
from attio.commands.attributes import attributes
from attio.commands.config import config
from attio.commands.entries import entries
from attio.commands.lists import lists
from attio.commands.members import members
from attio.commands.notes import notes
from attio.commands.objects import objects
from attio.commands.records import records
from attio.commands.tasks import tasks
from attio.commands.webhooks import webhooks
from attio.config import get_api_key
from attio.output import output_one


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
