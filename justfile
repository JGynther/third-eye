default:
    @just --list

sync:
    uv sync --all-packages

run:
    uv run run.py
