.PHONY: test lint format-check typecheck check verify

UV_CACHE_DIR ?= /tmp/attio-uv-cache

test:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --with pytest pytest -q tests

lint:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uvx ruff check src tests

format-check:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uvx ruff format --check src tests

typecheck:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --with-editable . --with ty --with pytest ty check src tests

check:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uvx pre-commit run --all-files

verify: test check
