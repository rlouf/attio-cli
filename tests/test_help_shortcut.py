from unittest.mock import patch

from click.testing import CliRunner

from attio_cli.main import cli


def test_root_help_supports_short_flag():
    result = CliRunner().invoke(cli, ["-h"])

    assert result.exit_code == 0
    assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output


def test_group_help_supports_short_flag():
    result = CliRunner().invoke(cli, ["records", "-h"])

    assert result.exit_code == 0
    assert "Usage: cli records [OPTIONS] COMMAND [ARGS]..." in result.output


def test_root_help_hides_banner_for_non_tty():
    result = CliRunner().invoke(cli, ["--help"])

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


def test_root_help_shows_banner_for_tty():
    runner = CliRunner()

    with patch("attio_cli.main._should_show_banner", return_value=True):
        result = runner.invoke(cli, ["--help"], color=False)

    assert result.exit_code == 0
    assert "A CLI for Attio" in result.output
    assert "@@@@@@@@@." in result.output


def test_root_llm_flag_prints_machine_guide():
    result = CliRunner().invoke(cli, ["--llm"])

    assert result.exit_code == 0
    assert "ATTIO CLI LLM GUIDE" in result.output
    assert "Structured JSON input precedence:" in result.output
    assert "Identifier conventions:" in result.output
    assert "Command inventory:" in result.output
    assert "records: list, retrieve, create, update, search, entries, values" in result.output
    assert "Delete operations are intentionally not implemented in this CLI." in result.output
