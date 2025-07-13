"""Pytest configuration for iterm2-focus tests."""

import sys

import pytest
from pytest_mock import MockerFixture

# Check if MCP is available
try:
    from mcp.shared.memory import create_connected_server_and_client_session

    MCP_TEST_AVAILABLE = True
except ImportError:
    MCP_TEST_AVAILABLE = False

# Mark to skip MCP tests
skip_if_no_mcp = pytest.mark.skipif(
    not MCP_TEST_AVAILABLE,
    reason="MCP not available (requires mcp[cli] package)",
)


@pytest.fixture
def anyio_backend():
    """Set anyio backend to asyncio for all tests."""
    return "asyncio"


if MCP_TEST_AVAILABLE:

    @pytest.fixture
    def mock_iterm2_for_mcp(mocker):
        """Mock iTerm2 for MCP tests."""
        mock_iterm2_module = mocker.MagicMock()

        # Mock Connection class
        mock_connection_instance = mocker.AsyncMock()
        mock_connection_class = mocker.MagicMock()
        mock_connection_class.async_create = mocker.AsyncMock(
            return_value=mock_connection_instance
        )
        mock_iterm2_module.Connection = mock_connection_class

        # Mock App
        mock_app = mocker.MagicMock()
        mock_iterm2_module.async_get_app = mocker.AsyncMock(return_value=mock_app)

        # Mock Window
        mock_window = mocker.MagicMock()
        mock_window.window_id = "w0"
        mock_window.async_activate = mocker.AsyncMock()

        # Mock Tab
        mock_tab = mocker.MagicMock()
        mock_tab.tab_id = "t0"
        mock_tab.async_select = mocker.AsyncMock()

        # Mock Session
        mock_session = mocker.MagicMock()
        mock_session.session_id = "w0t0p0:12345678-1234-1234-1234-123456789012"
        mock_session.async_activate = mocker.AsyncMock()
        mock_session.async_get_profile = mocker.AsyncMock(
            return_value={"Title": "Test Session", "Name": "Session Name"}
        )

        # Wire up the relationships
        mock_tab.sessions = [mock_session]
        mock_window.tabs = [mock_tab]
        mock_window.current_tab = mock_tab
        mock_tab.current_session = mock_session
        mock_app.terminal_windows = [mock_window]
        mock_app.windows = [mock_window]
        mock_app.current_terminal_window = mock_window

        # Patch the iterm2 module for MCP imports
        mocker.patch("iterm2_focus.mcp.tools.iterm_tools.iterm2", mock_iterm2_module)

        return mock_iterm2_module

    @pytest.fixture
    async def mcp_server(mock_iterm2_for_mcp):
        """Create an iterm2-focus MCP server instance for testing."""
        # Import server AFTER mock_iterm2 is set up
        from iterm2_focus.mcp.server import mcp

        return mcp

    @pytest.fixture
    async def client_session(mcp_server):
        """Create a connected client session to the MCP server."""
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _client_session():
            async with create_connected_server_and_client_session(
                mcp_server._mcp_server
            ) as client:
                yield client

        return _client_session


@pytest.fixture(autouse=True)
def mock_iterm2(mocker: MockerFixture, request):
    """Mock iTerm2 API for testing without real iTerm2.

    This is autouse to ensure iterm2 is always mocked in tests,
    preventing accidental connections to real iTerm2.
    """
    # Skip for real integration tests
    if "integration" in request.keywords:
        yield None
        return

    # Skip for tests that handle their own iterm2 mocking
    if request.node.name.startswith(
        "test_async_focus_"
    ) or request.node.name.startswith("test_focus_session"):
        yield None
        return

    # Skip for MCP tests - they'll use their own mock
    if any(
        part in str(request.fspath)
        for part in ["test_mcp", "test_iterm_tools", "test_utils"]
    ):
        yield None
        return

    # Mock the iterm2 module before any imports
    mock_iterm2_module = mocker.MagicMock()

    # Mock Connection class
    mock_connection_instance = mocker.AsyncMock()
    mock_connection_class = mocker.MagicMock()
    mock_connection_class.async_create = mocker.AsyncMock(
        return_value=mock_connection_instance
    )
    mock_iterm2_module.Connection = mock_connection_class

    # Mock App
    mock_app = mocker.MagicMock()
    mock_iterm2_module.async_get_app = mocker.AsyncMock(return_value=mock_app)

    # Mock Window
    mock_window = mocker.MagicMock()
    mock_window.window_id = "w0"
    mock_window.async_activate = mocker.AsyncMock()

    # Mock Tab
    mock_tab = mocker.MagicMock()
    mock_tab.tab_id = "t0"
    mock_tab.async_select = mocker.AsyncMock()

    # Mock Session
    mock_session = mocker.MagicMock()
    mock_session.session_id = "w0t0p0:12345678-1234-1234-1234-123456789012"
    mock_session.async_activate = mocker.AsyncMock()
    mock_session.async_get_profile = mocker.AsyncMock(
        return_value={"Title": "Test Session", "Name": "Session Name"}
    )

    # Wire up the relationships
    mock_tab.sessions = [mock_session]
    mock_window.tabs = [mock_tab]
    mock_window.current_tab = mock_tab
    mock_tab.current_session = mock_session
    mock_app.terminal_windows = [mock_window]
    mock_app.windows = [mock_window]
    mock_app.current_terminal_window = mock_window

    # Patch the iterm2 module at import level
    # This ensures any imports of iterm2 get the mock
    original_iterm2 = sys.modules.get("iterm2")
    sys.modules["iterm2"] = mock_iterm2_module

    # Also patch at the import name level for dynamic imports
    mocker.patch("iterm2_focus.mcp.tools.iterm_tools.iterm2", mock_iterm2_module)

    yield mock_iterm2_module

    # Restore original if it existed
    if original_iterm2:
        sys.modules["iterm2"] = original_iterm2
    else:
        sys.modules.pop("iterm2", None)
