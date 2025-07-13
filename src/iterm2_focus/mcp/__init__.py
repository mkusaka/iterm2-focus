"""MCP server implementation for iterm2-focus."""

from typing import Any

# Initialize with None, will be overridden if import succeeds
mcp: Any | None = None
focus_session: Any | None = None
get_current_session: Any | None = None
list_sessions: Any | None = None
MCP_AVAILABLE = False

try:
    from .server import mcp
    from .tools import focus_session, get_current_session, list_sessions

    MCP_AVAILABLE = True
except ImportError:
    # MCP dependencies not installed - keep the None values
    pass

__all__ = [
    "mcp",
    "MCP_AVAILABLE",
    "focus_session",
    "get_current_session",
    "list_sessions",
]
