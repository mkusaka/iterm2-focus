# iTerm2 Focus Notification Scripts

## Quick One-liner

Send a notification that focuses the current iTerm2 session when clicked:

```bash
terminal-notifier -title "Task Complete" -message "Click to focus" -execute "/Users/masatomokusaka/.local/bin/uvx iterm2-focus $ITERM_SESSION_ID"
```

Note: Replace `/Users/masatomokusaka/.local/bin/uvx` with your actual uvx path (find it with `which uvx`).

This directory contains scripts that integrate `terminal-notifier` with `iterm2-focus` to send macOS notifications that can focus specific iTerm2 sessions when clicked.

## Prerequisites

1. **terminal-notifier** - Install via Homebrew:
   ```bash
   brew install terminal-notifier
   ```

2. **iterm2-focus** - Should already be installed in this project:
   ```bash
   # Install from this project
   make install
   # or
   uv sync --all-extras --dev
   ```

## Scripts Overview

### 1. `notify-focus.py` - Main notification script
Full-featured Python script with terminal-notifier integration.

**Basic usage:**
```bash
# Notify for specific session
./notify-focus.py w0t0p0:SESSION_ID "Title" "Message"

# Notify for current session
./notify-focus.py --current "Task Done" "Your task completed"

# Send test notifications for all sessions
./notify-focus.py --list
```

**Advanced options:**
- `--icon PATH` - Custom notification icon
- `--timeout SECONDS` - Auto-dismiss timeout
- `--subtitle TEXT` - Additional subtitle text

### 2. `watch-and-notify.sh` - Command watcher
Runs a command and sends notification when it completes.

```bash
# Watch a build command
./watch-and-notify.sh make build

# Watch tests
./watch-and-notify.sh npm test

# Watch any command
./watch-and-notify.sh "python long_script.py"
```

The notification will show:
- ✓ Success (green) if command exits with 0
- ✗ Failure (red) if command fails
- Duration of the command
- Click to focus the terminal where it ran

### 3. `notify-with-osascript.sh` - Native macOS notifications
Alternative using built-in osascript (limited functionality).

```bash
# Note: These notifications cannot focus sessions on click
./notify-with-osascript.sh --current "Info" "Native notification"
```

### 4. `examples.sh` - Usage examples
Run this to see various usage examples and patterns.

```bash
./examples.sh
```

## Real-World Use Cases

### Long-running builds
```bash
# In your build script
make clean && make all && \
  notify-focus.py --current "Build Success" "Build completed" || \
  notify-focus.py --current "Build Failed" "Check errors"
```

### Background jobs
```bash
# Start a background job with notification
(
  python data_processing.py && \
  notify-focus.py --current "Processing Done" "Dataset ready"
) &
```

### Git hooks
Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
if [[ -n "$ITERM_SESSION_ID" ]]; then
  notify-focus.py --current "Git" "Commit successful"
fi
```

### SSH operations
```bash
SESSION=$ITERM_SESSION_ID
ssh server 'backup.sh' && \
  notify-focus.py $SESSION "Backup Complete" "Remote backup finished"
```

### Test watchers
```bash
# Watch tests and notify on completion
while true; do
  ./watch-and-notify.sh pytest
  echo "Press Ctrl+C to stop, any key to run again..."
  read -n 1
done
```

## How It Works

1. **Notification Creation**: Scripts use `terminal-notifier` to create macOS notifications
2. **Click Handler**: Each notification has an associated shell script in `/tmp/` that executes `iterm2-focus SESSION_ID`
3. **Session Focus**: When clicked, the notification runs the script which focuses the specified iTerm2 session
4. **Cleanup**: Temporary scripts are cleaned up automatically

## Tips

- Notifications are grouped by session ID to prevent duplicates
- Use `--quiet` flag with `iterm2-focus` in scripts to suppress output
- Combine with `fswatch`, `entr`, or `watchman` for file monitoring
- Works great with `tmux` or `screen` sessions in iTerm2

## Troubleshooting

1. **"terminal-notifier not found"**
   - Install with: `brew install terminal-notifier`

2. **Notifications don't appear**
   - Check System Preferences > Notifications > terminal-notifier
   - Ensure notifications are enabled

3. **Clicking doesn't focus session**
   - Verify iTerm2 is running
   - Check that session ID is valid with `iterm2-focus --list`
   - Ensure iterm2-focus is in PATH

4. **Permission errors**
   - Scripts need execute permission: `chmod +x script_name.sh`
   - May need to allow terminal-notifier in Security settings