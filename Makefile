PORT ?= 8000

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

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app