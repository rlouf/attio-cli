"""Workspace member commands."""

import click

from attio_cli.columns import MEMBER_COLUMNS
from attio_cli.commands.common import get_client
from attio_cli.output import output_many, output_one


@click.group()
def members() -> None:
    """Manage workspace members."""


@members.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def members_list(as_json: bool) -> None:
    """List workspace members."""
    with get_client() as client:
        response = client.get("/workspace_members")
        output_many(response["data"], MEMBER_COLUMNS, as_json)


@members.command("retrieve")
@click.argument("member_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def members_retrieve(member_id: str, as_json: bool) -> None:
    """Retrieve member details."""
    with get_client() as client:
        response = client.get(f"/workspace_members/{member_id}")
        output_one(response["data"], MEMBER_COLUMNS, as_json)
