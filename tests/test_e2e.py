"""End-to-end tests for iterm2-focus CLI."""

import os
import subprocess
import sys
from typing import Dict, Any
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from iterm2_focus import __version__


def run_cli_command(args: list) -> Dict[str, Any]:
    """Run iterm2-focus CLI command and return result."""
    result = subprocess.run(
        [sys.executable, "-m", "iterm2_focus.cli"] + args,
        capture_output=True,
        text=True
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


@pytest.mark.e2e
def test_cli_version():
    """Test --version flag works correctly."""
    result = run_cli_command(["--version"])
    assert result["returncode"] == 0
    assert f"iterm2-focus {__version__}" in result["stdout"]


@pytest.mark.e2e
def test_cli_help():
    """Test --help flag shows usage information."""
    result = run_cli_command(["--help"])
    assert result["returncode"] == 0
    assert "Focus iTerm2 session by ID" in result["stdout"]
    assert "Examples:" in result["stdout"]


@pytest.mark.e2e
def test_cli_no_args():
    """Test running without arguments shows help."""
    result = run_cli_command([])
    assert result["returncode"] == 1
    assert "Usage:" in result["stdout"]


@pytest.mark.e2e
def test_cli_with_mock_iterm2():
    """Test CLI with mocked iTerm2 functionality."""
    # Create a test script that mocks iTerm2 and runs the CLI
    test_script = """
import sys
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Mock iTerm2 module
class MockSession:
    def __init__(self, session_id, name="Test Session"):
        self.session_id = session_id
        self.name = name
        self._activated = False
    
    async def async_activate(self):
        self._activated = True
        return True
    
    async def async_get_variable(self, name):
        variables = {
            "session.name": self.name,
            "session.tty": f"/dev/ttys{self.session_id[-3:]}",
            "user.username": "testuser",
            "session.hostname": "localhost",
            "session.path": "/home/test"
        }
        return variables.get(name)

class MockTab:
    def __init__(self, sessions):
        self.sessions = sessions
        self.tab_id = "mock_tab_001"
        self._selected = False
    
    async def async_select(self):
        self._selected = True
        return True

class MockWindow:
    def __init__(self, tabs):
        self.tabs = tabs
        self.window_id = "mock_window_001"
        self._activated = False
    
    async def async_activate(self):
        self._activated = True
        return True

class MockApp:
    def __init__(self):
        session1 = MockSession("test_session_001", "Session 1")
        session2 = MockSession("test_session_002", "Session 2")
        tab1 = MockTab([session1])
        tab2 = MockTab([session2])
        window = MockWindow([tab1, tab2])
        self.terminal_windows = [window]

class MockConnection:
    @classmethod
    async def async_create(cls):
        return cls()

async def mock_get_app(connection):
    return MockApp()

# Create mock iterm2 module
mock_iterm2 = MagicMock()
mock_iterm2.Connection = MockConnection
mock_iterm2.async_get_app = mock_get_app

# Inject mock
sys.modules['iterm2'] = mock_iterm2

# Now run the actual CLI
from iterm2_focus.cli import main
from click.testing import CliRunner

runner = CliRunner()

# Test listing sessions
result = runner.invoke(main, ['--list'])
print(f"List exit code: {result.exit_code}")
print(f"List output: {result.output}")
assert result.exit_code == 0
assert "Session 1" in result.output
assert "Session 2" in result.output
assert "test_session_001" in result.output
assert "test_session_002" in result.output

# Test focusing a session
result = runner.invoke(main, ['test_session_001'])
print(f"Focus exit code: {result.exit_code}")
print(f"Focus output: {result.output}")
assert result.exit_code == 0
assert "Focused session: test_session_001" in result.output

# Test focusing non-existent session
result = runner.invoke(main, ['non_existent'])
print(f"Not found exit code: {result.exit_code}")
print(f"Not found output: {result.output}")
assert result.exit_code == 1
assert "Session not found" in result.output

# Test get-current with environment variable
import os
os.environ['ITERM_SESSION_ID'] = 'test_session_001'
result = runner.invoke(main, ['--get-current'])
print(f"Get current exit code: {result.exit_code}")
print(f"Get current output: {result.output}")
assert result.exit_code == 0
assert "test_session_001" in result.output

print("All tests passed!")
"""
    
    # Write test script
    with open("test_cli_e2e.py", "w") as f:
        f.write(test_script)
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, "test_cli_e2e.py"],
            capture_output=True,
            text=True
        )
        
        print("E2E Test Output:")
        print(result.stdout)
        if result.stderr:
            print("E2E Test Errors:")
            print(result.stderr)
        
        assert result.returncode == 0, f"E2E test failed: {result.stderr}"
        assert "All tests passed!" in result.stdout
        
    finally:
        # Cleanup
        if os.path.exists("test_cli_e2e.py"):
            os.remove("test_cli_e2e.py")


@pytest.mark.e2e
def test_session_id_prefix_handling():
    """Test that session ID prefixes are handled correctly."""
    # Create a test that verifies prefix removal
    test_script = """
import sys
from unittest.mock import MagicMock, AsyncMock

# Mock simple iTerm2
mock_iterm2 = MagicMock()

class MockSession:
    def __init__(self, sid):
        self.session_id = sid

class MockTab:
    def __init__(self):
        self.sessions = [MockSession("test123")]

class MockWindow:
    def __init__(self):
        self.tabs = [MockTab()]

class MockApp:
    def __init__(self):
        self.terminal_windows = [MockWindow()]

class MockConnection:
    @classmethod
    async def async_create(cls):
        return cls()

async def mock_get_app(conn):
    return MockApp()

mock_iterm2.Connection = MockConnection
mock_iterm2.async_get_app = mock_get_app

# Focus session mock
async def mock_async_focus(session_id):
    # Verify the prefix was stripped
    assert session_id == "test123", f"Expected 'test123', got '{session_id}'"
    return True

# Inject mocks
sys.modules['iterm2'] = mock_iterm2
sys.modules['iterm2_focus.focus'] = MagicMock()
sys.modules['iterm2_focus.focus'].async_focus_session = mock_async_focus

from iterm2_focus.cli import main
from click.testing import CliRunner

runner = CliRunner()

# Test with prefixed session ID
result = runner.invoke(main, ['w0t5p1:test123'])
assert result.exit_code == 0, f"Failed with: {result.output}"
print("Prefix handling test passed!")
"""
    
    with open("test_prefix.py", "w") as f:
        f.write(test_script)
    
    try:
        result = subprocess.run(
            [sys.executable, "test_prefix.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Prefix test failed: {result.stderr}"
        assert "Prefix handling test passed!" in result.stdout
    finally:
        if os.path.exists("test_prefix.py"):
            os.remove("test_prefix.py")