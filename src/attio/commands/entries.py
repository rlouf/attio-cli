"""List entry commands."""

import click

from attio.cli_core import ENTRIES_CREATE_EXAMPLES, ENTRIES_UPDATE_EXAMPLES, AttioCommand
from attio.columns import ATTRIBUTE_VALUE_COLUMNS, ENTRY_COLUMNS
from attio.commands.common import get_client
from attio.output import get_json_input, output_many, output_one


@click.group()
def entries() -> None:
    """Manage list entries."""


@entries.command("list")
@click.argument("list_id")
@click.option("--limit", type=int, help="Maximum number of entries")
@click.option("--offset", type=int, help="Number of entries to skip")
@click.option("--filter", "filter_json", help="Filter as JSON")
@click.option("--filter-file", help="Read filter JSON from file or '-' for stdin")
@click.option("--sort", "sort_json", help="Sort as JSON")
@click.option("--sort-file", help="Read sort JSON from file or '-' for stdin")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def entries_list(
    list_id: str,
    limit: int,
    offset: int,
    filter_json: str,
    filter_file: str,
    sort_json: str,
    sort_file: str,
    as_json: bool,
) -> None:
    """List entries in a list."""
    query = {}
    if limit:
        query["limit"] = limit
    if offset:
        query["offset"] = offset

    filter_value = get_json_input(
        data=filter_json,
        data_file=filter_file,
        required=False,
        context="filter JSON",
        allow_stdin=False,
    )
    if filter_value is not None:
        query["filter"] = filter_value

    sort_value = get_json_input(
        data=sort_json,
        data_file=sort_file,
        required=False,
        context="sort JSON",
        allow_stdin=False,
    )
    if sort_value is not None:
        query["sorts"] = sort_value

    with get_client() as client:
        response = client.post(f"/lists/{list_id}/entries/query", query)
        output_many(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("retrieve")
@click.argument("list_id")
@click.argument("entry_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def entries_retrieve(list_id: str, entry_id: str, as_json: bool) -> None:
    """Retrieve an entry by ID."""
    with get_client() as client:
        response = client.get(f"/lists/{list_id}/entries/{entry_id}")
        output_one(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("create", cls=AttioCommand, examples=ENTRIES_CREATE_EXAMPLES)
@click.argument("list_id")
@click.option("--record-id", required=True, help="Record ID to add")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Entry values as JSON")
@click.option("--data-file", help="Read entry values JSON from file or '-' for stdin")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def entries_create(
    list_id: str,
    record_id: str,
    data: str,
    data_json: str,
    data_file: str,
    as_json: bool,
) -> None:
    """Add a record to a list."""
    entry_values = get_json_input(
        data,
        data=data_json,
        data_file=data_file,
        required=False,
        context="entry values JSON",
    )

    body = {"data": {"parent_record_id": record_id}}
    if entry_values is not None:
        body["data"]["entry_values"] = entry_values

    with get_client() as client:
        response = client.post(f"/lists/{list_id}/entries", body)
        output_one(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("update", cls=AttioCommand, examples=ENTRIES_UPDATE_EXAMPLES)
@click.argument("list_id")
@click.argument("entry_id")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Entry values as JSON")
@click.option("--data-file", help="Read entry values JSON from file or '-' for stdin")
@click.option("--overwrite", is_flag=True, help="Overwrite multiselect values")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def entries_update(
    list_id: str,
    entry_id: str,
    data: str,
    data_json: str,
    data_file: str,
    overwrite: bool,
    as_json: bool,
) -> None:
    """Update an entry."""
    values = get_json_input(
        data,
        data=data_json,
        data_file=data_file,
        context="entry values JSON",
    )
    body = {"data": {"entry_values": values}}

    with get_client() as client:
        if overwrite:
            response = client.put(f"/lists/{list_id}/entries/{entry_id}", body)
        else:
            response = client.patch(f"/lists/{list_id}/entries/{entry_id}", body)
        output_one(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("values")
@click.argument("list_id")
@click.argument("entry_id")
@click.argument("attribute")
@click.option("--show-historic", is_flag=True, help="Include historic values")
@click.option("--limit", type=int, help="Maximum number of values")
@click.option("--offset", type=int, help="Number of values to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def entries_values(
    list_id: str,
    entry_id: str,
    attribute: str,
    show_historic: bool,
    limit: int,
    offset: int,
    as_json: bool,
) -> None:
    """List values for a list entry attribute."""
    params = {}
    if show_historic:
        params["show_historic"] = "true"
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset

    with get_client() as client:
        response = client.get(
            f"/lists/{list_id}/entries/{entry_id}/attributes/{attribute}/values",
            params=params,
        )
        output_many(response["data"], ATTRIBUTE_VALUE_COLUMNS, as_json)
