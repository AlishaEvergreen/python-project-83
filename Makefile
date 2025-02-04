install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=page_analyzer --cov-report xml

lint:
	uv run ruff check page_analyzer

check: test lint

format-app:
	uv run ruff check --fix page_analyzer/app.py
