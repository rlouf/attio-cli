from attio.main import cli


def test_tasks_list_sends_limit_and_offset(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("POST", "/tasks/query", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(cli, ["tasks", "list", "--limit", "3", "--offset", "1", "--json"])

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/tasks/query",
            "params": None,
            "json": {"limit": 3, "offset": 1},
        }
    ]


def test_tasks_create_reads_json_file_flags(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("POST", "/tasks", {"data": {"id": {"task_id": "task_1"}}})
    patch_command_clients(client)

    with runner.isolated_filesystem():
        with open("assignees.json", "w") as f:
            f.write('[{"workspace_member_id": "member_1"}]')
        with open("linked-records.json", "w") as f:
            f.write('[{"target_object": "people", "target_record_id": "rec_1"}]')

        result = runner.invoke(
            cli,
            [
                "tasks",
                "create",
                "Follow up",
                "--deadline",
                "2026-03-12T10:00:00Z",
                "--assignees-file",
                "assignees.json",
                "--linked-records-file",
                "linked-records.json",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/tasks",
            "params": None,
            "json": {
                "data": {
                    "content": "Follow up",
                    "format": "plaintext",
                    "deadline_at": "2026-03-12T10:00:00Z",
                    "assignees": [{"workspace_member_id": "member_1"}],
                    "linked_records": [{"target_object": "people", "target_record_id": "rec_1"}],
                }
            },
        }
    ]


def test_tasks_update_shapes_patch_body(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("PATCH", "/tasks/task_1", {"data": {"id": {"task_id": "task_1"}}})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "tasks",
            "update",
            "task_1",
            "--content",
            "Follow up with prospect",
            "--completed",
            "true",
            "--deadline",
            "2026-03-15T09:00:00Z",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/tasks/task_1",
            "params": None,
            "json": {
                "data": {
                    "content": "Follow up with prospect",
                    "format": "plaintext",
                    "is_completed": True,
                    "deadline_at": "2026-03-15T09:00:00Z",
                }
            },
        }
    ]


def test_notes_list_sends_parent_filters(
    runner,
    recording_client_factory,
    patch_command_clients,
):
    client = recording_client_factory()
    client.queue_response("POST", "/notes/query", {"data": []})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "notes",
            "list",
            "--parent-object",
            "people",
            "--parent-record-id",
            "rec_1",
            "--limit",
            "5",
            "--offset",
            "2",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/notes/query",
            "params": None,
            "json": {
                "limit": 5,
                "offset": 2,
                "parent_object": "people",
                "parent_record_id": "rec_1",
            },
        }
    ]


def test_notes_create_shapes_request_body(runner, recording_client_factory, patch_command_clients):
    client = recording_client_factory()
    client.queue_response("POST", "/notes", {"data": {"id": {"note_id": "note_1"}}})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "notes",
            "create",
            "--title",
            "Meeting Notes",
            "--parent-object",
            "people",
            "--parent-record-id",
            "rec_1",
            "--content",
            "Discussion points",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "POST",
            "path": "/notes",
            "params": None,
            "json": {
                "data": {
                    "parent_object": "people",
                    "parent_record_id": "rec_1",
                    "title": "Meeting Notes",
                    "format": "plaintext",
                    "content": "Discussion points",
                }
            },
        }
    ]


def test_notes_update_shapes_patch_body(runner, recording_client_factory, patch_command_clients):
    client = recording_client_factory()
    client.queue_response("PATCH", "/notes/note_1", {"data": {"id": {"note_id": "note_1"}}})
    patch_command_clients(client)

    result = runner.invoke(
        cli,
        [
            "notes",
            "update",
            "note_1",
            "--title",
            "Dotty Research",
            "--content",
            "Last updated: 2026-03-21",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert client.calls == [
        {
            "method": "PATCH",
            "path": "/notes/note_1",
            "params": None,
            "json": {
                "data": {
                    "title": "Dotty Research",
                    "content": "Last updated: 2026-03-21",
                    "format": "plaintext",
                }
            },
        }
    ]
