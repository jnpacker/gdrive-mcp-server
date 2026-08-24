.DEFAULT_GOAL := help

GOOGLE_CLIENT_SECRETS_FILE ?= $(CURDIR)/credentials.json
GOOGLE_TOKEN_FILE ?= $(CURDIR)/token.json
export GOOGLE_CLIENT_SECRETS_FILE
export GOOGLE_TOKEN_FILE

VENV := .venv
PYTHON := $(VENV)/bin/python3

.PHONY: help auth test test-integration install lint lint-fix

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

$(VENV)/bin/activate: pyproject.toml
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	touch $(VENV)/bin/activate

install: $(VENV)/bin/activate ## Install package and dev dependencies into a local .venv

auth: install ## Run OAuth2 browser flow to generate token.json (requires GOOGLE_CLIENT_SECRETS_FILE and GOOGLE_TOKEN_FILE)
	@test -n "$(GOOGLE_CLIENT_SECRETS_FILE)" || (echo "Error: GOOGLE_CLIENT_SECRETS_FILE is not set"; exit 1)
	@test -n "$(GOOGLE_TOKEN_FILE)" || (echo "Error: GOOGLE_TOKEN_FILE is not set"; exit 1)
	$(PYTHON) -c "from gdrive_mcp_server.auth import get_credentials; get_credentials()"

test: install ## Run unit tests
	$(PYTHON) -m pytest tests/unit/ -v

test-integration: install ## Run integration tests (requires GDRIVE_TEST_FOLDER_ID, GOOGLE_CLIENT_SECRETS_FILE, GOOGLE_TOKEN_FILE)
	$(PYTHON) -m pytest tests/integration/ -v

lint: install ## Run ruff linter
	$(PYTHON) -m ruff check src/ tests/

lint-fix: install ## Run ruff linter with auto-fix
	$(PYTHON) -m ruff check --fix src/ tests/
