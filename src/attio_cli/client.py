"""HTTP client for the Attio API."""

from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL = "https://api.attio.com/v2"
AUTH_SETUP_HINT = "Set ATTIO_API_KEY or run: attio config set api-key <key>"


@dataclass
class AttioError(Exception):
    """Structured CLI-facing error for Attio API failures."""

    message: str
    status_code: int | None = None
    hint: str | None = None
    details: str | None = None

    def format_for_cli(self) -> str:
        """Render a multi-line Click-friendly error message."""
        lines = [self.message]
        if self.details and self.details != self.message:
            lines.append(f"Details: {self.details}")
        if self.hint:
            lines.append(f"Hint: {self.hint}")
        return "\n".join(lines)


class AttioClient:
    """Client for the Attio API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make a request and normalize transport and API errors."""
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise AttioError(
                "Network error contacting Attio API.",
                hint="Check your network connection and try again.",
                details=str(exc),
            ) from None
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate errors."""
        if response.is_success:
            return response.json()

        try:
            error_body = response.json()
            message = error_body.get("message", "Unknown error")
        except Exception:
            message = response.text or "Unknown error"

        status = response.status_code
        if status == 401:
            raise AttioError(
                "Unauthorized.",
                status_code=status,
                hint=AUTH_SETUP_HINT,
                details=message,
            )
        if status == 403:
            raise AttioError(
                "Forbidden.",
                status_code=status,
                hint="Your API key is valid but does not have access to this resource.",
                details=message,
            )
        if status == 404:
            raise AttioError(
                "Resource not found.",
                status_code=status,
                hint="Check the resource identifier and try again.",
                details=message,
            )
        if status in {400, 422}:
            raise AttioError(
                "Validation error.",
                status_code=status,
                hint="Inspect the target resource and try again with a valid payload.",
                details=message,
            )
        if status == 429:
            raise AttioError(
                "Rate limited.",
                status_code=status,
                hint="Wait briefly and retry your request.",
                details=message,
            )
        raise AttioError(
            f"Attio API error ({status}).",
            status_code=status,
            details=message,
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, json=json or {})

    def put(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """Make a PUT request."""
        return self._request("PUT", path, json=json)

    def patch(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """Make a PATCH request."""
        return self._request("PATCH", path, json=json)

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
