"""Webhook commands."""

import click

from attio.columns import WEBHOOK_COLUMNS
from attio.commands.common import get_client
from attio.output import output_many, output_one


@click.group()
def webhooks() -> None:
    """Manage webhooks."""


@webhooks.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSONL")
def webhooks_list(as_json: bool) -> None:
    """List webhooks."""
    with get_client() as client:
        response = client.get("/webhooks")
        output_many(response["data"], WEBHOOK_COLUMNS, as_json)


@webhooks.command("retrieve")
@click.argument("webhook_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def webhooks_retrieve(webhook_id: str, as_json: bool) -> None:
    """Retrieve webhook details."""
    with get_client() as client:
        response = client.get(f"/webhooks/{webhook_id}")
        output_one(response["data"], WEBHOOK_COLUMNS, as_json)


@webhooks.command("create")
@click.option("--target-url", required=True, help="Target URL")
@click.option("--subscriptions", required=True, help="Comma-separated event types")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def webhooks_create(target_url: str, subscriptions: str, as_json: bool) -> None:
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
def webhooks_update(webhook_id: str, target_url: str, subscriptions: str, as_json: bool) -> None:
    """Update a webhook."""
    data = {}
    if target_url:
        data["target_url"] = target_url
    if subscriptions:
        data["subscriptions"] = [{"event_type": s.strip()} for s in subscriptions.split(",")]

    with get_client() as client:
        response = client.patch(f"/webhooks/{webhook_id}", {"data": data})
        output_one(response["data"], WEBHOOK_COLUMNS, as_json)
