"""Task commands."""

import click

from attio_cli.cli_core import TASKS_CREATE_EXAMPLES, AttioCommand
from attio_cli.columns import TASK_COLUMNS
from attio_cli.commands.common import get_client
from attio_cli.output import get_json_input, output_many, output_one


@click.group()
def tasks() -> None:
    """Manage tasks."""


@tasks.command("list")
@click.option("--limit", type=int, help="Maximum number of tasks")
@click.option("--offset", type=int, help="Number of tasks to skip")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def tasks_list(limit: int, offset: int, as_json: bool) -> None:
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
def tasks_retrieve(task_id: str, as_json: bool) -> None:
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
) -> None:
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
def tasks_update(task_id: str, content: str, completed: bool, deadline: str, as_json: bool) -> None:
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
