.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	uv sync --all-extras --dev

.PHONY: build
build: ## Build the package
	uv build

.PHONY: test
test: ## Run tests
	uv run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage
	uv run pytest -v --cov=iterm2_focus --cov-report=xml --cov-report=term

.PHONY: mypy
mypy: ## Run type checking
	uv run mypy src

.PHONY: lint
lint: ## Run linting
	uv run ruff check src tests

.PHONY: lint-fix
lint-fix: ## Run linting with auto-fix
	uv run ruff check --fix src tests

.PHONY: format
format: ## Format code with black
	uv run black src tests

.PHONY: format-check
format-check: ## Check code formatting
	uv run black --check src tests

.PHONY: check
check: lint mypy format-check test ## Run all checks

.PHONY: clean
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Version management
.PHONY: version-patch
version-patch: ## Bump patch version (0.0.X)
	@uv run python scripts/bump_version.py patch

.PHONY: version-minor
version-minor: ## Bump minor version (0.X.0)
	@uv run python scripts/bump_version.py minor

.PHONY: version-major
version-major: ## Bump major version (X.0.0)
	@uv run python scripts/bump_version.py major

# Shortcuts
.PHONY: patch
patch: version-patch ## Alias for version-patch

.PHONY: minor
minor: version-minor ## Alias for version-minor

.PHONY: major
major: version-major ## Alias for version-major

.PHONY: publish
publish: clean build ## Build and publish to PyPI
	uv publish

.PHONY: publish-test
publish-test: clean build ## Build and publish to TestPyPI
	uv publish --repository test-pypi