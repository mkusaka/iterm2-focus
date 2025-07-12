"""Integration tests for iterm2-focus with real iTerm2."""

import os
import platform
import subprocess
import time

import pytest

from iterm2_focus import __version__
from iterm2_focus.cli import main
from iterm2_focus.focus import async_focus_session
from iterm2_focus.utils import get_all_sessions, get_session_info


def is_iterm2_running() -> bool:
    """Check if iTerm2 is running."""
    if platform.system() != "Darwin":
        return False

    try:
        result = subprocess.run(
            ["pgrep", "-x", "iTerm2"], capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def has_python_api_enabled() -> bool:
    """Check if iTerm2 Python API is enabled."""
    # Check if iTerm2 is configured to allow Python API connections
    # This is a heuristic - actual check would require attempting connection
    return os.path.exists(
        os.path.expanduser("~/Library/Application Support/iTerm2/iterm2env")
    )


# Skip all integration tests if iTerm2 is not available
pytestmark = pytest.mark.skipif(
    not is_iterm2_running() or not has_python_api_enabled(),
    reason="iTerm2 not running or Python API not enabled",
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_connection():
    """Test real connection to iTerm2."""
    import iterm2

    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)
        assert app is not None

        # Verify we can access windows
        windows = app.terminal_windows
        assert isinstance(windows, list)

        # Clean up
        connection = None
    except Exception as e:
        pytest.fail(f"Failed to connect to iTerm2: {e}")


@pytest.mark.integration
def test_list_real_sessions():
    """Test listing real iTerm2 sessions."""
    sessions = get_all_sessions()

    # Should have at least one session if iTerm2 is running
    assert len(sessions) > 0

    # Verify session structure
    for session in sessions:
        assert "id" in session
        assert "name" in session
        assert "window" in session
        assert "tab" in session

        # Session ID should be non-empty
        assert session["id"]
        assert isinstance(session["id"], str)


@pytest.mark.integration
def test_get_real_session_info():
    """Test getting info from a real session."""
    sessions = get_all_sessions()
    if not sessions:
        pytest.skip("No sessions available")

    # Get info for the first session
    session_id = sessions[0]["id"]
    info = get_session_info(session_id)

    assert info is not None
    assert info["id"] == session_id
    assert "name" in info
    assert "hostname" in info
    assert "username" in info
    assert "tty" in info


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_focus_session():
    """Test creating a new session and focusing it."""
    import iterm2

    connection = await iterm2.Connection.async_create()
    app = await iterm2.async_get_app(connection)

    # Get current window
    window = app.current_terminal_window
    if not window:
        # Create a new window if none exists
        window = await app.async_create_window()

    # Create a new tab
    tab = await window.async_create_tab()
    session = tab.current_session
    new_session_id = session.session_id

    # Give it a unique name
    test_name = f"iterm2-focus-test-{int(time.time())}"
    await session.async_set_name(test_name)

    # Now try to focus it using our library
    try:
        result = await async_focus_session(new_session_id)
        assert result is True

        # Verify it's actually focused
        import asyncio

        await asyncio.sleep(0.1)  # Small delay for focus to take effect
        current_session = app.current_terminal_window.current_tab.current_session
        assert current_session.session_id == new_session_id

    finally:
        # Clean up - close the test tab
        await tab.async_close(force=True)


@pytest.mark.integration
def test_cli_with_real_iterm2(runner):
    """Test CLI commands with real iTerm2."""
    from click.testing import CliRunner

    runner = CliRunner()

    # Test --list command
    result = runner.invoke(main, ["--list"])
    assert result.exit_code == 0
    assert "ID:" in result.output
    assert "Name:" in result.output

    # Test --version
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output

    # Test focusing a non-existent session
    result = runner.invoke(main, ["nonexistent-session-id"])
    assert result.exit_code == 1
    assert "Session not found" in result.output


@pytest.mark.integration
def test_environment_variable_integration():
    """Test ITERM_SESSION_ID environment variable in real iTerm2."""
    # This test only makes sense when run from within iTerm2
    if "ITERM_SESSION_ID" not in os.environ:
        pytest.skip("Not running inside iTerm2")

    from click.testing import CliRunner

    runner = CliRunner()

    # Test --get-current
    result = runner.invoke(main, ["--get-current"])
    assert result.exit_code == 0
    session_id = result.output.strip()
    assert session_id  # Should not be empty

    # Verify this session actually exists
    info = get_session_info(session_id)
    assert info is not None

    # Test --current (focus current session)
    result = runner.invoke(main, ["--current"])
    assert result.exit_code == 0
    assert f"Focused session: {session_id}" in result.output


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent operations don't interfere."""
    import asyncio

    sessions = get_all_sessions()
    if len(sessions) < 2:
        pytest.skip("Need at least 2 sessions for concurrent test")

    # Try to get info for multiple sessions concurrently
    session_ids = [s["id"] for s in sessions[:3]]

    async def get_info_async(session_id):
        """Wrapper to run get_session_info asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_session_info, session_id)

    # Run concurrently
    results = await asyncio.gather(*[get_info_async(sid) for sid in session_ids])

    # Verify all succeeded
    for i, result in enumerate(results):
        assert result is not None
        assert result["id"] == session_ids[i]


# Add a fixture to ensure we're in the right environment
@pytest.fixture(scope="session", autouse=True)
def check_environment():
    """Check and report test environment."""
    if platform.system() != "Darwin":
        pytest.skip("Integration tests require macOS")

    if not is_iterm2_running():
        pytest.skip("iTerm2 is not running")

    if not has_python_api_enabled():
        pytest.skip("iTerm2 Python API is not enabled")

    # Print environment info for debugging
    print(f"\nRunning integration tests on {platform.system()} {platform.version()}")
    print(f"iTerm2 running: {is_iterm2_running()}")
    print(f"Python API available: {has_python_api_enabled()}")

    yield
