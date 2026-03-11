from attio.main import cli


def test_records_create_uses_data_flag(runner, recording_client_factory, patch_command_clients):
    client = recording_client_factory()
    client.queue_response(
        "POST", "/objects/people/records", {"data": {"id": {"record_id": "rec_1"}}}
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        ["records", "create", "people", "--data", '{"name": "Jane Doe"}', "--json"],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/objects/people/records",
            "params": None,
            "json": {"data": {"values": {"name": "Jane Doe"}}},
        }
    ]


def test_records_create_rejects_multiple_json_sources(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    patch_command_clients(recording_client_factory())

    result = runner.invoke(
        cli,
        [
            "records",
            "create",
            "people",
            '{"name": "Positional"}',
            "--data",
            '{"name": "Flag"}',
        ],
    )

    assert result.exit_code == 1
    assert "Provide record values JSON via only one source" in result.output


def test_records_update_uses_put_when_overwrite(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response(
        "PUT",
        "/objects/people/records/rec_1",
        {"data": {"id": {"record_id": "rec_1"}}},
    )
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "records",
            "update",
            "people",
            "rec_1",
            "--data",
            '{"regions": ["EMEA"]}',
            "--overwrite",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PUT",
            "path": "/objects/people/records/rec_1",
            "params": None,
            "json": {"data": {"values": {"regions": ["EMEA"]}}},
        }
    ]


def test_records_list_reads_filter_and_sort_files(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("POST", "/objects/people/records/query", {"data": []})
    patch_command_clients(client)

    with runner.isolated_filesystem():
        with open("filter.json", "w") as f:
            f.write('{"name": "Jane"}')
        with open("sort.json", "w") as f:
            f.write('[{"field": "name", "direction": "asc"}]')

        result = runner.invoke(
            cli,
            [
                "records",
                "list",
                "people",
                "--limit",
                "10",
                "--offset",
                "5",
                "--filter-file",
                "filter.json",
                "--sort-file",
                "sort.json",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/objects/people/records/query",
            "params": None,
            "json": {
                "limit": 10,
                "offset": 5,
                "filter": {"name": "Jane"},
                "sorts": [{"field": "name", "direction": "asc"}],
            },
        }
    ]


def test_records_search_sends_limit(runner, recording_client_factory, patch_command_clients):
    client = recording_client_factory()
    client.queue_response("POST", "/objects/records/search", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(cli, ["records", "search", "people", "jane", "--limit", "3", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/objects/records/search",
            "params": None,
            "json": {"query": "jane", "objects": ["people"], "limit": 3},
        }
    ]
