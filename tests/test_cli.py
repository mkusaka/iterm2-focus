"""Tests for CLI module."""

import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from iterm2_focus import __version__
from iterm2_focus.cli import main
from iterm2_focus.focus import FocusError


@pytest.fixture
def runner() -> CliRunner:
    """Create a Click test runner."""
    return CliRunner()


def test_version(runner: CliRunner) -> None:
    """Test --version flag."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert f"iterm2-focus {__version__}" in result.output


def test_help(runner: CliRunner) -> None:
    """Test help output."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Focus iTerm2 session by ID" in result.output
    assert "Examples:" in result.output


def test_no_arguments(runner: CliRunner) -> None:
    """Test running without arguments shows help."""
    result = runner.invoke(main, [])
    assert result.exit_code == 1
    assert "Usage:" in result.output


def test_focus_session_success(runner: CliRunner) -> None:
    """Test successful session focus."""
    with patch("iterm2_focus.cli.focus_session", return_value=True):
        result = runner.invoke(main, ["test_session_id"])

    assert result.exit_code == 0
    assert "Focused session: test_session_id" in result.output


def test_focus_session_quiet(runner: CliRunner) -> None:
    """Test quiet mode."""
    with patch("iterm2_focus.cli.focus_session", return_value=True):
        result = runner.invoke(main, ["test_session_id", "--quiet"])

    assert result.exit_code == 0
    assert result.output == ""


def test_focus_session_not_found(runner: CliRunner) -> None:
    """Test session not found."""
    with patch("iterm2_focus.cli.focus_session", return_value=False):
        result = runner.invoke(main, ["test_session_id"])

    assert result.exit_code == 1
    assert "Error: Session not found: test_session_id" in result.output


def test_focus_session_error(runner: CliRunner) -> None:
    """Test focus error."""
    with patch(
        "iterm2_focus.cli.focus_session", side_effect=FocusError("Connection failed")
    ):
        result = runner.invoke(main, ["test_session_id"])

    assert result.exit_code == 1
    assert "Error: Connection failed" in result.output
    assert "Make sure iTerm2's Python API is enabled" in result.output


def test_current_session_with_env(runner: CliRunner) -> None:
    """Test --current with ITERM_SESSION_ID set."""
    test_session_id = "test_session_id"

    with patch.dict(os.environ, {"ITERM_SESSION_ID": test_session_id}), patch(
        "iterm2_focus.cli.focus_session", return_value=True
    ):
        result = runner.invoke(main, ["--current"])

    assert result.exit_code == 0
    assert f"Focused session: {test_session_id}" in result.output


def test_current_session_without_env(runner: CliRunner) -> None:
    """Test --current without ITERM_SESSION_ID set."""
    with patch.dict(os.environ, {}, clear=True):
        result = runner.invoke(main, ["--current"])

    assert result.exit_code == 1
    assert "Error: ITERM_SESSION_ID environment variable not found" in result.output
    assert "Are you running this from within iTerm2?" in result.output


def test_get_current_with_env(runner: CliRunner) -> None:
    """Test --get-current with ITERM_SESSION_ID set."""
    test_session_id = "test_session_id"

    with patch.dict(os.environ, {"ITERM_SESSION_ID": test_session_id}):
        result = runner.invoke(main, ["--get-current"])

    assert result.exit_code == 0
    assert result.output.strip() == test_session_id


def test_get_current_quiet(runner: CliRunner) -> None:
    """Test --get-current with --quiet."""
    test_session_id = "test_session_id"

    with patch.dict(os.environ, {"ITERM_SESSION_ID": test_session_id}):
        result = runner.invoke(main, ["--get-current", "--quiet"])

    assert result.exit_code == 0
    assert result.output.strip() == test_session_id


def test_get_current_without_env(runner: CliRunner) -> None:
    """Test --get-current without ITERM_SESSION_ID set."""
    with patch.dict(os.environ, {}, clear=True):
        result = runner.invoke(main, ["--get-current"])

    assert result.exit_code == 1
    assert "Error: ITERM_SESSION_ID environment variable not found" in result.output


def test_list_sessions_success(runner: CliRunner) -> None:
    """Test listing sessions."""
    mock_sessions = [
        {
            "id": "session1",
            "name": "Test Session 1",
            "window": "window1",
            "tab": "tab1",
            "hostname": "localhost",
            "username": "user",
            "path": "/home/user",
        },
        {
            "id": "session2",
            "name": "Test Session 2",
            "window": "window1",
            "tab": "tab2",
            "hostname": "remote.host",
            "username": "user",
            "path": "/var/www",
        },
    ]

    with patch("iterm2_focus.cli.asyncio.run", return_value=mock_sessions):
        result = runner.invoke(main, ["--list"])

    assert result.exit_code == 0
    assert "Available iTerm2 sessions:" in result.output
    assert "ID: session1" in result.output
    assert "Test Session 1" in result.output
    assert "ID: session2" in result.output
    assert "user@remote.host" in result.output


def test_list_sessions_empty(runner: CliRunner) -> None:
    """Test listing sessions when none found."""
    with patch("iterm2_focus.cli.asyncio.run", return_value=[]):
        result = runner.invoke(main, ["--list"])

    assert result.exit_code == 0
    assert "No sessions found." in result.output


def test_list_sessions_error(runner: CliRunner) -> None:
    """Test listing sessions error."""
    with patch(
        "iterm2_focus.cli.asyncio.run", side_effect=Exception("Connection failed")
    ):
        result = runner.invoke(main, ["--list"])

    assert result.exit_code == 1
    assert "Error: Failed to list sessions: Connection failed" in result.output


def test_focus_session_with_prefix(runner: CliRunner) -> None:
    """Test handling session ID with prefix format."""
    with patch("iterm2_focus.cli.focus_session", return_value=True) as mock_focus:
        result = runner.invoke(main, ["w0t5p1:test_session_id"])

    mock_focus.assert_called_once_with("test_session_id")
    assert result.exit_code == 0
    assert "Focused session: test_session_id" in result.output


def test_current_session_with_prefix(runner: CliRunner) -> None:
    """Test --current with prefixed ITERM_SESSION_ID."""
    with patch.dict(os.environ, {"ITERM_SESSION_ID": "w0t5p1:test_session_id"}), patch(
        "iterm2_focus.cli.focus_session", return_value=True
    ) as mock_focus:
        result = runner.invoke(main, ["--current"])

    mock_focus.assert_called_once_with("test_session_id")
    assert result.exit_code == 0
    assert "Focused session: test_session_id" in result.output


def test_get_current_with_prefix(runner: CliRunner) -> None:
    """Test --get-current with prefixed ITERM_SESSION_ID."""
    with patch.dict(os.environ, {"ITERM_SESSION_ID": "w0t5p1:test_session_id"}):
        result = runner.invoke(main, ["--get-current"])

    assert result.exit_code == 0
    assert result.output.strip() == "test_session_id"


def test_list_sessions_without_path(runner: CliRunner) -> None:
    """Test listing sessions where some have no path."""
    mock_sessions = [
        {
            "id": "session1",
            "name": "Session with path",
            "window": "window1",
            "tab": "tab1",
            "hostname": "localhost",
            "username": "user",
            "path": "/home/user",
            "tty": "/dev/ttys001",
        },
        {
            "id": "session2",
            "name": "Session without path",
            "window": "window1",
            "tab": "tab2",
            "hostname": "localhost",
            "username": "user",
            "path": None,  # No path
            "tty": "/dev/ttys002",
        },
    ]

    with patch("iterm2_focus.cli.asyncio.run", return_value=mock_sessions):
        result = runner.invoke(main, ["--list"])

    assert result.exit_code == 0
    # Verify path is shown for session1
    assert "Path: /home/user" in result.output
    # Verify session2 is listed
    assert "ID: session2" in result.output
    # Verify no path is shown after session2 by checking lines
    lines = result.output.split("\n")
    session2_index = next(i for i, line in enumerate(lines) if "ID: session2" in line)
    # Check that there's no "Path:" line immediately after session2 (within next 5 lines)
    assert not any(
        "Path:" in lines[i]
        for i in range(session2_index, min(session2_index + 5, len(lines)))
    )
