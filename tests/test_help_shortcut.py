from io import StringIO
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


def test_root_help_shows_banner_for_tty():
    class TtyStringIO(StringIO):
        def isatty(self):
            return True

    stdout = TtyStringIO()
    stderr = TtyStringIO()
    runner = CliRunner()

    with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
        result = runner.invoke(cli, ["--help"], color=False)

    assert result.exit_code == 0
    assert "A CLI for Attio" in result.output
    assert "@@@@@@@@@." in result.output
