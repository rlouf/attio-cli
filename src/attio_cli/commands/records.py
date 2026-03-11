"""Record commands."""

from typing import Any

import click

from attio_cli.cli_core import RECORDS_CREATE_EXAMPLES, RECORDS_UPDATE_EXAMPLES, AttioCommand
from attio_cli.columns import (
    ATTRIBUTE_VALUE_COLUMNS,
    RECORD_COLUMNS,
    RECORD_ENTRY_COLUMNS,
    SEARCH_COLUMNS,
)
from attio_cli.commands.common import get_client
from attio_cli.output import get_json_input, output_many, output_one


@click.group()
def records() -> None:
    """Manage records (people, companies, etc.)."""


@records.command("list")
@click.argument("object")
@click.option("--limit", type=int, help="Maximum number of records")
@click.option("--offset", type=int, help="Number of records to skip")
@click.option("--filter", "filter_json", help="Filter as JSON")
@click.option("--filter-file", help="Read filter JSON from file or '-' for stdin")
@click.option("--sort", "sort_json", help="Sort as JSON")
@click.option("--sort-file", help="Read sort JSON from file or '-' for stdin")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def records_list(
    object: str,
    limit: int,
    offset: int,
    filter_json: str,
    filter_file: str,
    sort_json: str,
    sort_file: str,
    as_json: bool,
) -> None:
    """List records of an object type."""
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
        response = client.post(f"/objects/{object}/records/query", query)
        output_many(response["data"], RECORD_COLUMNS, as_json)


@records.command("retrieve")
@click.argument("object")
@click.argument("record_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def records_retrieve(object: str, record_id: str, as_json: bool) -> None:
    """Retrieve a record by ID."""
    with get_client() as client:
        response = client.get(f"/objects/{object}/records/{record_id}")
        output_one(response["data"], RECORD_COLUMNS, as_json)


@records.command("create", cls=AttioCommand, examples=RECORDS_CREATE_EXAMPLES)
@click.argument("object")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Record values as JSON")
@click.option("--data-file", help="Read record values JSON from file or '-' for stdin")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def records_create(object: str, data: str, data_json: str, data_file: str, as_json: bool) -> None:
    """Create a new record."""
    values = get_json_input(
        data,
        data=data_json,
        data_file=data_file,
        context="record values JSON",
    )
    with get_client() as client:
        response = client.post(f"/objects/{object}/records", {"data": {"values": values}})
        output_one(response["data"], RECORD_COLUMNS, as_json)


@records.command("update", cls=AttioCommand, examples=RECORDS_UPDATE_EXAMPLES)
@click.argument("object")
@click.argument("record_id")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Record values as JSON")
@click.option("--data-file", help="Read record values JSON from file or '-' for stdin")
@click.option("--overwrite", is_flag=True, help="Overwrite multiselect values")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def records_update(
    object: str,
    record_id: str,
    data: str,
    data_json: str,
    data_file: str,
    overwrite: bool,
    as_json: bool,
) -> None:
    """Update a record."""
    values = get_json_input(
        data,
        data=data_json,
        data_file=data_file,
        context="record values JSON",
    )
    with get_client() as client:
        body = {"data": {"values": values}}
        if overwrite:
            response = client.put(f"/objects/{object}/records/{record_id}", body)
        else:
            response = client.patch(f"/objects/{object}/records/{record_id}", body)
        output_one(response["data"], RECORD_COLUMNS, as_json)


@records.command("search")
@click.argument("object")
@click.argument("query")
@click.option("--limit", type=int, help="Maximum number of results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def records_search(object: str, query: str, limit: int, as_json: bool) -> None:
    """Search records."""
    body: dict[str, Any] = {"query": query, "objects": [object]}
    if limit:
        body["limit"] = limit

    with get_client() as client:
        response = client.post("/objects/records/search", body)
        output_many(response["data"], SEARCH_COLUMNS, as_json)


@records.command("entries")
@click.argument("object")
@click.argument("record_id")
@click.option("--limit", type=int, help="Maximum number of entries")
@click.option("--offset", type=int, help="Number of entries to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def records_entries(object: str, record_id: str, limit: int, offset: int, as_json: bool) -> None:
    """List list entries linked to a record."""
    params = {}
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset

    with get_client() as client:
        response = client.get(f"/objects/{object}/records/{record_id}/entries", params=params)
        output_many(response["data"], RECORD_ENTRY_COLUMNS, as_json)


@records.command("values")
@click.argument("object")
@click.argument("record_id")
@click.argument("attribute")
@click.option("--show-historic", is_flag=True, help="Include historic values")
@click.option("--limit", type=int, help="Maximum number of values")
@click.option("--offset", type=int, help="Number of values to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def records_values(
    object: str,
    record_id: str,
    attribute: str,
    show_historic: bool,
    limit: int,
    offset: int,
    as_json: bool,
) -> None:
    """List values for a record attribute."""
    params = {}
    if show_historic:
        params["show_historic"] = "true"
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset

    with get_client() as client:
        response = client.get(
            f"/objects/{object}/records/{record_id}/attributes/{attribute}/values",
            params=params,
        )
        output_many(response["data"], ATTRIBUTE_VALUE_COLUMNS, as_json)
