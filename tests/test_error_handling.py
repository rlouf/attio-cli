from unittest.mock import patch

from attio.client import AUTH_SETUP_HINT, AttioError
from attio.main import cli


def test_missing_api_key_is_actionable(runner):
    with patch("attio.main.get_api_key", return_value=None):
        result = runner.invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert f"Error: No API key configured. {AUTH_SETUP_HINT}" in result.output


def test_unauthorized_api_error_includes_auth_hint(runner, failing_client_factory):
    error = AttioError(
        "Unauthorized.",
        status_code=401,
        details="Invalid API key",
        hint=AUTH_SETUP_HINT,
    )

    with patch("attio.main.get_client", return_value=failing_client_factory(error)):
        result = runner.invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert "Error: Unauthorized." in result.output
    assert "Details: Invalid API key" in result.output
    assert f"Hint: {AUTH_SETUP_HINT}" in result.output


def test_not_found_api_error_is_normalized(runner, failing_client_factory):
    error = AttioError(
        "Resource not found.",
        status_code=404,
        details="Record was not found",
        hint="Check the resource identifier and try again.",
    )

    with patch("attio.main.get_client", return_value=failing_client_factory(error)):
        result = runner.invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert "Error: Resource not found." in result.output
    assert "Details: Record was not found" in result.output
    assert "Hint: Check the resource identifier and try again." in result.output


def test_network_error_is_normalized(runner, failing_client_factory):
    error = AttioError(
        "Network error contacting Attio API.",
        details="temporary dns failure",
        hint="Check your network connection and try again.",
    )

    with patch("attio.main.get_client", return_value=failing_client_factory(error)):
        result = runner.invoke(cli, ["whoami"])

    assert result.exit_code == 1
    assert "Error: Network error contacting Attio API." in result.output
    assert "Details: temporary dns failure" in result.output
    assert "Hint: Check your network connection and try again." in result.output
