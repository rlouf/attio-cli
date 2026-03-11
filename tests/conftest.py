"""Shared test fixtures and helpers for CLI tests."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any

import pytest
from click.testing import CliRunner

CLIENT_MODULE_NAMES = [
    "attio.main",
    "attio.commands.attributes",
    "attio.commands.entries",
    "attio.commands.lists",
    "attio.commands.members",
    "attio.commands.notes",
    "attio.commands.objects",
    "attio.commands.records",
    "attio.commands.tasks",
    "attio.commands.webhooks",
]


class FakeKeyring:
    """In-memory keyring stub for config/auth tests."""

    def __init__(self, initial: dict[tuple[str, str], str] | None = None, fail_set: bool = False):
        self.store = initial or {}
        self.fail_set = fail_set

    def get_password(self, service: str, username: str) -> str | None:
        return self.store.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        if self.fail_set:
            raise RuntimeError("keychain unavailable")
        self.store[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        self.store.pop((service, username), None)


class FailingClient:
    """Client stub that always raises the provided error."""

    def __init__(self, error: Exception):
        self.error = error

    def __enter__(self) -> FailingClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        raise self.error

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        raise self.error

    def put(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        raise self.error

    def patch(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        raise self.error


class RecordingClient:
    """Client stub that records calls and returns queued responses."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.responses: dict[tuple[str, str], dict[str, Any]] = {}

    def __enter__(self) -> RecordingClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def queue_response(self, method: str, path: str, response: dict[str, Any]) -> None:
        self.responses[(method.upper(), path)] = response

    def _call(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append({"method": method.upper(), "path": path, "params": params, "json": json})
        return self.responses.get((method.upper(), path), {"data": {}})

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._call("GET", path, params=params)

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._call("POST", path, json=json)

    def put(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        return self._call("PUT", path, json=json)

    def patch(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        return self._call("PATCH", path, json=json)


@pytest.fixture
def runner() -> CliRunner:
    """Reusable Click test runner."""
    return CliRunner()


@pytest.fixture
def fake_keyring_factory() -> type[FakeKeyring]:
    """Factory for fake keyring instances."""
    return FakeKeyring


@pytest.fixture
def failing_client_factory() -> type[FailingClient]:
    """Factory for failing client stubs."""
    return FailingClient


@pytest.fixture
def recording_client_factory() -> type[RecordingClient]:
    """Factory for recording client stubs."""
    return RecordingClient


@pytest.fixture
def patch_command_clients(monkeypatch: pytest.MonkeyPatch) -> Callable[[Any], None]:
    """Patch get_client across the root CLI and all command modules."""

    def apply(client_or_factory: Any) -> None:
        for module_name in CLIENT_MODULE_NAMES:
            module = import_module(module_name)
            if callable(client_or_factory):
                monkeypatch.setattr(module, "get_client", client_or_factory)
            else:
                monkeypatch.setattr(module, "get_client", lambda client=client_or_factory: client)

    return apply
