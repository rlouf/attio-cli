from unittest.mock import patch

from click.testing import CliRunner

from attio_cli.client import AUTH_SETUP_HINT, AttioError
from attio_cli.main import cli


class FailingClient:
    def __init__(self, error: AttioError):
        self.error = error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, path, params=None):
        raise self.error


def test_missing_api_key_is_actionable():
    with patch("attio_cli.main.get_api_key", return_value=None):
        result = CliRunner().invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert f"Error: No API key configured. {AUTH_SETUP_HINT}" in result.output


def test_unauthorized_api_error_includes_auth_hint():
    error = AttioError(
        "Unauthorized.",
        status_code=401,
        details="Invalid API key",
        hint=AUTH_SETUP_HINT,
    )

    with patch("attio_cli.main.get_client", return_value=FailingClient(error)):
        result = CliRunner().invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert "Error: Unauthorized." in result.output
    assert "Details: Invalid API key" in result.output
    assert f"Hint: {AUTH_SETUP_HINT}" in result.output


def test_not_found_api_error_is_normalized():
    error = AttioError(
        "Resource not found.",
        status_code=404,
        details="Record was not found",
        hint="Check the resource identifier and try again.",
    )

    with patch("attio_cli.main.get_client", return_value=FailingClient(error)):
        result = CliRunner().invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert "Error: Resource not found." in result.output
    assert "Details: Record was not found" in result.output
    assert "Hint: Check the resource identifier and try again." in result.output


def test_network_error_is_normalized():
    error = AttioError(
        "Network error contacting Attio API.",
        details="temporary dns failure",
        hint="Check your network connection and try again.",
    )

    with patch("attio_cli.main.get_client", return_value=FailingClient(error)):
        result = CliRunner().invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert "Error: Network error contacting Attio API." in result.output
    assert "Details: temporary dns failure" in result.output
    assert "Hint: Check your network connection and try again." in result.output
