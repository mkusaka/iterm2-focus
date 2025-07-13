"""Entry point for running the MCP server."""

import sys

# Check Python version before importing MCP
if sys.version_info < (3, 10):
    print("Error: MCP server requires Python 3.10 or higher.", file=sys.stderr)
    print(f"Current Python version: {sys.version}", file=sys.stderr)
    sys.exit(1)

try:
    from .server import mcp
    from .tools import *  # Import all tools to register them
except ImportError as e:
    print(f"Error: Failed to import MCP dependencies: {e}", file=sys.stderr)
    print("Please install with: pip install 'iterm2-focus[mcp]'", file=sys.stderr)
    sys.exit(1)


def main():
    """Run the MCP server."""
    # Run with STDIO transport (default for Claude Desktop and other MCP clients)
    mcp.run()


if __name__ == "__main__":
    main()
