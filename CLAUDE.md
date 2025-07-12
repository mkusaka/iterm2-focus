# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

iterm2-focus is a Python CLI tool that allows focusing iTerm2 sessions by their ID from the command line. It leverages the iTerm2 Python API to interact with terminal sessions.

## Development Commands

### Build and Distribution
```bash
# Build the package
make build
# or
uv build

# Upload to PyPI (requires credentials)
make publish
# or
uv publish

# Upload to TestPyPI
make publish-test
```

### Version Management
```bash
# Bump patch version (0.0.X)
make patch
# or
make version-patch

# Bump minor version (0.X.0)
make minor
# or
make version-minor

# Bump major version (X.0.0)
make major
# or
make version-major
```

Version bumping automatically:
- Updates version in pyproject.toml and __init__.py
- Runs `uv sync` to update uv.lock
- Creates a git commit with message "chore: bump version to X.Y.Z"
- Creates a git tag "vX.Y.Z"

### Testing
```bash
# Run all tests
make test
# or
uv run pytest

# Run tests with coverage
make test-cov
# or
uv run pytest --cov=iterm2_focus

# Run a specific test file
uv run pytest tests/test_cli.py

# Run a specific test
uv run pytest tests/test_cli.py::test_version
```

### Type Checking
```bash
# Run mypy type checker
make mypy
# or
uv run mypy src
```

### Linting and Formatting
```bash
# Check with ruff
make lint
# or
uv run ruff check src tests

# Auto-fix with ruff
make lint-fix
# or
uv run ruff check --fix src tests

# Format with black
make format
# or
uv run black src tests

# Check formatting without changes
make format-check
# or
uv run black --check src tests

# Run all checks (lint, mypy, format-check, test)
make check
```

### Development Setup
```bash
# Install all dependencies (including dev dependencies)
make install
# or
uv sync --all-extras --dev

# Show all available make commands
make help

# Clean build artifacts
make clean
```

## Architecture

The codebase follows a simple structure with clear separation of concerns:

- **src/iterm2_focus/** - Main package directory
  - **cli.py** - Click-based CLI interface that handles command-line arguments and user interaction
  - **focus.py** - Core functionality for focusing iTerm2 sessions using the iTerm2 Python API
  - **utils.py** - Utility functions (if any)
  - **__init__.py** - Package initialization with version info

- **tests/** - Test suite using pytest
  - Comprehensive tests for CLI functionality
  - Unit tests for the focus module
  - Uses pytest-mock for mocking external dependencies

The application workflow:
1. CLI parses user input via Click framework
2. For focus operations, calls into focus.py which uses asyncio
3. focus.py connects to iTerm2 via its Python API
4. Searches through windows/tabs/sessions to find matching session ID
5. Activates the found session, tab, and window

Key design patterns:
- Async/await pattern for iTerm2 API interactions (wrapped in sync interface)
- Clear error handling with custom FocusError exception
- Type hints throughout for better IDE support and type safety
- Modular design allowing easy testing of individual components