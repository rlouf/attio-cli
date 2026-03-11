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
