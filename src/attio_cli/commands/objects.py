"""Object schema commands."""

import click

from attio_cli.columns import OBJECT_COLUMNS
from attio_cli.commands.common import get_client
from attio_cli.output import output_many, output_one


@click.group()
def objects() -> None:
    """Manage objects (schema)."""


@objects.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def objects_list(as_json: bool) -> None:
    """List all objects."""
    with get_client() as client:
        response = client.get("/objects")
        output_many(response["data"], OBJECT_COLUMNS, as_json)


@objects.command("retrieve")
@click.argument("object")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def objects_retrieve(object: str, as_json: bool) -> None:
    """Retrieve object details."""
    with get_client() as client:
        response = client.get(f"/objects/{object}")
        output_one(response["data"], OBJECT_COLUMNS, as_json)
