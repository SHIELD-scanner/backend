.PHONY: install sync run dev clean format lint check

install:
	uv sync

install-dev:
	uv sync --dev

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

format:
	uv run black app/
	uv run ruff format app/

lint:
	uv run ruff check app/

check:
	uv run validate-pyproject pyproject.toml

clean:
	rm -rf .venv
	rm -rf .ruff_cache
	rm -rf shield_backend.egg-info/
	rm -rf app/__pycache__/
	rm -rf app/*/__pycache__/
