import click
import pytest

from attio import output


def test_get_json_input_uses_data_flag():
    assert output.get_json_input(data='{"name": "Jane"}', context="payload") == {"name": "Jane"}


def test_get_json_input_reads_data_file(tmp_path):
    path = tmp_path / "payload.json"
    path.write_text('{"name": "Jane"}')

    assert output.get_json_input(data_file=str(path), context="payload") == {"name": "Jane"}


def test_get_json_input_reads_stdin_when_allowed(monkeypatch):
    monkeypatch.setattr(output, "is_stdin_piped", lambda: True)
    monkeypatch.setattr(output, "read_stdin", lambda: '{"name": "Jane"}')

    assert output.get_json_input(context="payload") == {"name": "Jane"}


def test_get_json_input_rejects_multiple_sources():
    with pytest.raises(click.ClickException) as exc_info:
        output.get_json_input('{"name": "Positional"}', data='{"name": "Flag"}', context="payload")

    assert "Provide payload via only one source" in str(exc_info.value)


def test_get_json_input_rejects_empty_required_input(monkeypatch):
    monkeypatch.setattr(output, "is_stdin_piped", lambda: True)
    monkeypatch.setattr(output, "read_stdin", lambda: "   ")

    with pytest.raises(click.ClickException) as exc_info:
        output.get_json_input(context="payload")

    assert "Missing payload. JSON input was empty." in str(exc_info.value)


def test_get_json_input_reads_dash_data_file_from_stdin(monkeypatch):
    monkeypatch.setattr(output, "read_stdin", lambda: '{"name": "Jane"}')

    assert output.get_json_input(data_file="-", context="payload") == {"name": "Jane"}


def test_get_json_input_returns_none_when_optional_and_empty(monkeypatch):
    monkeypatch.setattr(output, "is_stdin_piped", lambda: True)
    monkeypatch.setattr(output, "read_stdin", lambda: "")

    assert output.get_json_input(required=False, context="payload") is None


def test_get_json_input_ignores_stdin_when_disabled(monkeypatch):
    monkeypatch.setattr(output, "is_stdin_piped", lambda: True)
    monkeypatch.setattr(output, "read_stdin", lambda: '{"name": "Ignored"}')

    assert output.get_json_input(required=False, allow_stdin=False, context="payload") is None


def test_get_json_input_rejects_invalid_json():
    with pytest.raises(click.ClickException) as exc_info:
        output.get_json_input(data="{invalid", context="payload")

    assert "Invalid JSON for payload" in str(exc_info.value)
