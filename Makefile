all: help

help:
	@echo "targets: format, check, run"


format:
	uv run ruff format *.py

check:
	uv run mypy *.py

run:
	uv run main.py
