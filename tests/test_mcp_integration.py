"""Integration tests for iterm2-focus MCP server."""

import pytest

from tests.conftest import MCP_TEST_AVAILABLE, skip_if_no_mcp

if MCP_TEST_AVAILABLE:
    from iterm2_focus.mcp.__main__ import main as mcp_main


class TestMCPIntegration:
    """Test MCP server integration scenarios."""

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_full_workflow(self, mcp_server, client_session, mock_iterm2_for_mcp):
        """Test a complete workflow: list sessions, get current, focus session."""
        async with client_session() as client:
            # Step 1: List all sessions
            result = await client.list_tools()
            assert len(result.tools) == 3

            # Step 2: Get list of sessions
            result = await client.call_tool("list_sessions", {})
            sessions = result.structuredContent["result"]
            assert len(sessions) > 0

            # Remember the first session
            target_session = sessions[0]
            target_id = target_session["session_id"]

            # Step 3: Get current session
            result = await client.call_tool("get_current_session", {})
            current = result.structuredContent["result"]
            assert current is not None
            assert current["session_id"] == target_id  # Should be same in our mock

            # Step 4: Focus a session
            result = await client.call_tool("focus_session", {"session_id": target_id})
            focus_result = result.structuredContent
            assert focus_result["success"] is True

            # Verify all iTerm2 methods were called
            assert mock_iterm2_for_mcp.Connection.async_create.called
            assert mock_iterm2_for_mcp.async_get_app.called

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_multiple_windows_navigation(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test navigation across multiple windows."""
        # Import AsyncMock from unittest.mock
        from unittest.mock import AsyncMock

        # Get mock app
        mock_app = await mock_iterm2_for_mcp.async_get_app()

        # Create second window with sessions
        window2 = mock_iterm2_for_mcp.MagicMock()
        window2.window_id = "w1"
        window2.async_activate = AsyncMock()

        tab2 = mock_iterm2_for_mcp.MagicMock()
        tab2.tab_id = "t0"
        tab2.async_select = AsyncMock()

        session2 = mock_iterm2_for_mcp.MagicMock()
        session2.session_id = "w1t0p0:second-window-session"
        session2.async_activate = AsyncMock()
        session2.async_get_profile = AsyncMock(
            return_value={"Title": "Window 2 Session", "Name": "W2S1"}
        )

        tab2.sessions = [session2]
        window2.tabs = [tab2]
        window2.current_tab = tab2

        # Add second window
        mock_app.terminal_windows.append(window2)
        mock_app.windows.append(window2)

        async with client_session() as client:
            # List all sessions across windows
            result = await client.call_tool("list_sessions", {})
            sessions = result.structuredContent["result"]

            # Should have sessions from both windows
            assert len(sessions) == 2
            window_ids = {s["window_id"] for s in sessions}
            assert window_ids == {"w0", "w1"}

            # Focus session in second window
            result = await client.call_tool(
                "focus_session", {"session_id": "w1t0p0:second-window-session"}
            )
            focus_result = result.structuredContent
            assert focus_result["success"] is True

            # Verify second window was activated (at least once)
            window2.async_activate.assert_called()
            tab2.async_select.assert_called()
            session2.async_activate.assert_called()

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_error_recovery(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test error recovery in workflow."""
        async with client_session() as client:
            # First call succeeds
            result = await client.call_tool("list_sessions", {})
            sessions = result.structuredContent["result"]
            assert len(sessions) == 1

            # Make connection fail for next call
            mock_iterm2_for_mcp.Connection.async_create.side_effect = Exception(
                "Connection lost"
            )

            # List sessions should return empty list
            result = await client.call_tool("list_sessions", {})
            sessions = result.structuredContent["result"]
            assert sessions == []

            # Focus should fail gracefully
            result = await client.call_tool(
                "focus_session", {"session_id": "any-session"}
            )
            focus_result = result.structuredContent
            assert focus_result["success"] is False
            assert "Failed" in focus_result["message"]

            # Reset connection
            mock_iterm2_for_mcp.Connection.async_create.side_effect = None
            mock_iterm2_for_mcp.Connection.async_create.return_value = (
                mock_iterm2_for_mcp.AsyncMock()
            )

            # Should work again
            result = await client.call_tool("list_sessions", {})
            sessions = result.structuredContent["result"]
            assert len(sessions) == 1

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_concurrent_operations(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test concurrent tool calls."""
        import asyncio

        async with client_session() as client:
            # Run multiple operations concurrently
            tasks = [
                client.call_tool("list_sessions", {}),
                client.call_tool("get_current_session", {}),
                client.call_tool("list_sessions", {}),  # Duplicate intentionally
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed
            assert len(results) == 3
            for result in results:
                assert not isinstance(result, Exception)
                assert result.structuredContent is not None

    @skip_if_no_mcp
    def test_mcp_main_import(self):
        """Test that MCP main can be imported."""
        # This tests that the __main__.py module works correctly
        assert mcp_main is not None
        assert callable(mcp_main)

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_empty_terminal_state(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test behavior when iTerm2 has no windows/sessions."""
        # Get mock app and clear it
        mock_app = await mock_iterm2_for_mcp.async_get_app()
        mock_app.terminal_windows = []
        mock_app.windows = []
        mock_app.current_terminal_window = None

        async with client_session() as client:
            # List sessions should return empty
            result = await client.call_tool("list_sessions", {})
            sessions = result.structuredContent["result"]
            assert sessions == []

            # Get current should return None
            result = await client.call_tool("get_current_session", {})
            current = result.structuredContent["result"]
            assert current is None

            # Focus should fail
            result = await client.call_tool(
                "focus_session", {"session_id": "any-session"}
            )
            focus_result = result.structuredContent
            assert focus_result["success"] is False
            assert "not found" in focus_result["message"]
