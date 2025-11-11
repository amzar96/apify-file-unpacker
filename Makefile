# This is used by the Github Actions to run the static analysis.

.PHONY: clean install-dev lint type-check format check-code

-include .env
export 

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist htmlcov .coverage */__pycache__

install-dev:
	uv sync --all-extras

lint:
	uv run ruff format --check
	uv run ruff check

type-check:
	uv run mypy

format:
	uv run ruff check --fix
	uv run ruff format

check-code: lint type-check

run:
	apify run