# Contributing to iterm2-focus

Thank you for your interest in contributing to iterm2-focus! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/iterm2-focus
   cd iterm2-focus
   ```

2. **Install uv (if not already installed)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create a virtual environment and install dependencies**
   ```bash
   uv venv
   uv sync --all-extras --dev
   ```

4. **Install pre-commit hooks (optional but recommended)**
   ```bash
   uv run pre-commit install
   ```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=iterm2_focus

# Run specific test file
uv run pytest tests/test_focus.py

# Run with verbose output
uv run pytest -v
```

## Code Quality

Before submitting a pull request, ensure your code passes all quality checks:

```bash
# Format code
uv run black src tests
uv run ruff format src tests

# Check linting
uv run ruff check src tests

# Type checking
uv run mypy src

# Run all checks at once
uv run black src tests && uv run ruff check src tests && uv run mypy src && uv run pytest
```

## Testing the CLI

During development, you can test the CLI using:

```bash
# Using uv run
uv run isf --help
uv run isf --list

# Or activate the virtual environment
source .venv/bin/activate
isf --help
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Add tests for new functionality
   - Update documentation as needed

3. **Ensure all tests pass**
   ```bash
   uv run pytest
   uv run mypy src
   ```

4. **Push your branch and create a pull request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Ensure CI passes

## Code Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names

## Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use pytest fixtures for test setup
- Mock external dependencies (especially iTerm2 API calls)

## Documentation

- Update README.md if adding new features
- Add docstrings to all public functions and classes
- Include type hints in function signatures

## Release Process

Releases are automated through GitHub Actions:

1. Update version in `pyproject.toml` and `src/iterm2_focus/__init__.py`
2. Create a PR with version changes
3. After merging, create a GitHub release with tag `v{version}`
4. CI will automatically publish to PyPI

## Questions?

Feel free to open an issue for any questions or concerns!