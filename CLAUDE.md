# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

iterm2-focus is a Python CLI tool that allows focusing iTerm2 sessions by their ID from the command line. It leverages the iTerm2 Python API to interact with terminal sessions.

## Development Commands

### Build and Distribution
```bash
# Build the package
uv build

# Upload to PyPI (requires credentials)
uv publish
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=iterm2_focus

# Run a specific test file
uv run pytest tests/test_cli.py

# Run a specific test
uv run pytest tests/test_cli.py::test_version

# Run tests excluding integration tests
uv run pytest -m "not integration"

# Run only integration tests (requires iTerm2)
uv run pytest -m integration

# Run integration tests with helper script
./scripts/run_integration_tests.sh
```

### Type Checking
```bash
# Run mypy type checker
uv run mypy src
```

### Linting and Formatting
```bash
# Check with ruff
uv run ruff check src tests

# Auto-fix with ruff
uv run ruff check --fix src tests

# Format with black
uv run black src tests

# Check formatting without changes
uv run black --check src tests
```

### Development Setup
```bash
# Create virtual environment
uv venv

# Install package in development mode with all dependencies
uv pip install -e ".[dev]"
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