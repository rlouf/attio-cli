"""Note commands."""

import click

from attio.columns import NOTE_COLUMNS
from attio.commands.common import get_client
from attio.output import output_many, output_one


@click.group()
def notes() -> None:
    """Manage notes."""


@notes.command("list")
@click.option("--parent-object", help="Filter by parent object type")
@click.option("--parent-record-id", help="Filter by parent record ID")
@click.option("--limit", type=int, help="Maximum number of notes")
@click.option("--offset", type=int, help="Number of notes to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def notes_list(
    parent_object: str, parent_record_id: str, limit: int, offset: int, as_json: bool
) -> None:
    """List notes."""
    query = {}
    if limit:
        query["limit"] = limit
    if offset:
        query["offset"] = offset
    if parent_object:
        query["parent_object"] = parent_object
    if parent_record_id:
        query["parent_record_id"] = parent_record_id

    with get_client() as client:
        response = client.post("/notes/query", query)
        output_many(response["data"], NOTE_COLUMNS, as_json)


@notes.command("retrieve")
@click.argument("note_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def notes_retrieve(note_id: str, as_json: bool) -> None:
    """Retrieve a note by ID."""
    with get_client() as client:
        response = client.get(f"/notes/{note_id}")
        output_one(response["data"], NOTE_COLUMNS, as_json)


@notes.command("create")
@click.option("--title", required=True, help="Note title")
@click.option("--parent-object", required=True, help="Parent object type")
@click.option("--parent-record-id", required=True, help="Parent record ID")
@click.option("--content", help="Note content")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def notes_create(
    title: str, parent_object: str, parent_record_id: str, content: str, as_json: bool
) -> None:
    """Create a new note."""
    data = {
        "parent_object": parent_object,
        "parent_record_id": parent_record_id,
        "title": title,
        "format": "plaintext",
    }
    if content:
        data["content"] = content

    with get_client() as client:
        response = client.post("/notes", {"data": data})
        output_one(response["data"], NOTE_COLUMNS, as_json)
