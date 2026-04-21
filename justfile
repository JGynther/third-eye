default:
    @just --list

sync:
    uv sync --all-packages

run:
    uv run run.py

lint:
    uv run ruff check .
    uv run ruff format --check .
    cd ui && bun run lint
    cd ui && bun run fmt:check

fmt:
    uv run ruff format .
    uv run ruff check --fix .
    cd ui && bun run fmt

typecheck:
    uv run ty check .
    cd ui && bun run check
