from attio.main import cli


def test_objects_list_hits_objects_endpoint(
    runner, recording_client_factory, patch_command_clients
):
    client = recording_client_factory()
    client.queue_response("GET", "/objects", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(cli, ["objects", "list", "--json"])

    assert result.exit_code == 0
    assert client.calls == [{"method": "GET", "path": "/objects", "params": None, "json": None}]


def test_objects_retrieve_hits_object_endpoint(
    runner, recording_client_factory, patch_command_clients
):
    client = recording_client_factory()
    client.queue_response("GET", "/objects/people", {"data": {"id": {"object_id": "obj_1"}}})
    patch_command_clients(client)

    result = runner.invoke(cli, ["objects", "retrieve", "people", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {"method": "GET", "path": "/objects/people", "params": None, "json": None}
    ]


def test_members_retrieve_hits_member_endpoint(
    runner, recording_client_factory, patch_command_clients
):
    client = recording_client_factory()
    client.queue_response(
        "GET",
        "/workspace_members/member_1",
        {"data": {"id": {"workspace_member_id": "member_1"}}},
    )
    patch_command_clients(client)

    result = runner.invoke(cli, ["members", "retrieve", "member_1", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "GET",
            "path": "/workspace_members/member_1",
            "params": None,
            "json": None,
        }
    ]


def test_webhooks_create_splits_subscriptions(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "POST",
        "/webhooks",
        {"data": {"id": {"webhook_id": "webhook_1"}}},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "webhooks",
            "create",
            "--target-url",
            "https://example.com/webhook",
            "--subscriptions",
            "record.created,record.updated",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/webhooks",
            "params": None,
            "json": {
                "data": {
                    "target_url": "https://example.com/webhook",
                    "subscriptions": [
                        {"event_type": "record.created"},
                        {"event_type": "record.updated"},
                    ],
                }
            },
        }
    ]


def test_webhooks_update_splits_subscriptions(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "PATCH",
        "/webhooks/webhook_1",
        {"data": {"id": {"webhook_id": "webhook_1"}}},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "webhooks",
            "update",
            "webhook_1",
            "--target-url",
            "https://example.com/webhook",
            "--subscriptions",
            "record.created,record.updated",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/webhooks/webhook_1",
            "params": None,
            "json": {
                "data": {
                    "target_url": "https://example.com/webhook",
                    "subscriptions": [
                        {"event_type": "record.created"},
                        {"event_type": "record.updated"},
                    ],
                }
            },
        }
    ]
