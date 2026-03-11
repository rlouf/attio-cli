"""Output formatting for Attio CLI."""

import json
import sys
from typing import Any, Callable

from rich.console import Console
from rich.table import Table

console = Console()
Row = dict[str, Any]
ColumnExtractor = Callable[[Row], str]
ColumnSpec = tuple[str, ColumnExtractor]


def print_json(data: Any) -> None:
    """Print data as JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_jsonl(items: list[Any]) -> None:
    """Print items as JSONL (one JSON object per line)."""
    for item in items:
        print(json.dumps(item, default=str))


def print_table(
    items: list[Row],
    columns: list[ColumnSpec],
) -> None:
    """Print items as a table.

    Args:
        items: List of dictionaries to display
        columns: List of (header, extractor) tuples
    """
    if not items:
        console.print("[dim]No results[/dim]")
        return

    table = Table(show_header=True, header_style="bold")
    for header, _ in columns:
        table.add_column(header)

    for item in items:
        row = [extractor(item) for _, extractor in columns]
        table.add_row(*row)

    console.print(table)


def print_single_table(
    item: Row,
    columns: list[ColumnSpec],
) -> None:
    """Print a single item as a table."""
    print_table([item], columns)


def output_many(
    items: list[Row],
    columns: list[ColumnSpec],
    as_json: bool = False,
) -> None:
    """Output multiple items (table or JSONL)."""
    if as_json:
        print_jsonl(items)
    else:
        print_table(items, columns)


def output_one(
    item: Row,
    columns: list[ColumnSpec],
    as_json: bool = False,
) -> None:
    """Output a single item (table or JSON)."""
    if as_json:
        print_json(item)
    else:
        print_single_table(item, columns)


def is_stdin_piped() -> bool:
    """Check if stdin has piped data."""
    return not sys.stdin.isatty()


def read_stdin() -> str:
    """Read all data from stdin."""
    return sys.stdin.read()


def _load_json(text: str, context: str) -> Any:
    """Load JSON text with a consistent error message."""
    import click

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON for {context}: {e}") from None


def _read_json_file(path: str) -> str:
    """Read JSON content from a file path or stdin."""
    if path == "-":
        return read_stdin()

    with open(path) as f:
        return f.read()


def get_json_input(
    positional_data: str | None = None,
    *,
    data: str | None = None,
    data_file: str | None = None,
    required: bool = True,
    context: str = "input",
    allow_stdin: bool = True,
) -> Any:
    """Get JSON input from a single supported source.

    Args:
        positional_data: Legacy positional JSON string
        data: JSON string from an explicit flag
        data_file: File path to read JSON from, or '-' for stdin
        required: Whether a value must be provided
        context: Context name for error messages
        allow_stdin: Whether piped stdin is accepted as an implicit source

    Returns:
        Parsed JSON value

    Raises:
        click.ClickException: If inputs conflict, are missing, or invalid
    """
    import click

    explicit_sources = [
        name
        for name, value in [
            ("positional argument", positional_data),
            ("--data", data),
            ("--data-file", data_file),
        ]
        if value is not None
    ]
    if len(explicit_sources) > 1:
        joined = ", ".join(explicit_sources)
        raise click.ClickException(f"Provide {context} via only one source, not: {joined}")

    if positional_data is not None:
        input_str = positional_data
    elif data is not None:
        input_str = data
    elif data_file is not None:
        input_str = _read_json_file(data_file)
    elif allow_stdin and is_stdin_piped():
        input_str = read_stdin()
    elif required:
        raise click.ClickException(
            f"Missing {context}. Provide --data, --data-file, a positional JSON argument, or pipe via stdin."
        )
    else:
        return None

    if not input_str.strip():
        if required:
            raise click.ClickException(f"Missing {context}. JSON input was empty.")
        return None

    return _load_json(input_str, context)
