# iterm2-focus

Focus iTerm2 sessions by ID from the command line.

## Features

- Focus any iTerm2 session by its ID
- Get the current session ID
- List all available sessions
- Focus the current session (useful when returning from other applications)

## Installation

```bash
pip install iterm2-focus
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install iterm2-focus
```

## Quick Usage (without installation)

You can run `iterm2-focus` directly without installing using `uvx`:

```bash
# List all sessions
uvx iterm2-focus --list

# Focus a specific session
uvx iterm2-focus <session-id>

# Get current session ID
uvx iterm2-focus --get-current
```

## Prerequisites

1. **macOS** with iTerm2 installed
2. **Python 3.8** or later (Python 3.10+ required for MCP server)
3. **iTerm2 Python API** must be enabled:
   - Open iTerm2
   - Go to *Settings* → *General* → *Magic*
   - Check "Enable Python API"
   - Restart iTerm2

## Usage

### Focus a specific session

```bash
iterm2-focus w0t0p0:12345678-1234-1234-1234-123456789012
```

### Focus the current session

Useful when returning from another application:

```bash
iterm2-focus --current
# or
iterm2-focus -c
```

### Get the current session ID

```bash
iterm2-focus --get-current
# or
iterm2-focus -g
```

### List all sessions

```bash
iterm2-focus --list
# or
iterm2-focus -l
```

### Additional options

```bash
# Show version
iterm2-focus --version

# Quiet mode (suppress output)
iterm2-focus -q <session-id>

# Help
iterm2-focus --help
```

## MCP Server Mode (Python 3.10+)

`iterm2-focus` can run as an MCP (Model Context Protocol) server, allowing LLM applications like Claude Desktop to control iTerm2 sessions.

### Starting the MCP server

```bash
# Install with MCP support
pip install 'iterm2-focus[mcp]'

# Start the MCP server
iterm2-focus --mcp
```

### Configuring Claude Desktop

Using Claude Code CLI (recommended):

```bash
# Add the MCP server using uvx (no installation required)
claude mcp add iterm2-focus uvx iterm2-focus --mcp

# Or if you have it installed locally
claude mcp add iterm2-focus iterm2-focus --mcp
```

Or manually add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "iterm2-focus": {
      "command": "uvx",
      "args": ["iterm2-focus", "--mcp"]
    }
  }
}
```

Or if you have it installed locally:

```json
{
  "mcpServers": {
    "iterm2-focus": {
      "command": "iterm2-focus",
      "args": ["--mcp"]
    }
  }
}
```

### Available MCP tools

- **list_sessions**: List all iTerm2 sessions with their IDs and metadata
- **focus_session**: Focus a specific session by ID
- **get_current_session**: Get information about the currently focused session

## Examples

### Save and restore focus

```bash
# Save current session ID
SAVED_SESSION=$(iterm2-focus -g -q)

# ... do other work ...

# Return to saved session
iterm2-focus $SAVED_SESSION
```

### Focus a session from another application

```applescript
-- AppleScript example
do shell script "iterm2-focus w0t0p0:12345678-1234-1234-1234-123456789012"
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mkusaka/iterm2-focus
cd iterm2-focus

# Create virtual environment with uv
uv venv
uv pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=iterm2_focus

# Type checking
uv run mypy src

# Linting and formatting
uv run ruff check src tests
uv run black src tests
```

### Building

```bash
# Build the package
uv build

# Upload to PyPI
uv publish
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### "Failed to connect to iTerm2" error

Make sure iTerm2's Python API is enabled (see Prerequisites).

### "Session not found" error

Verify the session ID using `iterm2-focus --list` to see all available sessions.

### Permission errors

On first run, macOS may ask for permission to control iTerm2. Please allow this in System Preferences.

## Author

mkusaka <hinoshita1992@gmail.com>
