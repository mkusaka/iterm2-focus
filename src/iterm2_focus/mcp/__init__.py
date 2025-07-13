"""MCP server implementation for iterm2-focus."""

import sys

# MCP requires Python 3.10+
MCP_AVAILABLE = sys.version_info >= (3, 10)

if MCP_AVAILABLE:
    try:
        from .server import mcp
        from .tools import focus_session, get_current_session, list_sessions
    except ImportError:
        MCP_AVAILABLE = False
        mcp = None
        focus_session = None
        get_current_session = None
        list_sessions = None
else:
    mcp = None
    focus_session = None
    get_current_session = None
    list_sessions = None

__all__ = ["mcp", "MCP_AVAILABLE"]
