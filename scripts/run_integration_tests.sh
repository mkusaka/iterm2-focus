#!/bin/bash
# Script to run integration tests with iTerm2

set -e

echo "=== iTerm2 Integration Test Runner ==="
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: Integration tests require macOS"
    exit 1
fi

# Check if iTerm2 is installed
if ! [ -d "/Applications/iTerm.app" ]; then
    echo "Error: iTerm2 not found at /Applications/iTerm.app"
    echo "Please install iTerm2 from https://iterm2.com/"
    exit 1
fi

# Check if iTerm2 is running
if ! pgrep -x "iTerm2" > /dev/null; then
    echo "Starting iTerm2..."
    open -a iTerm
    sleep 3
fi

# Check Python API
if ! [ -d "$HOME/Library/Application Support/iTerm2/iterm2env" ]; then
    echo "Warning: iTerm2 Python API might not be enabled"
    echo "Please enable it in iTerm2 Preferences > General > Magic > Enable Python API"
fi

# Run integration tests
echo "Running integration tests..."
uv run pytest -v tests/test_integration.py -m integration --tb=short

echo ""
echo "Integration tests completed!"