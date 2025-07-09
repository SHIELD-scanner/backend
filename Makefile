.PHONY: install sync run dev clean format lint check

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

format:
	python -m black app/
	python -m ruff format app/

lint:
	python -m ruff check app/

check:
	python -m validate-pyproject pyproject.toml

clean:
	rm -rf .venv
	rm -rf .ruff_cache
	rm -rf shield_backend.egg-info/
	rm -rf app/__pycache__/
	rm -rf app/*/__pycache__/
