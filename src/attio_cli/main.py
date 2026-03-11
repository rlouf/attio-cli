"""Main CLI entry point."""

import os
from typing import Any

import click

from attio_cli import __version__
from attio_cli.client import AUTH_SETUP_HINT, AttioClient, AttioError
from attio_cli.config import (
    AUTH_SOURCE_CONFIG,
    AUTH_SOURCE_ENV,
    delete_api_key,
    get_api_key,
    resolve_auth_state,
    set_api_key,
)
from attio_cli.output import ColumnSpec, Row, get_json_input, output_many, output_one


def get_client() -> AttioClient:
    """Get an authenticated API client."""
    api_key = get_api_key()
    if not api_key:
        raise click.ClickException(f"No API key configured. {AUTH_SETUP_HINT}")
    return AttioClient(api_key)


# Column definitions for different types
IDENTITY_COLUMNS: list[ColumnSpec] = [
    ("WORKSPACE", lambda x: x.get("workspace", {}).get("name", "-")),
    ("WORKSPACE ID", lambda x: x.get("workspace", {}).get("id", {}).get("workspace_id", "-")),
    ("ACCESS TYPE", lambda x: x.get("access_type", "-")),
]

OBJECT_COLUMNS: list[ColumnSpec] = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("SINGULAR", lambda x: x.get("singular_noun", "-")),
    ("PLURAL", lambda x: x.get("plural_noun", "-")),
    ("ID", lambda x: x.get("id", {}).get("object_id", "-")),
]

RECORD_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("record_id", "-")),
    ("NAME", lambda x: _extract_name(x.get("values", {}))),
    ("VALUES", lambda x: _truncate(str(x.get("values", {})), 60)),
]

SEARCH_COLUMNS: list[ColumnSpec] = [
    ("RECORD ID", lambda x: x.get("id", {}).get("record_id", "-")),
    ("OBJECT", lambda x: x.get("object_slug", "-")),
    ("TEXT", lambda x: x.get("record_text", "-")),
]

RECORD_ENTRY_COLUMNS: list[ColumnSpec] = [
    ("ENTRY ID", lambda x: x.get("entry_id", "-")),
    ("LIST", lambda x: x.get("list_api_slug", "-")),
    ("LIST ID", lambda x: x.get("list_id", "-")),
]

LIST_COLUMNS: list[ColumnSpec] = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("NAME", lambda x: x.get("name", "-")),
    (
        "PARENT OBJECT",
        lambda x: ", ".join(x.get("parent_object", [])) if x.get("parent_object") else "-",
    ),
    ("ID", lambda x: x.get("id", {}).get("list_id", "-")),
]

ENTRY_COLUMNS: list[ColumnSpec] = [
    ("ENTRY ID", lambda x: x.get("id", {}).get("entry_id", "-")),
    ("RECORD ID", lambda x: x.get("parent_record_id", "-")),
    ("VALUES", lambda x: _truncate(str(x.get("entry_values", {})), 60)),
]

TASK_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("task_id", "-")),
    ("CONTENT", lambda x: _truncate(x.get("content_plaintext", ""), 50)),
    ("COMPLETED", lambda x: "Y" if x.get("is_completed") else ""),
    ("DEADLINE", lambda x: x.get("deadline_at", "-") or "-"),
]

NOTE_COLUMNS: list[ColumnSpec] = [
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

ATTRIBUTE_COLUMNS: list[ColumnSpec] = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("TYPE", lambda x: x.get("type", "-")),
    ("REQUIRED", lambda x: "Y" if x.get("is_required") else ""),
    ("MULTISELECT", lambda x: "Y" if x.get("is_multiselect") else ""),
]

OPTION_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("option_id", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("ARCHIVED", lambda x: "Y" if x.get("is_archived") else ""),
]

STATUS_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("status_id", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("ARCHIVED", lambda x: "Y" if x.get("is_archived") else ""),
]

ATTRIBUTE_VALUE_COLUMNS: list[ColumnSpec] = [
    ("ACTIVE FROM", lambda x: x.get("active_from", "-") or "-"),
    ("ACTIVE UNTIL", lambda x: x.get("active_until", "-") or "-"),
    ("TYPE", lambda x: x.get("attribute_type", "-") or "-"),
    ("VALUE", lambda x: _summarize_value(x)),
]

MEMBER_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("workspace_member_id", "-")),
    ("NAME", lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}".strip() or "-"),
    ("EMAIL", lambda x: x.get("email_address", "-") or "-"),
    ("ACCESS", lambda x: x.get("access_level", "-") or "-"),
]

WEBHOOK_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("webhook_id", "-")),
    ("TARGET URL", lambda x: x.get("target_url", "-")),
    ("STATUS", lambda x: x.get("status", "-") or "-"),
    (
        "SUBSCRIPTIONS",
        lambda x: f"{len(x.get('subscriptions', []))} events" if x.get("subscriptions") else "-",
    ),
]


def _extract_name(values: Row) -> str:
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


def _summarize_value(item: Row) -> str:
    """Summarize an attribute value payload for table output."""
    metadata_keys = {
        "active_from",
        "active_until",
        "attribute_type",
        "created_by_actor",
    }
    value = {k: v for k, v in item.items() if k not in metadata_keys}
    return _truncate(str(value), 60) if value else "-"


def _attribute_path(target: str, identifier: str, suffix: str = "") -> str:
    """Build an attributes API path for objects or lists."""
    base = f"/{target}/{identifier}/attributes"
    return f"{base}{suffix}"


BANNER_LINES = [
    "               @@@@@@@@@.",
    "             @@@@@@@@@.%#",
    "           .@@@@@@@@@   :@",
    "          =@@@@@@@@@      @",
    "         @@@@@@@@@@       @",
    "        @@@@@@@@@*      -@",
    "       @@@@@@@@@.      %*",
    "      @@@@@@@@@       @. @@@@@@*",
    "    :@@@@@@@@@       @  @@@@@@: @",
    "   %@@@@@@@@@       @  @@@@@@    @",
    "  @@@@@@@@@%      .@ .@@@@@@      @",
    "  %@@@@@@@@@     #@ +@@@@@@@      @",
    "   .@@@@@@@@@   @:  @@@@@@@@@:  .@",
    "     @@@@@@@@@ @     @@@@@@@@@*+@",
    "      %@@@@@@@@       .@@@@@@@@.",
]
BANNER_WORDMARK = "A CLI for Attio"
LLM_GUIDE = """ATTIO CLI LLM GUIDE

Purpose:
- Use this CLI to read and modify Attio CRM data from the terminal.
- When uncertain about a command signature, run `attio <group> --help`.

Authentication:
- Preferred: ATTIO_API_KEY environment variable.
- Saved login: attio config login [<key>]
- Backward-compatible alternative: attio config set api-key <key>
- Verify auth: attio whoami

Help and orientation:
- Root help: attio --help or attio -h
- Group help: attio <group> --help or attio <group> -h
- Machine guide: attio --llm

Output contract:
- Default output is a human-readable table on stdout.
- `--json` returns JSON for single-item commands.
- `--json` returns JSONL for collection commands.
- For automation, prefer `--json` plus `jq`.
- Do not parse table output when IDs are needed.

Identifier conventions:
- `<object>` means an object slug such as `people`, `companies`, or a custom object slug.
- `<record-id>` is a record UUID from `id.record_id`.
- `<list-id>` is the list identifier used by list and entry commands.
- `<entry-id>` is an entry UUID from `id.entry_id`.
- `<attribute>` is usually an attribute API slug, not the display title.
- Attribute commands default to object attributes; use `--target lists` for list attributes.

Structured JSON input precedence:
- Preferred source order for agents:
  1. piped stdin
  2. `--data`
  3. `--data-file`
  4. legacy positional JSON only for backward compatibility
- Do not provide multiple JSON sources to the same command.
- `--data-file -` reads JSON from stdin explicitly.
- Empty JSON input is treated as an error.

JSON-supporting options:
- Main payload commands use `--data` and `--data-file`.
- List/query helpers also support `--filter-file` and `--sort-file`.
- Task array options support `--assignees-file` and `--linked-records-file`.
- Status timing payloads support `--target-time-in-status-file`.

Recommended agent workflow:
1. Discover resource types and IDs with list/search commands.
2. Re-run with `--json` and extract identifiers.
3. Inspect current state with retrieve/values commands before mutation.
4. Apply the smallest valid update payload.
5. Retrieve again if confirmation matters.

Common discovery commands:
- attio whoami
- attio objects list
- attio records list <object>
- attio records search <object> <query>
- attio lists list
- attio entries list <list-id>
- attio attributes list <identifier> [--target objects|lists]

Command inventory:
- whoami
- config: show, set
- objects: list, retrieve
- records: list, retrieve, create, update, search, entries, values
- lists: list, retrieve, update
- entries: list, retrieve, create, update, values
- tasks: list, retrieve, create, update
- notes: list, retrieve, create
- attributes: list, retrieve, create, update, options, add-option, update-option, statuses, add-status, update-status
- members: list, retrieve
- webhooks: list, retrieve, create, update

Records:
- Create: `attio records create <object> --data '{"field": "value"}'`
- Update: `attio records update <object> <record-id> --data '{"field": "value"}'`
- Default update uses PATCH semantics.
- For multiselect fields, PATCH appends values.
- Use `--overwrite` to switch to PUT semantics and replace multiselect values.
- Linked list entries: `attio records entries <object> <record-id>`
- Record attribute values: `attio records values <object> <record-id> <attribute>`

Lists and entries:
- Update list: `attio lists update <list-id> --data '{"name": "New Name"}'`
- Create entry: `attio entries create <list-id> --record-id <record-id> --data '{"field": "value"}'`
- Update entry: `attio entries update <list-id> <entry-id> --data '{"field": "value"}'`
- Entry updates follow the same multiselect behavior as records; use `--overwrite` to replace.
- Entry values: `attio entries values <list-id> <entry-id> <attribute>`

Attributes:
- Default target is `objects`; use `--target lists` for list attributes.
- Use attribute API slugs as identifiers.
- Create with named flags for common cases: `--title`, `--type`, `--slug`
- Use `--data` or `--data-file` for richer attribute payloads.
- Options workflow: `options`, `add-option`, `update-option`
- Status workflow: `statuses`, `add-status`, `update-status`
- Status/option listing supports `--show-archived`.

Tasks:
- Create: `attio tasks create <content> [--deadline ...]`
- Update simple fields with named flags like `--content`, `--completed`, `--deadline`.
- Use `--assignees-file` and `--linked-records-file` for JSON arrays.

Notes:
- Supported: list, retrieve, create
- Not supported: update

Known limitations:
- Delete operations are intentionally not implemented in this CLI.
- Objects are read-only in this CLI.
- List create is not implemented.
- Note update is not implemented.

Example workflows:
- Find and update a record:
  `attio records search people "john@example.com" --json | jq -r '.id.record_id'`
  `echo '{"region": "EMEA"}' | attio records update people <record-id>`
- Inspect list entry status values:
  `attio entries values <list-id> <entry-id> status --json`
- Update a list attribute instead of an object attribute:
  `attio attributes update <list-id> stage --target lists --title "Pipeline Stage"`

Safety:
- Prefer inspect-first workflows before update.
- Prefer `--json` when an agent needs IDs or structured confirmation.
"""

TOP_LEVEL_COMMAND_GROUPS = [
    ("Getting Started", ["config", "whoami"]),
    ("CRM Data", ["records", "entries", "notes", "tasks"]),
    ("Schema", ["objects", "attributes", "lists"]),
    ("Workspace", ["members", "webhooks"]),
]

RECORDS_CREATE_EXAMPLES = [
    'attio records create people --data \'{"name": "Jane Doe"}\'',
    'echo \'{"name": "Jane Doe", "email_addresses": ["jane@example.com"]}\' | attio records create people',
]
RECORDS_UPDATE_EXAMPLES = [
    'attio records update people <record-id> --data \'{"region": "EMEA"}\'',
    "attio records update people <record-id> --data-file record-update.json --overwrite",
]
ENTRIES_CREATE_EXAMPLES = [
    "attio entries create <list-id> --record-id <record-id>",
    'attio entries create <list-id> --record-id <record-id> --data \'{"status": "active"}\'',
]
ENTRIES_UPDATE_EXAMPLES = [
    'attio entries update <list-id> <entry-id> --data \'{"status": "qualified"}\'',
    "attio entries update <list-id> <entry-id> --data-file entry-update.json --overwrite",
]
ATTRIBUTES_CREATE_EXAMPLES = [
    'attio attributes create people --title "Region" --type select --slug region',
    "attio attributes create <list-id> --target lists --data-file attribute.json",
]
ATTRIBUTES_UPDATE_EXAMPLES = [
    'attio attributes update people region --title "Sales Region"',
    'attio attributes update <list-id> stage --target lists --data \'{"description": "Pipeline stage"}\'',
]
ATTRIBUTES_ADD_STATUS_EXAMPLES = [
    'attio attributes add-status <list-id> stage --target lists --title "Qualified"',
    "attio attributes add-status <list-id> stage --target lists --data-file status.json --target-time-in-status-file target-time.json",
]
ATTRIBUTES_UPDATE_STATUS_EXAMPLES = [
    'attio attributes update-status <list-id> stage <status-id> --target lists --title "Proposal"',
    "attio attributes update-status <list-id> stage <status-id> --target lists --archived true --target-time-in-status-file target-time.json",
]
TASKS_CREATE_EXAMPLES = [
    'attio tasks create "Follow up with client" --deadline "2026-03-12T10:00:00Z"',
    'attio tasks create "Prep QBR" --assignees-file assignees.json --linked-records-file linked-records.json',
]


def _render_banner() -> str:
    """Render the help banner with a centered wordmark."""
    width = max(len(line) for line in BANNER_LINES)
    wordmark = BANNER_WORDMARK.center(width)
    return "\n".join([*BANNER_LINES, "", wordmark])


def _should_show_banner(ctx: click.Context) -> bool:
    """Show the banner only for root help in interactive terminals."""
    if ctx.parent is not None:
        return False
    if os.environ.get("ATTIO_NO_BANNER") == "1":
        return False

    stream = click.get_text_stream("stdout")
    return hasattr(stream, "isatty") and stream.isatty()


class AttioGroup(click.Group):
    """Click group with a banner on root help output."""

    def invoke(self, ctx: click.Context) -> object:
        """Normalize API errors into consistent Click-style CLI output."""
        try:
            return super().invoke(ctx)
        except AttioError as exc:
            raise click.ClickException(exc.format_for_cli()) from None

    def get_help(self, ctx: click.Context) -> str:
        """Render help output, prefixing the banner for interactive root help."""
        help_text = super().get_help(ctx)
        if not _should_show_banner(ctx):
            return help_text
        return f"{_render_banner()}\n\n{help_text}"

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Group top-level commands by workflow in root help output."""
        if ctx.parent is not None:
            super().format_commands(ctx, formatter)
            return

        visible_commands = {}
        for name in self.list_commands(ctx):
            command = self.get_command(ctx, name)
            if command is None or command.hidden:
                continue
            visible_commands[name] = command

        if not visible_commands:
            return

        formatter.write_paragraph()
        emitted = set()
        sections = []

        for title, command_names in TOP_LEVEL_COMMAND_GROUPS:
            rows = []
            for name in command_names:
                command = visible_commands.get(name)
                if command is None:
                    continue
                emitted.add(name)
                rows.append((name, command.get_short_help_str()))
            if rows:
                sections.append((title, rows))

        other_rows = []
        for name in self.list_commands(ctx):
            if name in emitted or name not in visible_commands:
                continue
            other_rows.append((name, visible_commands[name].get_short_help_str()))
        if other_rows:
            sections.append(("Other Commands", other_rows))

        for index, (title, rows) in enumerate(sections):
            with formatter.section(title):
                formatter.write_dl(rows)
            if index < len(sections) - 1:
                formatter.write_paragraph()


class AttioCommand(click.Command):
    """Click command with optional examples and cross-references."""

    def __init__(
        self,
        *args,
        examples: list[str] | None = None,
        see_also: list[str] | None = None,
        **kwargs,
    ):
        self.examples = examples or []
        self.see_also = see_also or []
        super().__init__(*args, **kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Render standard help plus optional example sections."""
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_options(ctx, formatter)
        self._format_examples(formatter)
        self._format_see_also(formatter)
        self.format_epilog(ctx, formatter)

    def _format_examples(self, formatter: click.HelpFormatter) -> None:
        """Append a section of task-oriented examples."""
        if not self.examples:
            return
        formatter.write_paragraph()
        with formatter.section("Examples"):
            for index, example in enumerate(self.examples):
                formatter.write_text(example)
                if index < len(self.examples) - 1:
                    formatter.write_paragraph()

    def _format_see_also(self, formatter: click.HelpFormatter) -> None:
        """Append related commands when provided."""
        if not self.see_also:
            return
        formatter.write_paragraph()
        with formatter.section("See Also"):
            for related in self.see_also:
                formatter.write_text(related)


def _show_llm_guide(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Print the LLM-oriented operating guide and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(LLM_GUIDE)
    ctx.exit()


CLI_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(cls=AttioGroup, context_settings=CLI_CONTEXT_SETTINGS)
@click.option(
    "--llm",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_show_llm_guide,
    help="Print a machine-oriented usage guide and exit.",
)
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
    auth_state = resolve_auth_state()
    click.echo(f"Config file: {auth_state.config_path}")
    click.echo(f"Auth source: {auth_state.source}")
    click.echo(f"Preferred local storage: {auth_state.preferred_storage}")
    if auth_state.api_key:
        masked = auth_state.api_key[:8] + "..." + auth_state.api_key[-4:]
        click.echo(f"API key: {masked}")
    else:
        click.echo("API key: (not set)")


def _save_api_key_and_echo(api_key: str) -> None:
    """Persist an API key and explain where it was saved."""
    storage = set_api_key(api_key)
    if storage == AUTH_SOURCE_CONFIG:
        click.echo("API key saved to config file because system keychain storage is unavailable.")
        return
    click.echo("API key saved to system keychain.")


@config.command("login")
@click.argument("api_key", required=False)
def config_login(api_key: str | None):
    """Save an API key for local CLI usage."""
    if not api_key:
        api_key = click.prompt("Attio API key", hide_input=True)
    _save_api_key_and_echo(api_key)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value."""
    if key == "api-key":
        _save_api_key_and_echo(value)
    else:
        raise click.ClickException(f"Unknown config key: {key}")


@config.command("logout")
def config_logout():
    """Remove locally saved API credentials."""
    removed_sources = delete_api_key()
    if not removed_sources:
        click.echo("No saved API key found.")
    elif len(removed_sources) == 1:
        click.echo(f"Removed saved API key from {removed_sources[0]}.")
    else:
        joined = " and ".join(removed_sources)
        click.echo(f"Removed saved API key from {joined}.")

    if resolve_auth_state().source == AUTH_SOURCE_ENV:
        click.echo("ATTIO_API_KEY is still set in the environment and will continue to be used.")


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


@objects.command("retrieve")
@click.argument("object")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def objects_retrieve(object: str, as_json: bool):
    """Retrieve object details."""
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
):
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
def records_retrieve(object: str, record_id: str, as_json: bool):
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
def records_create(object: str, data: str, data_json: str, data_file: str, as_json: bool):
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
):
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
def records_search(object: str, query: str, limit: int, as_json: bool):
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
def records_entries(object: str, record_id: str, limit: int, offset: int, as_json: bool):
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
):
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


@lists.command("retrieve")
@click.argument("list_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def lists_retrieve(list_id: str, as_json: bool):
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
def lists_update(list_id: str, data: str, data_json: str, data_file: str, as_json: bool):
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
):
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
def entries_retrieve(list_id: str, entry_id: str, as_json: bool):
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
):
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
):
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
):
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


@tasks.command("retrieve")
@click.argument("task_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def tasks_retrieve(task_id: str, as_json: bool):
    """Retrieve a task by ID."""
    with get_client() as client:
        response = client.get(f"/tasks/{task_id}")
        output_one(response["data"], TASK_COLUMNS, as_json)


@tasks.command("create", cls=AttioCommand, examples=TASKS_CREATE_EXAMPLES)
@click.argument("content")
@click.option("--deadline", help="Deadline (ISO 8601 format)")
@click.option("--assignees", help="Assignees as JSON array")
@click.option("--assignees-file", help="Read assignees JSON from file or '-' for stdin")
@click.option("--linked-records", help="Linked records as JSON array")
@click.option(
    "--linked-records-file",
    help="Read linked records JSON from file or '-' for stdin",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def tasks_create(
    content: str,
    deadline: str,
    assignees: str,
    assignees_file: str,
    linked_records: str,
    linked_records_file: str,
    as_json: bool,
):
    """Create a new task."""
    data = {"content": content, "format": "plaintext"}
    if deadline:
        data["deadline_at"] = deadline
    assignee_value = get_json_input(
        data=assignees,
        data_file=assignees_file,
        required=False,
        context="assignees JSON",
        allow_stdin=False,
    )
    if assignee_value is not None:
        data["assignees"] = assignee_value
    linked_record_value = get_json_input(
        data=linked_records,
        data_file=linked_records_file,
        required=False,
        context="linked records JSON",
        allow_stdin=False,
    )
    if linked_record_value is not None:
        data["linked_records"] = linked_record_value

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


@notes.command("retrieve")
@click.argument("note_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def notes_retrieve(note_id: str, as_json: bool):
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
    """Manage attributes for objects and lists."""
    pass


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
def attributes_list(identifier: str, target: str, as_json: bool):
    """List attributes for an object or list."""
    with get_client() as client:
        response = client.get(_attribute_path(target, identifier))
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
def attributes_retrieve(identifier: str, attribute: str, target: str, as_json: bool):
    """Retrieve attribute details."""
    with get_client() as client:
        response = client.get(_attribute_path(target, identifier, f"/{attribute}"))
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
):
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
            _attribute_path(target, identifier),
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
):
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
            _attribute_path(target, identifier, f"/{attribute}"),
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
):
    """List select options for an attribute."""
    params = {"show_archived": "true"} if show_archived else None
    with get_client() as client:
        response = client.get(
            _attribute_path(target, identifier, f"/{attribute}/options"),
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
):
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
            _attribute_path(target, identifier, f"/{attribute}/options"),
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
):
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
            _attribute_path(target, identifier, f"/{attribute}/options/{option_id}"),
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
):
    """List status options for an attribute."""
    params = {"show_archived": "true"} if show_archived else None
    with get_client() as client:
        response = client.get(
            _attribute_path(target, identifier, f"/{attribute}/statuses"),
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
):
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
            _attribute_path(target, identifier, f"/{attribute}/statuses"),
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
):
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
            _attribute_path(target, identifier, f"/{attribute}/statuses/{status_id}"),
            {"data": payload},
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


@members.command("retrieve")
@click.argument("member_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def members_retrieve(member_id: str, as_json: bool):
    """Retrieve member details."""
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


@webhooks.command("retrieve")
@click.argument("webhook_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def webhooks_retrieve(webhook_id: str, as_json: bool):
    """Retrieve webhook details."""
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
