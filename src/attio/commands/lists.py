"""List commands."""

import click

from attio.columns import LIST_COLUMNS
from attio.commands.common import get_client
from attio.output import get_json_input, output_many, output_one


@click.group()
def lists() -> None:
    """Manage lists (pipelines, workflows)."""


@lists.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def lists_list(as_json: bool) -> None:
    """List all lists."""
    with get_client() as client:
        response = client.get("/lists")
        output_many(response["data"], LIST_COLUMNS, as_json)


@lists.command("retrieve")
@click.argument("list_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def lists_retrieve(list_id: str, as_json: bool) -> None:
    """Retrieve list details."""
    with get_client() as client:
        response = client.get(f"/lists/{list_id}")
        output_one(response["data"], LIST_COLUMNS, as_json)


@lists.command("update")
@click.argument("list_id")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="List update payload as JSON")
@click.option("--data-file", help="Read list update JSON from file or '-' for stdin")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def lists_update(list_id: str, data: str, data_json: str, data_file: str, as_json: bool) -> None:
    """Update a list."""
    payload = get_json_input(
        data,
        data=data_json,
        data_file=data_file,
        context="list update JSON",
    )
    with get_client() as client:
        response = client.patch(f"/lists/{list_id}", {"data": payload})
        output_one(response["data"], LIST_COLUMNS, as_json)
