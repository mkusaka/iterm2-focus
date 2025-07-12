"""Tests for focus module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from iterm2_focus.focus import FocusError, async_focus_session, focus_session


@pytest.mark.asyncio
async def test_async_focus_session_success() -> None:
    """Test successful session focus."""
    # Mock iTerm2 objects
    mock_session = MagicMock()
    mock_session.session_id = "test_session_id"
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
        result = await async_focus_session("test_session_id")

    assert result is True
    mock_session.async_activate.assert_called_once()
    mock_tab.async_select.assert_called_once()
    mock_window.async_activate.assert_called_once()


@pytest.mark.asyncio
async def test_async_focus_session_not_found() -> None:
    """Test session not found."""
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
        result = await async_focus_session("test_session_id")

    assert result is False


@pytest.mark.asyncio
async def test_async_focus_session_connection_error() -> None:
    """Test connection error handling."""
    with patch(
        "iterm2.Connection.async_create", side_effect=Exception("Connection failed")
    ), pytest.raises(FocusError) as exc_info:
        await async_focus_session("test_session_id")

    assert "Unexpected error: Connection failed" in str(exc_info.value)


def test_focus_session_success() -> None:
    """Test synchronous focus_session wrapper."""
    with patch(
        "iterm2_focus.focus.async_focus_session", return_value=True
    ) as mock_async:
        result = focus_session("test_session_id")

    assert result is True
    mock_async.assert_called_once_with("test_session_id")


def test_focus_session_not_found() -> None:
    """Test synchronous focus_session when session not found."""
    with patch(
        "iterm2_focus.focus.async_focus_session", return_value=False
    ) as mock_async:
        result = focus_session("test_session_id")

    assert result is False
    mock_async.assert_called_once_with("test_session_id")


def test_focus_session_error() -> None:
    """Test synchronous focus_session error handling."""
    with patch(
        "iterm2_focus.focus.async_focus_session", side_effect=FocusError("Test error")
    ), pytest.raises(FocusError) as exc_info:
        focus_session("test_session_id")

    assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_focus_session_connection_error_specific() -> None:
    """Test specific ConnectionError handling."""
    with patch(
        "iterm2.Connection.async_create",
        side_effect=ConnectionError("Connection refused"),
    ), pytest.raises(FocusError) as exc_info:
        await async_focus_session("test_session_id")

    assert "Failed to connect to iTerm2" in str(exc_info.value)
    assert "Connection refused" in str(exc_info.value)
    assert "Make sure iTerm2 is running and Python API is enabled" in str(
        exc_info.value
    )
