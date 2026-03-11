"""Attribute commands."""

import click

from attio_cli.cli_core import (
    ATTRIBUTES_ADD_STATUS_EXAMPLES,
    ATTRIBUTES_CREATE_EXAMPLES,
    ATTRIBUTES_UPDATE_EXAMPLES,
    ATTRIBUTES_UPDATE_STATUS_EXAMPLES,
    AttioCommand,
)
from attio_cli.columns import ATTRIBUTE_COLUMNS, OPTION_COLUMNS, STATUS_COLUMNS
from attio_cli.commands.common import attribute_path, get_client
from attio_cli.output import get_json_input, output_many, output_one


@click.group()
def attributes() -> None:
    """Manage attributes for objects and lists."""


@attributes.command("list")
@click.argument("identifier")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def attributes_list(identifier: str, target: str, as_json: bool) -> None:
    """List attributes for an object or list."""
    with get_client() as client:
        response = client.get(attribute_path(target, identifier))
        output_many(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("retrieve")
@click.argument("identifier")
@click.argument("attribute")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_retrieve(identifier: str, attribute: str, target: str, as_json: bool) -> None:
    """Retrieve attribute details."""
    with get_client() as client:
        response = client.get(attribute_path(target, identifier, f"/{attribute}"))
        output_one(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("create", cls=AttioCommand, examples=ATTRIBUTES_CREATE_EXAMPLES)
@click.argument("identifier")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Attribute payload as JSON")
@click.option("--data-file", help="Read attribute JSON from file or '-' for stdin")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--title", help="Attribute title")
@click.option("--type", "attr_type", help="Attribute type")
@click.option("--slug", help="Attribute API slug")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_create(
    identifier: str,
    data: str,
    data_json: str,
    data_file: str,
    target: str,
    title: str,
    attr_type: str,
    slug: str,
    as_json: bool,
) -> None:
    """Create a new attribute."""
    payload = (
        get_json_input(
            data,
            data=data_json,
            data_file=data_file,
            required=False,
            context="attribute JSON",
        )
        or {}
    )
    if title is not None:
        payload["title"] = title
    if attr_type is not None:
        payload["type"] = attr_type
    if slug is not None:
        payload["api_slug"] = slug
    if not payload:
        raise click.ClickException("Provide attribute JSON or at least one attribute field.")

    with get_client() as client:
        response = client.post(
            attribute_path(target, identifier),
            {"data": payload},
        )
        output_one(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("update", cls=AttioCommand, examples=ATTRIBUTES_UPDATE_EXAMPLES)
@click.argument("identifier")
@click.argument("attribute")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Attribute update payload as JSON")
@click.option("--data-file", help="Read attribute update JSON from file or '-' for stdin")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--title", help="New title")
@click.option("--slug", help="New API slug")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_update(
    identifier: str,
    attribute: str,
    data: str,
    data_json: str,
    data_file: str,
    target: str,
    title: str,
    slug: str,
    as_json: bool,
) -> None:
    """Update an attribute."""
    payload = (
        get_json_input(
            data,
            data=data_json,
            data_file=data_file,
            required=False,
            context="attribute update JSON",
        )
        or {}
    )
    if title:
        payload["title"] = title
    if slug:
        payload["api_slug"] = slug
    if not payload:
        raise click.ClickException("Provide update JSON or at least one field to change.")

    with get_client() as client:
        response = client.patch(
            attribute_path(target, identifier, f"/{attribute}"),
            {"data": payload},
        )
        output_one(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("options")
@click.argument("identifier")
@click.argument("attribute")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--show-archived", is_flag=True, help="Include archived options")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def attributes_options(
    identifier: str, attribute: str, target: str, show_archived: bool, as_json: bool
) -> None:
    """List select options for an attribute."""
    params = {"show_archived": "true"} if show_archived else None
    with get_client() as client:
        response = client.get(
            attribute_path(target, identifier, f"/{attribute}/options"),
            params=params,
        )
        output_many(response["data"], OPTION_COLUMNS, as_json)


@attributes.command("add-option")
@click.argument("identifier")
@click.argument("attribute")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Option payload as JSON")
@click.option("--data-file", help="Read option JSON from file or '-' for stdin")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--title", help="Option title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_add_option(
    identifier: str,
    attribute: str,
    data: str,
    data_json: str,
    data_file: str,
    target: str,
    title: str,
    as_json: bool,
) -> None:
    """Add a select option."""
    payload = (
        get_json_input(
            data,
            data=data_json,
            data_file=data_file,
            required=False,
            context="option JSON",
        )
        or {}
    )
    if title is not None:
        payload["title"] = title
    if not payload:
        raise click.ClickException("Provide option JSON or at least --title.")

    with get_client() as client:
        response = client.post(
            attribute_path(target, identifier, f"/{attribute}/options"),
            {"data": payload},
        )
        output_one(response["data"], OPTION_COLUMNS, as_json)


@attributes.command("update-option")
@click.argument("identifier")
@click.argument("attribute")
@click.argument("option_id")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Option update payload as JSON")
@click.option("--data-file", help="Read option update JSON from file or '-' for stdin")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--title", help="New title")
@click.option("--archived", type=bool, help="Whether the option is archived")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_update_option(
    identifier: str,
    attribute: str,
    option_id: str,
    data: str,
    data_json: str,
    data_file: str,
    target: str,
    title: str,
    archived: bool,
    as_json: bool,
) -> None:
    """Update a select option."""
    payload = (
        get_json_input(
            data,
            data=data_json,
            data_file=data_file,
            required=False,
            context="option update JSON",
        )
        or {}
    )
    if title:
        payload["title"] = title
    if archived is not None:
        payload["is_archived"] = archived
    if not payload:
        raise click.ClickException("Provide update JSON or at least one field to change.")

    with get_client() as client:
        response = client.patch(
            attribute_path(target, identifier, f"/{attribute}/options/{option_id}"),
            {"data": payload},
        )
        output_one(response["data"], OPTION_COLUMNS, as_json)


@attributes.command("statuses")
@click.argument("identifier")
@click.argument("attribute")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--show-archived", is_flag=True, help="Include archived statuses")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def attributes_statuses(
    identifier: str,
    attribute: str,
    target: str,
    show_archived: bool,
    as_json: bool,
) -> None:
    """List status options for an attribute."""
    params = {"show_archived": "true"} if show_archived else None
    with get_client() as client:
        response = client.get(
            attribute_path(target, identifier, f"/{attribute}/statuses"),
            params=params,
        )
        output_many(response["data"], STATUS_COLUMNS, as_json)


@attributes.command("add-status", cls=AttioCommand, examples=ATTRIBUTES_ADD_STATUS_EXAMPLES)
@click.argument("identifier")
@click.argument("attribute")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Status payload as JSON")
@click.option("--data-file", help="Read status JSON from file or '-' for stdin")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--title", help="Status title")
@click.option("--celebration-enabled", type=bool, help="Whether celebration is enabled")
@click.option("--target-time-in-status", help="Target time in status as JSON")
@click.option(
    "--target-time-in-status-file",
    help="Read target time in status JSON from file or '-' for stdin",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_add_status(
    identifier: str,
    attribute: str,
    data: str,
    data_json: str,
    data_file: str,
    target: str,
    title: str,
    celebration_enabled: bool,
    target_time_in_status: str,
    target_time_in_status_file: str,
    as_json: bool,
) -> None:
    """Add a status option."""
    payload = (
        get_json_input(
            data,
            data=data_json,
            data_file=data_file,
            required=False,
            context="status JSON",
        )
        or {}
    )
    if title is not None:
        payload["title"] = title
    if celebration_enabled is not None:
        payload["celebration_enabled"] = celebration_enabled
    target_time_payload = get_json_input(
        data=target_time_in_status,
        data_file=target_time_in_status_file,
        required=False,
        context="target time in status JSON",
        allow_stdin=False,
    )
    if target_time_payload is not None:
        payload["target_time_in_status"] = target_time_payload
    if not payload:
        raise click.ClickException("Provide status JSON or at least one field.")

    with get_client() as client:
        response = client.post(
            attribute_path(target, identifier, f"/{attribute}/statuses"),
            {"data": payload},
        )
        output_one(response["data"], STATUS_COLUMNS, as_json)


@attributes.command(
    "update-status",
    cls=AttioCommand,
    examples=ATTRIBUTES_UPDATE_STATUS_EXAMPLES,
)
@click.argument("identifier")
@click.argument("attribute")
@click.argument("status_id")
@click.argument("data", required=False)
@click.option("--data", "data_json", help="Status update payload as JSON")
@click.option("--data-file", help="Read status update JSON from file or '-' for stdin")
@click.option(
    "--target",
    type=click.Choice(["objects", "lists"]),
    default="objects",
    show_default=True,
    help="Attribute owner type",
)
@click.option("--title", help="New title")
@click.option("--archived", type=bool, help="Whether the status is archived")
@click.option("--celebration-enabled", type=bool, help="Whether celebration is enabled")
@click.option("--target-time-in-status", help="Target time in status as JSON")
@click.option(
    "--target-time-in-status-file",
    help="Read target time in status JSON from file or '-' for stdin",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_update_status(
    identifier: str,
    attribute: str,
    status_id: str,
    data: str,
    data_json: str,
    data_file: str,
    target: str,
    title: str,
    archived: bool,
    celebration_enabled: bool,
    target_time_in_status: str,
    target_time_in_status_file: str,
    as_json: bool,
) -> None:
    """Update a status option."""
    payload = (
        get_json_input(
            data,
            data=data_json,
            data_file=data_file,
            required=False,
            context="status update JSON",
        )
        or {}
    )
    if title:
        payload["title"] = title
    if archived is not None:
        payload["is_archived"] = archived
    if celebration_enabled is not None:
        payload["celebration_enabled"] = celebration_enabled
    target_time_payload = get_json_input(
        data=target_time_in_status,
        data_file=target_time_in_status_file,
        required=False,
        context="target time in status JSON",
        allow_stdin=False,
    )
    if target_time_payload is not None:
        payload["target_time_in_status"] = target_time_payload
    if not payload:
        raise click.ClickException("Provide update JSON or at least one field to change.")

    with get_client() as client:
        response = client.patch(
            attribute_path(target, identifier, f"/{attribute}/statuses/{status_id}"),
            {"data": payload},
        )
        output_one(response["data"], STATUS_COLUMNS, as_json)
