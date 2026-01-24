"""Output formatting for Attio CLI."""

import json
import sys
from typing import Any, Callable

from rich.console import Console
from rich.table import Table

console = Console()


def print_json(data: Any) -> None:
    """Print data as JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_jsonl(items: list[Any]) -> None:
    """Print items as JSONL (one JSON object per line)."""
    for item in items:
        print(json.dumps(item, default=str))


def print_table(
    items: list[dict],
    columns: list[tuple[str, Callable[[dict], str]]],
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
    item: dict,
    columns: list[tuple[str, Callable[[dict], str]]],
) -> None:
    """Print a single item as a table."""
    print_table([item], columns)


def output_many(
    items: list[dict],
    columns: list[tuple[str, Callable[[dict], str]]],
    as_json: bool = False,
) -> None:
    """Output multiple items (table or JSONL)."""
    if as_json:
        print_jsonl(items)
    else:
        print_table(items, columns)


def output_one(
    item: dict,
    columns: list[tuple[str, Callable[[dict], str]]],
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


def get_json_input(data: str | None) -> dict:
    """Get JSON input from argument or stdin.

    Args:
        data: JSON string or None to read from stdin

    Returns:
        Parsed JSON as dictionary

    Raises:
        click.ClickException: If no data provided or invalid JSON
    """
    import click

    if data:
        input_str = data
    elif is_stdin_piped():
        input_str = read_stdin()
    else:
        raise click.ClickException("Missing JSON data. Provide as argument or pipe via stdin.")

    try:
        return json.loads(input_str)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}") from None
