PYTHON ?= python3
VENV ?= .venv

.PHONY: venv install run dev clean

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

run:
	$(VENV)/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	$(VENV)/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

clean:
	rm -rf $(VENV)
