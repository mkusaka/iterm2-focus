"""MCP server implementation for iterm2-focus."""

import sys
from typing import TYPE_CHECKING

# MCP requires Python 3.10+
MCP_AVAILABLE = sys.version_info >= (3, 10)

if TYPE_CHECKING:
    # Type checking imports
    from typing import Any, Optional

    mcp: Optional[Any] = None
    focus_session: Optional[Any] = None
    get_current_session: Optional[Any] = None
    list_sessions: Optional[Any] = None
elif MCP_AVAILABLE:
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
