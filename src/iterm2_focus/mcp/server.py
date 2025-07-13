"""MCP server instance for iterm2-focus."""

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    "iterm2-focus",
    description="Focus iTerm2 sessions by ID through MCP",
    version="0.1.0",
)
