"""Main CLI entry point."""

import click

from attio_cli import __version__
from attio_cli.client import AttioClient
from attio_cli.config import get_api_key, get_config_path, load_config, set_api_key
from attio_cli.output import get_json_input, output_many, output_one


def get_client() -> AttioClient:
    """Get an authenticated API client."""
    api_key = get_api_key()
    if not api_key:
        raise click.ClickException(
            "No API key configured. Set ATTIO_API_KEY or run: attio config set api-key <key>"
        )
    return AttioClient(api_key)


# Column definitions for different types
IDENTITY_COLUMNS = [
    ("WORKSPACE", lambda x: x.get("workspace", {}).get("name", "-")),
    ("WORKSPACE ID", lambda x: x.get("workspace", {}).get("id", {}).get("workspace_id", "-")),
    ("ACCESS TYPE", lambda x: x.get("access_type", "-")),
]

OBJECT_COLUMNS = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("SINGULAR", lambda x: x.get("singular_noun", "-")),
    ("PLURAL", lambda x: x.get("plural_noun", "-")),
    ("ID", lambda x: x.get("id", {}).get("object_id", "-")),
]

RECORD_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("record_id", "-")),
    ("NAME", lambda x: _extract_name(x.get("values", {}))),
    ("VALUES", lambda x: _truncate(str(x.get("values", {})), 60)),
]

SEARCH_COLUMNS = [
    ("RECORD ID", lambda x: x.get("id", {}).get("record_id", "-")),
    ("OBJECT", lambda x: x.get("object_slug", "-")),
    ("TEXT", lambda x: x.get("record_text", "-")),
]

LIST_COLUMNS = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("NAME", lambda x: x.get("name", "-")),
    (
        "PARENT OBJECT",
        lambda x: ", ".join(x.get("parent_object", [])) if x.get("parent_object") else "-",
    ),
    ("ID", lambda x: x.get("id", {}).get("list_id", "-")),
]

ENTRY_COLUMNS = [
    ("ENTRY ID", lambda x: x.get("id", {}).get("entry_id", "-")),
    ("RECORD ID", lambda x: x.get("parent_record_id", "-")),
    ("VALUES", lambda x: _truncate(str(x.get("entry_values", {})), 60)),
]

TASK_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("task_id", "-")),
    ("CONTENT", lambda x: _truncate(x.get("content_plaintext", ""), 50)),
    ("COMPLETED", lambda x: "Y" if x.get("is_completed") else ""),
    ("DEADLINE", lambda x: x.get("deadline_at", "-") or "-"),
]

NOTE_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("note_id", "-")),
    ("TITLE", lambda x: x.get("title", "-") or "-"),
    (
        "PARENT",
        lambda x: f"{x.get('parent_object', '')}:{x.get('parent_record_id', '')[:8]}"
        if x.get("parent_record_id")
        else "-",
    ),
    ("CREATED", lambda x: (x.get("created_at", "") or "")[:10] or "-"),
]

ATTRIBUTE_COLUMNS = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("TYPE", lambda x: x.get("type", "-")),
    ("REQUIRED", lambda x: "Y" if x.get("is_required") else ""),
    ("MULTISELECT", lambda x: "Y" if x.get("is_multiselect") else ""),
]

OPTION_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("option_id", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("ARCHIVED", lambda x: "Y" if x.get("is_archived") else ""),
]

STATUS_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("status_id", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("ARCHIVED", lambda x: "Y" if x.get("is_archived") else ""),
]

MEMBER_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("workspace_member_id", "-")),
    ("NAME", lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}".strip() or "-"),
    ("EMAIL", lambda x: x.get("email_address", "-") or "-"),
    ("ACCESS", lambda x: x.get("access_level", "-") or "-"),
]

WEBHOOK_COLUMNS = [
    ("ID", lambda x: x.get("id", {}).get("webhook_id", "-")),
    ("TARGET URL", lambda x: x.get("target_url", "-")),
    ("STATUS", lambda x: x.get("status", "-") or "-"),
    (
        "SUBSCRIPTIONS",
        lambda x: f"{len(x.get('subscriptions', []))} events" if x.get("subscriptions") else "-",
    ),
]


def _extract_name(values: dict) -> str:
    """Extract a display name from record values."""
    for field in ["name", "full_name", "first_name", "title", "email_addresses"]:
        if field in values:
            val = values[field]
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, dict):
                    for key in ["value", "email_address", "full_name", "first_name"]:
                        if key in first:
                            return str(first[key])
                else:
                    return str(first)
            elif val:
                return str(val)
    return "-"


def _truncate(s: str, length: int) -> str:
    """Truncate a string with ellipsis."""
    return s[:length] + "..." if len(s) > length else s


@click.group()
@click.version_option(version=__version__)
def cli():
    """CLI for interacting with Attio CRM API."""
    pass


# ============== Config Commands ==============


@cli.group()
def config():
    """Manage configuration."""
    pass


@config.command("show")
def config_show():
    """Show current configuration."""
    cfg = load_config()
    path = get_config_path()
    click.echo(f"Config file: {path}")
    if cfg.get("api_key"):
        masked = cfg["api_key"][:8] + "..." + cfg["api_key"][-4:]
        click.echo(f"API key: {masked}")
    else:
        click.echo("API key: (not set)")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value."""
    if key == "api-key":
        set_api_key(value)
        click.echo("API key saved.")
    else:
        raise click.ClickException(f"Unknown config key: {key}")


# ============== Whoami Command ==============


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def whoami(as_json: bool):
    """Show current workspace and authentication info."""
    with get_client() as client:
        response = client.get("/self")
        output_one(response["data"], IDENTITY_COLUMNS, as_json)


# ============== Objects Commands ==============


@cli.group()
def objects():
    """Manage objects (schema)."""
    pass


@objects.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def objects_list(as_json: bool):
    """List all objects."""
    with get_client() as client:
        response = client.get("/objects")
        output_many(response["data"], OBJECT_COLUMNS, as_json)


@objects.command("get")
@click.argument("object")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def objects_get(object: str, as_json: bool):
    """Get object details."""
    with get_client() as client:
        response = client.get(f"/objects/{object}")
        output_one(response["data"], OBJECT_COLUMNS, as_json)


# ============== Records Commands ==============


@cli.group()
def records():
    """Manage records (people, companies, etc.)."""
    pass


@records.command("list")
@click.argument("object")
@click.option("--limit", type=int, help="Maximum number of records")
@click.option("--offset", type=int, help="Number of records to skip")
@click.option("--filter", "filter_json", help="Filter as JSON")
@click.option("--sort", "sort_json", help="Sort as JSON")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def records_list(
    object: str, limit: int, offset: int, filter_json: str, sort_json: str, as_json: bool
):
    """List records of an object type."""
    import json as json_mod

    query = {}
    if limit:
        query["limit"] = limit
    if offset:
        query["offset"] = offset
    if filter_json:
        query["filter"] = json_mod.loads(filter_json)
    if sort_json:
        query["sorts"] = json_mod.loads(sort_json)

    with get_client() as client:
        response = client.post(f"/objects/{object}/records/query", query)
        output_many(response["data"], RECORD_COLUMNS, as_json)


@records.command("get")
@click.argument("object")
@click.argument("record_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def records_get(object: str, record_id: str, as_json: bool):
    """Get a record by ID."""
    with get_client() as client:
        response = client.get(f"/objects/{object}/records/{record_id}")
        output_one(response["data"], RECORD_COLUMNS, as_json)


@records.command("create")
@click.argument("object")
@click.argument("data", required=False)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def records_create(object: str, data: str, as_json: bool):
    """Create a new record."""
    values = get_json_input(data)
    with get_client() as client:
        response = client.post(f"/objects/{object}/records", {"data": {"values": values}})
        output_one(response["data"], RECORD_COLUMNS, as_json)


@records.command("update")
@click.argument("object")
@click.argument("record_id")
@click.argument("data", required=False)
@click.option("--overwrite", is_flag=True, help="Overwrite multiselect values")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def records_update(object: str, record_id: str, data: str, overwrite: bool, as_json: bool):
    """Update a record."""
    values = get_json_input(data)
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
def records_search(object: str, query: str, limit: int, as_json: bool):
    """Search records."""
    body = {"query": query, "objects": [object]}
    if limit:
        body["limit"] = limit

    with get_client() as client:
        response = client.post("/objects/records/search", body)
        output_many(response["data"], SEARCH_COLUMNS, as_json)


# ============== Lists Commands ==============


@cli.group()
def lists():
    """Manage lists (pipelines, workflows)."""
    pass


@lists.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def lists_list(as_json: bool):
    """List all lists."""
    with get_client() as client:
        response = client.get("/lists")
        output_many(response["data"], LIST_COLUMNS, as_json)


@lists.command("get")
@click.argument("list_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def lists_get(list_id: str, as_json: bool):
    """Get list details."""
    with get_client() as client:
        response = client.get(f"/lists/{list_id}")
        output_one(response["data"], LIST_COLUMNS, as_json)


# ============== Entries Commands ==============


@cli.group()
def entries():
    """Manage list entries."""
    pass


@entries.command("list")
@click.argument("list_id")
@click.option("--limit", type=int, help="Maximum number of entries")
@click.option("--offset", type=int, help="Number of entries to skip")
@click.option("--filter", "filter_json", help="Filter as JSON")
@click.option("--sort", "sort_json", help="Sort as JSON")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def entries_list(
    list_id: str, limit: int, offset: int, filter_json: str, sort_json: str, as_json: bool
):
    """List entries in a list."""
    import json as json_mod

    query = {}
    if limit:
        query["limit"] = limit
    if offset:
        query["offset"] = offset
    if filter_json:
        query["filter"] = json_mod.loads(filter_json)
    if sort_json:
        query["sorts"] = json_mod.loads(sort_json)

    with get_client() as client:
        response = client.post(f"/lists/{list_id}/entries/query", query)
        output_many(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("get")
@click.argument("list_id")
@click.argument("entry_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def entries_get(list_id: str, entry_id: str, as_json: bool):
    """Get an entry by ID."""
    with get_client() as client:
        response = client.get(f"/lists/{list_id}/entries/{entry_id}")
        output_one(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("create")
@click.argument("list_id")
@click.option("--record-id", required=True, help="Record ID to add")
@click.argument("data", required=False)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def entries_create(list_id: str, record_id: str, data: str, as_json: bool):
    """Add a record to a list."""
    import json as json_mod

    from attio_cli.output import is_stdin_piped, read_stdin

    entry_values = None
    if data:
        entry_values = json_mod.loads(data)
    elif is_stdin_piped():
        stdin_data = read_stdin().strip()
        if stdin_data:
            entry_values = json_mod.loads(stdin_data)

    body = {"data": {"parent_record_id": record_id}}
    if entry_values:
        body["data"]["entry_values"] = entry_values

    with get_client() as client:
        response = client.post(f"/lists/{list_id}/entries", body)
        output_one(response["data"], ENTRY_COLUMNS, as_json)


@entries.command("update")
@click.argument("list_id")
@click.argument("entry_id")
@click.argument("data", required=False)
@click.option("--overwrite", is_flag=True, help="Overwrite multiselect values")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def entries_update(list_id: str, entry_id: str, data: str, overwrite: bool, as_json: bool):
    """Update an entry."""
    values = get_json_input(data)
    body = {"data": {"entry_values": values}}

    with get_client() as client:
        if overwrite:
            response = client.put(f"/lists/{list_id}/entries/{entry_id}", body)
        else:
            response = client.patch(f"/lists/{list_id}/entries/{entry_id}", body)
        output_one(response["data"], ENTRY_COLUMNS, as_json)


# ============== Tasks Commands ==============


@cli.group()
def tasks():
    """Manage tasks."""
    pass


@tasks.command("list")
@click.option("--limit", type=int, help="Maximum number of tasks")
@click.option("--offset", type=int, help="Number of tasks to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def tasks_list(limit: int, offset: int, as_json: bool):
    """List tasks."""
    query = {}
    if limit:
        query["limit"] = limit
    if offset:
        query["offset"] = offset

    with get_client() as client:
        response = client.post("/tasks/query", query)
        output_many(response["data"], TASK_COLUMNS, as_json)


@tasks.command("get")
@click.argument("task_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def tasks_get(task_id: str, as_json: bool):
    """Get a task by ID."""
    with get_client() as client:
        response = client.get(f"/tasks/{task_id}")
        output_one(response["data"], TASK_COLUMNS, as_json)


@tasks.command("create")
@click.argument("content")
@click.option("--deadline", help="Deadline (ISO 8601 format)")
@click.option("--assignees", help="Assignees as JSON array")
@click.option("--linked-records", help="Linked records as JSON array")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def tasks_create(content: str, deadline: str, assignees: str, linked_records: str, as_json: bool):
    """Create a new task."""
    import json as json_mod

    data = {"content": content, "format": "plaintext"}
    if deadline:
        data["deadline_at"] = deadline
    if assignees:
        data["assignees"] = json_mod.loads(assignees)
    if linked_records:
        data["linked_records"] = json_mod.loads(linked_records)

    with get_client() as client:
        response = client.post("/tasks", {"data": data})
        output_one(response["data"], TASK_COLUMNS, as_json)


@tasks.command("update")
@click.argument("task_id")
@click.option("--content", help="New task content")
@click.option("--completed", type=bool, help="Mark as completed")
@click.option("--deadline", help="New deadline (ISO 8601 format)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def tasks_update(task_id: str, content: str, completed: bool, deadline: str, as_json: bool):
    """Update a task."""
    data = {}
    if content is not None:
        data["content"] = content
        data["format"] = "plaintext"
    if completed is not None:
        data["is_completed"] = completed
    if deadline is not None:
        data["deadline_at"] = deadline

    with get_client() as client:
        response = client.patch(f"/tasks/{task_id}", {"data": data})
        output_one(response["data"], TASK_COLUMNS, as_json)


# ============== Notes Commands ==============


@cli.group()
def notes():
    """Manage notes."""
    pass


@notes.command("list")
@click.option("--parent-object", help="Filter by parent object type")
@click.option("--parent-record-id", help="Filter by parent record ID")
@click.option("--limit", type=int, help="Maximum number of notes")
@click.option("--offset", type=int, help="Number of notes to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def notes_list(parent_object: str, parent_record_id: str, limit: int, offset: int, as_json: bool):
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


@notes.command("get")
@click.argument("note_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def notes_get(note_id: str, as_json: bool):
    """Get a note by ID."""
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
):
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


# ============== Attributes Commands ==============


@cli.group()
def attributes():
    """Manage object attributes."""
    pass


@attributes.command("list")
@click.argument("object")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def attributes_list(object: str, as_json: bool):
    """List attributes for an object."""
    with get_client() as client:
        response = client.get(f"/objects/{object}/attributes")
        output_many(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("get")
@click.argument("object")
@click.argument("attribute")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_get(object: str, attribute: str, as_json: bool):
    """Get attribute details."""
    with get_client() as client:
        response = client.get(f"/objects/{object}/attributes/{attribute}")
        output_one(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("create")
@click.argument("object")
@click.option("--title", required=True, help="Attribute title")
@click.option("--type", "attr_type", required=True, help="Attribute type")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_create(object: str, title: str, attr_type: str, as_json: bool):
    """Create a new attribute."""
    with get_client() as client:
        response = client.post(
            f"/objects/{object}/attributes",
            {"data": {"title": title, "type": attr_type}},
        )
        output_one(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("update")
@click.argument("object")
@click.argument("attribute")
@click.option("--title", help="New title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_update(object: str, attribute: str, title: str, as_json: bool):
    """Update an attribute."""
    data = {}
    if title:
        data["title"] = title

    with get_client() as client:
        response = client.patch(
            f"/objects/{object}/attributes/{attribute}",
            {"data": data},
        )
        output_one(response["data"], ATTRIBUTE_COLUMNS, as_json)


@attributes.command("options")
@click.argument("object")
@click.argument("attribute")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def attributes_options(object: str, attribute: str, as_json: bool):
    """List select options for an attribute."""
    with get_client() as client:
        response = client.get(f"/objects/{object}/attributes/{attribute}/options")
        output_many(response["data"], OPTION_COLUMNS, as_json)


@attributes.command("add-option")
@click.argument("object")
@click.argument("attribute")
@click.option("--title", required=True, help="Option title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_add_option(object: str, attribute: str, title: str, as_json: bool):
    """Add a select option."""
    with get_client() as client:
        response = client.post(
            f"/objects/{object}/attributes/{attribute}/options",
            {"data": {"title": title}},
        )
        output_one(response["data"], OPTION_COLUMNS, as_json)


@attributes.command("update-option")
@click.argument("object")
@click.argument("attribute")
@click.argument("option_id")
@click.option("--title", help="New title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_update_option(
    object: str, attribute: str, option_id: str, title: str, as_json: bool
):
    """Update a select option."""
    data = {}
    if title:
        data["title"] = title

    with get_client() as client:
        response = client.patch(
            f"/objects/{object}/attributes/{attribute}/options/{option_id}",
            {"data": data},
        )
        output_one(response["data"], OPTION_COLUMNS, as_json)


@attributes.command("statuses")
@click.argument("object")
@click.argument("attribute")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def attributes_statuses(object: str, attribute: str, as_json: bool):
    """List status options for an attribute."""
    with get_client() as client:
        response = client.get(f"/objects/{object}/attributes/{attribute}/statuses")
        output_many(response["data"], STATUS_COLUMNS, as_json)


@attributes.command("add-status")
@click.argument("object")
@click.argument("attribute")
@click.option("--title", required=True, help="Status title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_add_status(object: str, attribute: str, title: str, as_json: bool):
    """Add a status option."""
    with get_client() as client:
        response = client.post(
            f"/objects/{object}/attributes/{attribute}/statuses",
            {"data": {"title": title}},
        )
        output_one(response["data"], STATUS_COLUMNS, as_json)


@attributes.command("update-status")
@click.argument("object")
@click.argument("attribute")
@click.argument("status_id")
@click.option("--title", help="New title")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def attributes_update_status(
    object: str, attribute: str, status_id: str, title: str, as_json: bool
):
    """Update a status option."""
    data = {}
    if title:
        data["title"] = title

    with get_client() as client:
        response = client.patch(
            f"/objects/{object}/attributes/{attribute}/statuses/{status_id}",
            {"data": data},
        )
        output_one(response["data"], STATUS_COLUMNS, as_json)


# ============== Members Commands ==============


@cli.group()
def members():
    """Manage workspace members."""
    pass


@members.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def members_list(as_json: bool):
    """List workspace members."""
    with get_client() as client:
        response = client.get("/workspace_members")
        output_many(response["data"], MEMBER_COLUMNS, as_json)


@members.command("get")
@click.argument("member_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def members_get(member_id: str, as_json: bool):
    """Get member details."""
    with get_client() as client:
        response = client.get(f"/workspace_members/{member_id}")
        output_one(response["data"], MEMBER_COLUMNS, as_json)


# ============== Webhooks Commands ==============


@cli.group()
def webhooks():
    """Manage webhooks."""
    pass


@webhooks.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def webhooks_list(as_json: bool):
    """List webhooks."""
    with get_client() as client:
        response = client.get("/webhooks")
        output_many(response["data"], WEBHOOK_COLUMNS, as_json)


@webhooks.command("get")
@click.argument("webhook_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def webhooks_get(webhook_id: str, as_json: bool):
    """Get webhook details."""
    with get_client() as client:
        response = client.get(f"/webhooks/{webhook_id}")
        output_one(response["data"], WEBHOOK_COLUMNS, as_json)


@webhooks.command("create")
@click.option("--target-url", required=True, help="Target URL")
@click.option("--subscriptions", required=True, help="Comma-separated event types")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def webhooks_create(target_url: str, subscriptions: str, as_json: bool):
    """Create a new webhook."""
    subs = [{"event_type": s.strip()} for s in subscriptions.split(",")]
    with get_client() as client:
        response = client.post(
            "/webhooks",
            {"data": {"target_url": target_url, "subscriptions": subs}},
        )
        output_one(response["data"], WEBHOOK_COLUMNS, as_json)


@webhooks.command("update")
@click.argument("webhook_id")
@click.option("--target-url", help="New target URL")
@click.option("--subscriptions", help="New subscriptions (comma-separated)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def webhooks_update(webhook_id: str, target_url: str, subscriptions: str, as_json: bool):
    """Update a webhook."""
    data = {}
    if target_url:
        data["target_url"] = target_url
    if subscriptions:
        data["subscriptions"] = [{"event_type": s.strip()} for s in subscriptions.split(",")]

    with get_client() as client:
        response = client.patch(f"/webhooks/{webhook_id}", {"data": data})
        output_one(response["data"], WEBHOOK_COLUMNS, as_json)


if __name__ == "__main__":
    cli()
