"""Entry point for running the MCP server."""

import sys

try:
    from .server import mcp
    from .tools import focus_session, get_current_session, list_sessions  # noqa: F401
except ImportError as e:
    print(f"Error: Failed to import MCP dependencies: {e}", file=sys.stderr)
    print("Please install with: pip install 'iterm2-focus[mcp]'", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    """Run the MCP server."""
    # Run with STDIO transport (default for Claude Desktop and other MCP clients)
    mcp.run()


if __name__ == "__main__":
    main()
