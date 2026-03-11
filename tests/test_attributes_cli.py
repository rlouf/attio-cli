from attio.main import cli


def test_attributes_list_defaults_to_object_target(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("GET", "/objects/people/attributes", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(cli, ["attributes", "list", "people", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "GET",
            "path": "/objects/people/attributes",
            "params": None,
            "json": None,
        }
    ]


def test_attributes_create_for_list_target_uses_flag_fields(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("POST", "/lists/list_1/attributes", {"data": {"api_slug": "stage"}})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "attributes",
            "create",
            "list_1",
            "--target",
            "lists",
            "--title",
            "Stage",
            "--type",
            "status",
            "--slug",
            "stage",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/lists/list_1/attributes",
            "params": None,
            "json": {"data": {"title": "Stage", "type": "status", "api_slug": "stage"}},
        }
    ]


def test_attributes_list_uses_list_target(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("GET", "/lists/list_1/attributes", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(cli, ["attributes", "list", "list_1", "--target", "lists", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "GET",
            "path": "/lists/list_1/attributes",
            "params": None,
            "json": None,
        }
    ]


def test_attributes_update_combines_flags_and_json_payload(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "PATCH",
        "/objects/people/attributes/region",
        {"data": {"api_slug": "sales_region"}},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "attributes",
            "update",
            "people",
            "region",
            "--data",
            '{"description": "Sales territory"}',
            "--title",
            "Sales Region",
            "--slug",
            "sales_region",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/objects/people/attributes/region",
            "params": None,
            "json": {
                "data": {
                    "description": "Sales territory",
                    "title": "Sales Region",
                    "api_slug": "sales_region",
                }
            },
        }
    ]


def test_attributes_update_requires_a_change(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    patch_command_clients(recording_client_factory())

    result = runner.invoke(cli, ["attributes", "update", "people", "region"])

    assert result.exit_code == 1
    assert "Provide update JSON or at least one field to change." in result.output


def test_attributes_options_includes_show_archived(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("GET", "/objects/people/attributes/region/options", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        ["attributes", "options", "people", "region", "--show-archived", "--json"],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "GET",
            "path": "/objects/people/attributes/region/options",
            "params": {"show_archived": "true"},
            "json": None,
        }
    ]


def test_attributes_add_status_uses_target_time_file(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "POST",
        "/lists/list_1/attributes/stage/statuses",
        {"data": {"id": {"status_id": "status_1"}}},
    )
    patch_command_clients(client)

    with runner.isolated_filesystem():
        with open("target-time.json", "w") as f:
            f.write('{"unit": "days", "value": 7}')

        result = runner.invoke(
            cli,
            [
                "attributes",
                "add-status",
                "list_1",
                "stage",
                "--target",
                "lists",
                "--title",
                "Qualified",
                "--celebration-enabled",
                "true",
                "--target-time-in-status-file",
                "target-time.json",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/lists/list_1/attributes/stage/statuses",
            "params": None,
            "json": {
                "data": {
                    "title": "Qualified",
                    "celebration_enabled": True,
                    "target_time_in_status": {"unit": "days", "value": 7},
                }
            },
        }
    ]


def test_attributes_statuses_include_show_archived_for_lists(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("GET", "/lists/list_1/attributes/stage/statuses", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "attributes",
            "statuses",
            "list_1",
            "stage",
            "--target",
            "lists",
            "--show-archived",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "GET",
            "path": "/lists/list_1/attributes/stage/statuses",
            "params": {"show_archived": "true"},
            "json": None,
        }
    ]


def test_attributes_update_option_archives_option(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "PATCH",
        "/objects/people/attributes/region/options/opt_1",
        {"data": {"id": {"option_id": "opt_1"}}},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "attributes",
            "update-option",
            "people",
            "region",
            "opt_1",
            "--archived",
            "true",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/objects/people/attributes/region/options/opt_1",
            "params": None,
            "json": {"data": {"is_archived": True}},
        }
    ]


def test_attributes_update_status_combines_flags_and_json_sources(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "PATCH",
        "/lists/list_1/attributes/stage/statuses/status_1",
        {"data": {"id": {"status_id": "status_1"}}},
    )
    patch_command_clients(client)

    with runner.isolated_filesystem():
        with open("target-time.json", "w") as f:
            f.write('{"unit": "days", "value": 14}')

        result = runner.invoke(
            cli,
            [
                "attributes",
                "update-status",
                "list_1",
                "stage",
                "status_1",
                "--target",
                "lists",
                "--data",
                '{"description": "Sales-qualified pipeline stage"}',
                "--title",
                "Sales Qualified",
                "--archived",
                "false",
                "--celebration-enabled",
                "true",
                "--target-time-in-status-file",
                "target-time.json",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/lists/list_1/attributes/stage/statuses/status_1",
            "params": None,
            "json": {
                "data": {
                    "description": "Sales-qualified pipeline stage",
                    "title": "Sales Qualified",
                    "is_archived": False,
                    "celebration_enabled": True,
                    "target_time_in_status": {"unit": "days", "value": 14},
                }
            },
        }
    ]
