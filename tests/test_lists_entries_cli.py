from attio_cli.main import cli


def test_lists_update_reads_data_file(runner, recording_client_factory, patch_command_clients):
    client = recording_client_factory()
    client.queue_response("PATCH", "/lists/list_1", {"data": {"id": {"list_id": "list_1"}}})
    patch_command_clients(client)

    with runner.isolated_filesystem():
        with open("list-update.json", "w") as f:
            f.write('{"name": "Enterprise Pipeline"}')

        result = runner.invoke(
            cli,
            ["lists", "update", "list_1", "--data-file", "list-update.json", "--json"],
        )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/lists/list_1",
            "params": None,
            "json": {"data": {"name": "Enterprise Pipeline"}},
        }
    ]


def test_entries_create_reads_stdin_json(runner, recording_client_factory, patch_command_clients):
    client = recording_client_factory()
    client.queue_response(
        "POST", "/lists/list_1/entries", {"data": {"id": {"entry_id": "entry_1"}}}
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        ["entries", "create", "list_1", "--record-id", "rec_1", "--json"],
        input='{"status": "active"}',
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/lists/list_1/entries",
            "params": None,
            "json": {
                "data": {
                    "parent_record_id": "rec_1",
                    "entry_values": {"status": "active"},
                }
            },
        }
    ]


def test_entries_create_without_json_only_sends_record_id(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "POST", "/lists/list_1/entries", {"data": {"id": {"entry_id": "entry_1"}}}
    )
    patch_command_clients(client)

    result = runner.invoke(cli, ["entries", "create", "list_1", "--record-id", "rec_1", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/lists/list_1/entries",
            "params": None,
            "json": {"data": {"parent_record_id": "rec_1"}},
        }
    ]


def test_entries_update_uses_patch_by_default(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "PATCH",
        "/lists/list_1/entries/entry_1",
        {"data": {"id": {"entry_id": "entry_1"}}},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "entries",
            "update",
            "list_1",
            "entry_1",
            "--data",
            '{"status": "qualified"}',
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/lists/list_1/entries/entry_1",
            "params": None,
            "json": {"data": {"entry_values": {"status": "qualified"}}},
        }
    ]


def test_entries_values_sends_query_params(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "GET",
        "/lists/list_1/entries/entry_1/attributes/status/values",
        {"data": []},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "entries",
            "values",
            "list_1",
            "entry_1",
            "status",
            "--show-historic",
            "--limit",
            "2",
            "--offset",
            "1",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "GET",
            "path": "/lists/list_1/entries/entry_1/attributes/status/values",
            "params": {"show_historic": "true", "limit": 2, "offset": 1},
            "json": None,
        }
    ]


def test_entries_list_reads_filter_and_sort_files(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("POST", "/lists/list_1/entries/query", {"data": []})
    patch_command_clients(client)

    with runner.isolated_filesystem():
        with open("entry-filter.json", "w") as f:
            f.write('{"status": "qualified"}')
        with open("entry-sort.json", "w") as f:
            f.write('[{"field": "status", "direction": "desc"}]')

        result = runner.invoke(
            cli,
            [
                "entries",
                "list",
                "list_1",
                "--filter-file",
                "entry-filter.json",
                "--sort-file",
                "entry-sort.json",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/lists/list_1/entries/query",
            "params": None,
            "json": {
                "filter": {"status": "qualified"},
                "sorts": [{"field": "status", "direction": "desc"}],
            },
        }
    ]
