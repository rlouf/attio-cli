from unittest.mock import patch

from attio_cli.main import cli


def test_root_help_supports_short_flag(runner):
    result = runner.invoke(cli, ["-h"])

    assert result.exit_code == 0
    assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output


def test_group_help_supports_short_flag(runner):
    result = runner.invoke(cli, ["records", "-h"])

    assert result.exit_code == 0
    assert "Usage: cli records [OPTIONS] COMMAND [ARGS]..." in result.output


def test_root_help_hides_banner_for_non_tty(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "A CLI for Attio" not in result.output
    assert "Getting Started:" in result.output
    assert "CRM Data:" in result.output
    assert "Schema:" in result.output
    assert "Workspace:" in result.output

    config_index = result.output.index("config")
    records_index = result.output.index("records")
    objects_index = result.output.index("objects")
    members_index = result.output.index("members")

    assert config_index < records_index < objects_index < members_index


def test_root_help_shows_banner_for_tty(runner):
    with patch("attio_cli.cli_core.should_show_banner", return_value=True):
        result = runner.invoke(cli, ["--help"], color=False)

    assert result.exit_code == 0
    assert "A CLI for Attio" in result.output
    assert "@@@@@@@@@." in result.output


def test_root_llm_flag_prints_machine_guide(runner):
    result = runner.invoke(cli, ["--llm"])

    assert result.exit_code == 0
    assert "ATTIO CLI LLM GUIDE" in result.output
    assert "Structured JSON input precedence:" in result.output
    assert "Identifier conventions:" in result.output
    assert "Command inventory:" in result.output
    assert "records: list, retrieve, create, update, search, entries, values" in result.output
    assert "Delete operations are intentionally not implemented in this CLI." in result.output


def test_examples_are_shown_for_annotated_command_help(runner):
    result = runner.invoke(cli, ["records", "create", "--help"])

    assert result.exit_code == 0
    assert "Examples:" in result.output
    assert "attio records create people --data" in result.output
    assert 'echo \'{"name": "Jane Doe"' in result.output


def test_examples_are_shown_for_complex_attribute_command_help(runner):
    result = runner.invoke(cli, ["attributes", "update-status", "--help"])

    assert result.exit_code == 0
    assert "Examples:" in result.output
    assert "attio attributes update-status <list-id> stage <status-id>" in result.output
    assert "--target-time-in-status-file target-time.json" in result.output


def test_non_annotated_help_does_not_show_examples_section(runner):
    result = runner.invoke(cli, ["records", "retrieve", "--help"])

    assert result.exit_code == 0
    assert "Examples:" not in result.output
