"""Tests for the iterm2-focus MCP server."""

import pytest

from tests.conftest import MCP_TEST_AVAILABLE, skip_if_no_mcp

if MCP_TEST_AVAILABLE:
    from iterm2_focus.mcp import MCP_AVAILABLE


class TestMCPServer:
    """Test basic MCP server functionality."""

    @skip_if_no_mcp
    def test_mcp_available(self):
        """Test that MCP is available when requirements are met."""
        assert MCP_AVAILABLE is True

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_create_server(self, mcp_server):
        """Test MCP server creation."""
        assert mcp_server is not None
        assert mcp_server.name == "iterm2-focus"
        # Description and version are passed but not exposed as attributes
        assert hasattr(mcp_server, "_mcp_server")

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_list_tools(self, mcp_server, client_session):
        """Test that all tools are registered."""
        async with client_session() as client:
            tools = await client.list_tools()

            # Check that we have exactly 3 tools
            assert len(tools.tools) == 3

            # Check tool names
            tool_names = {tool.name for tool in tools.tools}
            expected_tools = {"list_sessions", "focus_session", "get_current_session"}
            assert tool_names == expected_tools

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_tool_descriptions(self, mcp_server, client_session):
        """Test that tools have proper descriptions."""
        async with client_session() as client:
            tools = await client.list_tools()

            for tool in tools.tools:
                assert tool.description is not None
                assert len(tool.description) > 0

                # Check specific descriptions
                if tool.name == "list_sessions":
                    assert "List all available iTerm2 sessions" in tool.description
                elif tool.name == "focus_session":
                    assert "Focus a specific iTerm2 session by ID" in tool.description
                elif tool.name == "get_current_session":
                    assert (
                        "Get information about the currently focused"
                        in tool.description
                    )

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_tool_schemas(self, mcp_server, client_session):
        """Test that tools have proper input/output schemas."""
        async with client_session() as client:
            tools = await client.list_tools()

            for tool in tools.tools:
                # Check input schemas
                if tool.name == "focus_session":
                    # focus_session should have required session_id parameter
                    assert tool.inputSchema is not None
                    assert "properties" in tool.inputSchema
                    assert "session_id" in tool.inputSchema["properties"]
                    assert "required" in tool.inputSchema
                    assert "session_id" in tool.inputSchema["required"]
                elif tool.name in ["list_sessions", "get_current_session"]:
                    # These tools don't require input
                    if tool.inputSchema:
                        assert tool.inputSchema.get("required", []) == []

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_server_capabilities(self, mcp_server):
        """Test server capabilities."""
        # Check that the server has the expected capabilities
        assert hasattr(mcp_server, "_mcp_server")

        # The server should support tools (capabilities are auto-discovered)
        # We can't directly call get_capabilities without a request context

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_tool_error_handling(
        self, mcp_server, client_session, mock_iterm2_for_mcp
    ):
        """Test error handling when iTerm2 connection fails."""
        # Make the connection fail
        mock_iterm2_for_mcp.Connection.async_create.side_effect = Exception(
            "Connection failed"
        )

        async with client_session() as client:
            # Try to list sessions
            result = await client.call_tool("list_sessions", {})

            # Should return empty list on error via structured content
            assert (
                result.isError is False
            )  # Tool returns [] on error, not an error result
            assert result.structuredContent is not None
            assert result.structuredContent == {"result": []}

    @skip_if_no_mcp
    @pytest.mark.anyio
    async def test_invalid_tool_call(self, mcp_server, client_session):
        """Test calling a non-existent tool."""
        async with client_session() as client:
            result = await client.call_tool("non_existent_tool", {})

            # FastMCP returns an error result instead of raising an exception
            assert result.isError is True
            # Check that error message indicates unknown tool
            error_content = result.content[0]
            assert (
                "unknown tool" in error_content.text.lower()
                or "not found" in error_content.text.lower()
            )
