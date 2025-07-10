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

You can run `isf` directly without installing using `uvx`:

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
2. **Python 3.8** or later
3. **iTerm2 Python API** must be enabled:
   - Open iTerm2
   - Go to *Settings* → *General* → *Magic*
   - Check "Enable Python API"
   - Restart iTerm2

## Usage

### Focus a specific session

```bash
isf w0t0p0:12345678-1234-1234-1234-123456789012
```

### Focus the current session

Useful when returning from another application:

```bash
isf --current
# or
isf -c
```

### Get the current session ID

```bash
isf --get-current
# or
isf -g
```

### List all sessions

```bash
isf --list
# or
isf -l
```

### Additional options

```bash
# Show version
isf --version

# Quiet mode (suppress output)
isf -q <session-id>

# Help
isf --help
```

## Examples

### Save and restore focus

```bash
# Save current session ID
SAVED_SESSION=$(isf -g -q)

# ... do other work ...

# Return to saved session
isf $SAVED_SESSION
```

### Focus a session from another application

```applescript
-- AppleScript example
do shell script "isf w0t0p0:12345678-1234-1234-1234-123456789012"
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

Verify the session ID using `isf --list` to see all available sessions.

### Permission errors

On first run, macOS may ask for permission to control iTerm2. Please allow this in System Preferences.

## Author

mkusaka <hinoshita1992@gmail.com>
