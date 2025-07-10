"""Tests for utils module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from iterm2_focus.utils import (
    focus_session_by_name,
    get_all_sessions,
    get_session_info,
    run_async,
)


@pytest.mark.asyncio
async def test_get_session_info_found() -> None:
    """Test getting session info when session exists."""
    # Mock session
    mock_session = MagicMock()
    mock_session.session_id = "test_session_id"
    mock_session.async_get_variable = AsyncMock(
        side_effect=lambda var: {
            "session.name": "Test Session",
            "hostname": "test.host",
            "username": "testuser",
            "path": "/test/path",
            "tty": "/dev/ttys001",
        }.get(var)
    )

    # Mock tab and window
    mock_tab = MagicMock()
    mock_tab.sessions = [mock_session]
    mock_tab.tab_id = "tab1"

    mock_window = MagicMock()
    mock_window.tabs = [mock_tab]
    mock_window.window_id = "window1"

    # Mock app and connection
    mock_app = MagicMock()
    mock_app.terminal_windows = [mock_window]

    mock_connection = AsyncMock()

    with patch("iterm2.Connection.async_create", return_value=mock_connection), patch(
        "iterm2.async_get_app", return_value=mock_app
    ):
        info = await get_session_info("test_session_id")

    assert info is not None
    assert info["id"] == "test_session_id"
    assert info["name"] == "Test Session"
    assert info["hostname"] == "test.host"
    assert info["username"] == "testuser"
    assert info["path"] == "/test/path"
    assert info["tty"] == "/dev/ttys001"
    assert info["window_id"] == "window1"
    assert info["tab_id"] == "tab1"


@pytest.mark.asyncio
async def test_get_session_info_not_found() -> None:
    """Test getting session info when session doesn't exist."""
    mock_session = MagicMock()
    mock_session.session_id = "different_session_id"

    mock_tab = MagicMock()
    mock_tab.sessions = [mock_session]

    mock_window = MagicMock()
    mock_window.tabs = [mock_tab]

    mock_app = MagicMock()
    mock_app.terminal_windows = [mock_window]

    mock_connection = AsyncMock()

    with patch("iterm2.Connection.async_create", return_value=mock_connection), patch(
        "iterm2.async_get_app", return_value=mock_app
    ):
        info = await get_session_info("test_session_id")

    assert info is None


@pytest.mark.asyncio
async def test_focus_session_by_name_found() -> None:
    """Test focusing session by name when match found."""
    # Mock session with matching name
    mock_session = MagicMock()
    mock_session.async_get_variable = AsyncMock(return_value="Test Production Server")
    mock_session.async_activate = AsyncMock()

    mock_tab = MagicMock()
    mock_tab.sessions = [mock_session]
    mock_tab.async_select = AsyncMock()

    mock_window = MagicMock()
    mock_window.tabs = [mock_tab]
    mock_window.async_activate = AsyncMock()

    mock_app = MagicMock()
    mock_app.terminal_windows = [mock_window]

    mock_connection = AsyncMock()

    with patch("iterm2.Connection.async_create", return_value=mock_connection), patch(
        "iterm2.async_get_app", return_value=mock_app
    ):
        result = await focus_session_by_name("production")

    assert result is True
    mock_session.async_activate.assert_called_once()
    mock_tab.async_select.assert_called_once()
    mock_window.async_activate.assert_called_once()


@pytest.mark.asyncio
async def test_focus_session_by_name_case_insensitive() -> None:
    """Test focusing session by name is case insensitive."""
    mock_session = MagicMock()
    mock_session.async_get_variable = AsyncMock(return_value="Test PRODUCTION Server")
    mock_session.async_activate = AsyncMock()

    mock_tab = MagicMock()
    mock_tab.sessions = [mock_session]
    mock_tab.async_select = AsyncMock()

    mock_window = MagicMock()
    mock_window.tabs = [mock_tab]
    mock_window.async_activate = AsyncMock()

    mock_app = MagicMock()
    mock_app.terminal_windows = [mock_window]

    mock_connection = AsyncMock()

    with patch("iterm2.Connection.async_create", return_value=mock_connection), patch(
        "iterm2.async_get_app", return_value=mock_app
    ):
        result = await focus_session_by_name("production")

    assert result is True
    mock_session.async_activate.assert_called_once()


@pytest.mark.asyncio
async def test_focus_session_by_name_not_found() -> None:
    """Test focusing session by name when no match found."""
    mock_session = MagicMock()
    mock_session.async_get_variable = AsyncMock(return_value="Test Development Server")

    mock_tab = MagicMock()
    mock_tab.sessions = [mock_session]

    mock_window = MagicMock()
    mock_window.tabs = [mock_tab]

    mock_app = MagicMock()
    mock_app.terminal_windows = [mock_window]

    mock_connection = AsyncMock()

    with patch("iterm2.Connection.async_create", return_value=mock_connection), patch(
        "iterm2.async_get_app", return_value=mock_app
    ):
        result = await focus_session_by_name("production")

    assert result is False


@pytest.mark.asyncio
async def test_get_all_sessions() -> None:
    """Test getting all sessions."""
    # Mock sessions
    mock_session1 = MagicMock()
    mock_session1.session_id = "session1"
    mock_session1.async_get_variable = AsyncMock(
        side_effect=lambda var: {
            "session.name": "Session 1",
            "hostname": "host1",
            "username": "user1",
            "path": "/path1",
        }.get(var)
    )

    mock_session2 = MagicMock()
    mock_session2.session_id = "session2"
    mock_session2.async_get_variable = AsyncMock(
        side_effect=lambda var: {
            "session.name": None,  # Unnamed session
            "hostname": "host2",
            "username": "user2",
            "path": "/path2",
        }.get(var)
    )

    # Mock tabs and windows
    mock_tab1 = MagicMock()
    mock_tab1.sessions = [mock_session1]
    mock_tab1.tab_id = "tab1"

    mock_tab2 = MagicMock()
    mock_tab2.sessions = [mock_session2]
    mock_tab2.tab_id = "tab2"

    mock_window = MagicMock()
    mock_window.tabs = [mock_tab1, mock_tab2]
    mock_window.window_id = "window1"

    mock_app = MagicMock()
    mock_app.terminal_windows = [mock_window]

    mock_connection = AsyncMock()

    with patch("iterm2.Connection.async_create", return_value=mock_connection), patch(
        "iterm2.async_get_app", return_value=mock_app
    ):
        sessions = await get_all_sessions()

    assert len(sessions) == 2

    assert sessions[0]["id"] == "session1"
    assert sessions[0]["name"] == "Session 1"
    assert sessions[0]["hostname"] == "host1"

    assert sessions[1]["id"] == "session2"
    assert sessions[1]["name"] == "Unnamed"  # Default for None
    assert sessions[1]["hostname"] == "host2"


def test_run_async() -> None:
    """Test run_async helper function."""

    async def sample_coroutine(value: int) -> int:
        return value * 2

    result = run_async(sample_coroutine(21))
    assert result == 42


def test_run_async_with_exception() -> None:
    """Test run_async with exception."""

    async def failing_coroutine() -> None:
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        run_async(failing_coroutine())
