"""MCP server implementation for iterm2-focus."""

import sys

# MCP requires Python 3.10+
MCP_AVAILABLE = sys.version_info >= (3, 10)

if MCP_AVAILABLE:
    try:
        from .server import mcp
        from .tools import *
    except ImportError:
        MCP_AVAILABLE = False
        mcp = None
else:
    mcp = None

__all__ = ["mcp", "MCP_AVAILABLE"]

