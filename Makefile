.DEFAULT_GOAL := help

.PHONY: help auth test test-integration install

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package and dev dependencies
	pip install -e ".[dev]"

auth: ## Run OAuth2 browser flow to generate token.json (requires GOOGLE_CLIENT_SECRETS_FILE and GOOGLE_TOKEN_FILE)
	@test -n "$(GOOGLE_CLIENT_SECRETS_FILE)" || (echo "Error: GOOGLE_CLIENT_SECRETS_FILE is not set"; exit 1)
	@test -n "$(GOOGLE_TOKEN_FILE)" || (echo "Error: GOOGLE_TOKEN_FILE is not set"; exit 1)
	python3 -c "from gdrive_mcp_server.auth import get_credentials; get_credentials()"

test: ## Run unit tests
	python3 -m pytest tests/unit/ -v

test-integration: ## Run integration tests (requires GDRIVE_TEST_FOLDER_ID, GOOGLE_CLIENT_SECRETS_FILE, GOOGLE_TOKEN_FILE)
	python3 -m pytest tests/integration/ -v
