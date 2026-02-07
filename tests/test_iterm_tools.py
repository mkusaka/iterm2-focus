"""Tests for iTerm2-specific MCP tools."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.conftest import MCP_TEST_AVAILABLE, skip_if_no_mcp

if MCP_TEST_AVAILABLE:
    pass


class TestITermTools:
    """Test iTerm2-specific MCP tools."""

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_list_sessions(self, mcp_server, client_session, mock_iterm2_for_mcp):
        """Test list_sessions tool."""
        async with client_session() as client:
            result = await client.call_tool("list_sessions", {})

            # Should return structured content with list of sessions
            assert result.isError is False
            assert result.structuredContent is not None
            assert "result" in result.structuredContent

            sessions = result.structuredContent["result"]
            assert isinstance(sessions, list)
            assert len(sessions) == 1

            # Check session structure
            session = sessions[0]
            assert (
                session["session_id"] == "w0t0p0:12345678-1234-1234-1234-123456789012"
            )
            assert session["window_id"] == "w0"
            assert session["tab_id"] == "t0"
            assert session["is_active"] is True
            assert session["title"] is None
            assert session["name"] == "Session Name"

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_list_sessions_multiple(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test list_sessions with multiple sessions."""
        # Get the mock app to access terminal windows
        mock_app = await mock_iterm2_for_mcp.async_get_app()

        # Add more sessions to the mock
        mock_profile2 = MagicMock()
        mock_profile2.name = "Session 2"
        session2 = MagicMock()
        session2.session_id = "w0t0p1:another-session"
        session2.async_get_profile = AsyncMock(return_value=mock_profile2)

        # Add second session to the same tab
        mock_app.terminal_windows[0].tabs[0].sessions.append(session2)

        async with client_session() as client:
            result = await client.call_tool("list_sessions", {})

            sessions = result.structuredContent["result"]
            assert len(sessions) == 2

            # Check both sessions
            session_ids = {s["session_id"] for s in sessions}
            assert "w0t0p0:12345678-1234-1234-1234-123456789012" in session_ids
            assert "w0t0p1:another-session" in session_ids

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_focus_session_success(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test successful focus_session."""
        async with client_session() as client:
            result = await client.call_tool(
                "focus_session",
                {"session_id": "w0t0p0:12345678-1234-1234-1234-123456789012"},
            )

            # FocusResult returns object fields directly in structuredContent
            assert result.isError is False
            assert result.structuredContent is not None

            # The structuredContent is the FocusResult object directly
            assert result.structuredContent["success"] is True
            assert (
                result.structuredContent["session_id"]
                == "w0t0p0:12345678-1234-1234-1234-123456789012"
            )
            assert "Successfully focused" in result.structuredContent["message"]

            # Verify the session was activated
            mock_app = await mock_iterm2_for_mcp.async_get_app()
            mock_app.terminal_windows[0].async_activate.assert_called_once()
            mock_app.terminal_windows[0].tabs[0].async_select.assert_called_once()
            mock_app.terminal_windows[0].tabs[0].sessions[
                0
            ].async_activate.assert_called_once()

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_focus_session_not_found(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test focus_session with non-existent session."""
        async with client_session() as client:
            result = await client.call_tool(
                "focus_session", {"session_id": "non-existent-session"}
            )

            # Should return structured content with failure
            assert result.isError is False
            assert result.structuredContent is not None

            assert result.structuredContent["success"] is False
            assert result.structuredContent["session_id"] == "non-existent-session"
            assert "not found" in result.structuredContent["message"]

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_focus_session_connection_error(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test focus_session when connection fails."""
        # Make connection fail
        mock_iterm2_for_mcp.Connection.async_create.side_effect = ConnectionError(
            "iTerm2 not running"
        )

        async with client_session() as client:
            result = await client.call_tool(
                "focus_session",
                {"session_id": "w0t0p0:12345678-1234-1234-1234-123456789012"},
            )

            # Should return failure with connection error
            assert result.isError is False
            assert result.structuredContent is not None

            assert result.structuredContent["success"] is False
            assert "Failed to connect" in result.structuredContent["message"]
            assert "iTerm2 not running" in result.structuredContent["message"]

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_get_current_session(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test get_current_session tool."""
        async with client_session() as client:
            result = await client.call_tool("get_current_session", {})

            # Should return structured content with session info
            assert result.isError is False
            assert result.structuredContent is not None

            # get_current_session returns SessionInfo | None, wrapped in result
            assert "result" in result.structuredContent
            session_info = result.structuredContent["result"]

            assert session_info is not None
            assert (
                session_info["session_id"]
                == "w0t0p0:12345678-1234-1234-1234-123456789012"
            )
            assert session_info["window_id"] == "w0"
            assert session_info["tab_id"] == "t0"
            assert session_info["is_active"] is True

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_get_current_session_none(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test get_current_session when no session is active."""
        # Get mock app and remove current window
        mock_app = await mock_iterm2_for_mcp.async_get_app()
        mock_app.current_terminal_window = None

        async with client_session() as client:
            result = await client.call_tool("get_current_session", {})

            # Should return null in structured content
            assert result.isError is False
            assert result.structuredContent is not None
            assert result.structuredContent["result"] is None

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_tool_parameter_validation(self, mcp_server, client_session):
        """Test parameter validation for tools."""
        async with client_session() as client:
            # focus_session without required parameter should return an error
            result = await client.call_tool("focus_session", {})

            # Should return an error result
            assert result.isError is True
            assert len(result.content) > 0
            error_text = result.content[0].text.lower()
            assert (
                "session_id" in error_text
                or "missing" in error_text
                or "required" in error_text
            )

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_tool_return_types(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test that tools return properly formatted responses."""
        async with client_session() as client:
            # Test list_sessions returns array
            result = await client.call_tool("list_sessions", {})
            assert result.structuredContent is not None
            sessions = result.structuredContent["result"]
            assert isinstance(sessions, list)

            # Test focus_session returns object
            result = await client.call_tool(
                "focus_session", {"session_id": "test-session"}
            )
            assert result.structuredContent is not None
            # FocusResult is returned directly as structuredContent
            assert isinstance(result.structuredContent, dict)
            assert "success" in result.structuredContent
            assert "session_id" in result.structuredContent
            assert "message" in result.structuredContent

            # Test get_current_session returns object or null
            result = await client.call_tool("get_current_session", {})
            assert result.structuredContent is not None
            current = result.structuredContent["result"]
            assert current is None or isinstance(current, dict)
