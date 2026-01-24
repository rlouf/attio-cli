"""HTTP client for the Attio API."""

from typing import Any

import httpx

BASE_URL = "https://api.attio.com/v2"


class AttioError(Exception):
    """Base exception for Attio API errors."""

    pass


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
            raise AttioError("Unauthorized: Check your API key")
        elif status == 403:
            raise AttioError(f"Forbidden: {message}")
        elif status == 404:
            raise AttioError(f"Not found: {message}")
        elif status == 422 or status == 400:
            raise AttioError(f"Validation error: {message}")
        elif status == 429:
            raise AttioError("Rate limited: Too many requests")
        else:
            raise AttioError(f"API error ({status}): {message}")

    def get(self, path: str) -> dict[str, Any]:
        """Make a GET request."""
        response = self._client.get(path)
        return self._handle_response(response)

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a POST request."""
        response = self._client.post(path, json=json or {})
        return self._handle_response(response)

    def put(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """Make a PUT request."""
        response = self._client.put(path, json=json)
        return self._handle_response(response)

    def patch(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """Make a PATCH request."""
        response = self._client.patch(path, json=json)
        return self._handle_response(response)

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
