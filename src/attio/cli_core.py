"""Shared CLI help, examples, and root command behavior."""

import os

import click

from attio.client import AttioError

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

CLI_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def render_banner() -> str:
    """Render the help banner with a centered wordmark."""
    width = max(len(line) for line in BANNER_LINES)
    wordmark = BANNER_WORDMARK.center(width)
    return "\n".join([*BANNER_LINES, "", wordmark])


def should_show_banner(ctx: click.Context) -> bool:
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
        if not should_show_banner(ctx):
            return help_text
        return f"{render_banner()}\n\n{help_text}"

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


def show_llm_guide(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Print the LLM-oriented operating guide and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(LLM_GUIDE)
    ctx.exit()
