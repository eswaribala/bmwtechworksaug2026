PYTHON ?= python
PYTEST ?= pytest

.PHONY: install test lint format terraform-fmt

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	tfenv install || true

test:
	$(PYTEST)

lint:
	ruff check .
	black --check .

format:
	black .
	ruff check --fix .

terraform-fmt:
	terraform fmt -recursive
