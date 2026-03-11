import os
from unittest.mock import patch

from click.testing import CliRunner

from attio_cli import config
from attio_cli.main import cli


class FakeKeyring:
    def __init__(self, initial=None, fail_set=False):
        self.store = initial or {}
        self.fail_set = fail_set

    def get_password(self, service, username):
        return self.store.get((service, username))

    def set_password(self, service, username, password):
        if self.fail_set:
            raise RuntimeError("keychain unavailable")
        self.store[(service, username)] = password

    def delete_password(self, service, username):
        self.store.pop((service, username), None)


def test_resolve_auth_state_prefers_environment(tmp_path):
    cfg_home = tmp_path / "xdg"
    fake_keyring = FakeKeyring(
        initial={(config.KEYRING_SERVICE, config.KEYRING_USERNAME): "keychain-key"}
    )

    with patch.dict(
        os.environ,
        {"XDG_CONFIG_HOME": str(cfg_home), "ATTIO_API_KEY": "env-key"},
        clear=True,
    ):
        with patch("attio_cli.config.keyring", fake_keyring):
            config.save_config({"api_key": "file-key"})
            auth_state = config.resolve_auth_state()

    assert auth_state.api_key == "env-key"
    assert auth_state.source == config.AUTH_SOURCE_ENV


def test_set_api_key_prefers_keychain_and_clears_config_fallback(tmp_path):
    cfg_home = tmp_path / "xdg"
    fake_keyring = FakeKeyring()

    with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(cfg_home)}, clear=True):
        config.save_config({"api_key": "old-file-key"})
        with patch("attio_cli.config.keyring", fake_keyring):
            storage = config.set_api_key("new-key")

        assert storage == config.AUTH_SOURCE_KEYCHAIN
        assert config.load_config() == {}
        assert (
            fake_keyring.get_password(config.KEYRING_SERVICE, config.KEYRING_USERNAME) == "new-key"
        )


def test_set_api_key_falls_back_to_config_when_keychain_unavailable(tmp_path):
    cfg_home = tmp_path / "xdg"

    with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(cfg_home)}, clear=True):
        with patch("attio_cli.config.keyring", None):
            storage = config.set_api_key("file-key")

        assert storage == config.AUTH_SOURCE_CONFIG
        assert config.load_config()["api_key"] == "file-key"


def test_config_show_reports_auth_source_and_storage(tmp_path):
    cfg_home = tmp_path / "xdg"
    fake_keyring = FakeKeyring(
        initial={(config.KEYRING_SERVICE, config.KEYRING_USERNAME): "saved-key"}
    )

    with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(cfg_home)}, clear=True):
        with patch("attio_cli.config.keyring", fake_keyring):
            result = CliRunner().invoke(cli, ["config", "show"])

    assert result.exit_code == 0
    assert "Auth source: system keychain" in result.output
    assert "Preferred local storage: system keychain" in result.output
    assert "API key: saved-ke...-key" in result.output


def test_config_login_saves_to_keychain(tmp_path):
    cfg_home = tmp_path / "xdg"
    fake_keyring = FakeKeyring()

    with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(cfg_home)}, clear=True):
        with patch("attio_cli.config.keyring", fake_keyring):
            result = CliRunner().invoke(cli, ["config", "login", "secret-key"])

    assert result.exit_code == 0
    assert "API key saved to system keychain." in result.output
    assert (
        fake_keyring.get_password(config.KEYRING_SERVICE, config.KEYRING_USERNAME) == "secret-key"
    )


def test_config_logout_removes_saved_key_and_mentions_environment_override(tmp_path):
    cfg_home = tmp_path / "xdg"
    fake_keyring = FakeKeyring(
        initial={(config.KEYRING_SERVICE, config.KEYRING_USERNAME): "saved-key"}
    )

    with patch.dict(
        os.environ,
        {"XDG_CONFIG_HOME": str(cfg_home), "ATTIO_API_KEY": "env-key"},
        clear=True,
    ):
        with patch("attio_cli.config.keyring", fake_keyring):
            result = CliRunner().invoke(cli, ["config", "logout"])

    assert result.exit_code == 0
    assert "Removed saved API key from system keychain." in result.output
    assert (
        "ATTIO_API_KEY is still set in the environment and will continue to be used."
        in result.output
    )
