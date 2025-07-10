"""CLI interface for iterm2-focus."""

import asyncio
import os
import sys
from typing import Dict, List, NoReturn, Optional

import click
import iterm2

from . import __version__
from .focus import FocusError, focus_session


@click.command()
@click.argument("session_id", required=False, default=None)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    help="Show version and exit.",
)
@click.option(
    "--current",
    "-c",
    is_flag=True,
    help="Focus the current session (uses $ITERM_SESSION_ID).",
)
@click.option(
    "--get-current",
    "-g",
    is_flag=True,
    help="Get the current session ID and exit.",
)
@click.option(
    "--list",
    "-l",
    "list_sessions",
    is_flag=True,
    help="List all available sessions.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress output messages.",
)
def main(
    session_id: Optional[str],
    version: bool,
    current: bool,
    get_current: bool,
    list_sessions: bool,
    quiet: bool,
) -> None:
    """Focus iTerm2 session by ID.

    \b
    Examples:
        isf w0t0p0:12345678-1234-1234-1234-123456789012
        isf --current
        isf -c
        isf --get-current
        isf -g
        isf --list
    """
    if version:
        click.echo(f"iterm2-focus {__version__}")
        sys.exit(0)

    if get_current:
        _get_current_session_id(quiet)
        sys.exit(0)

    if list_sessions:
        _list_sessions()
        sys.exit(0)

    if current:
        session_id = os.environ.get("ITERM_SESSION_ID")
        if not session_id:
            _error_exit(
                "ITERM_SESSION_ID environment variable not found.",
                "Are you running this from within iTerm2?",
            )
        # Remove the prefix (e.g., "w0t5p1:") if present
        if ":" in session_id:
            session_id = session_id.split(":", 1)[1]
    elif not session_id:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    # Type narrowing: session_id is definitely not None here
    assert session_id is not None

    # Remove the prefix (e.g., "w0t5p1:") if present
    if ":" in session_id:
        session_id = session_id.split(":", 1)[1]

    try:
        result = focus_session(session_id)
        if result:
            if not quiet:
                click.echo(f"Focused session: {session_id}")
        else:
            _error_exit(f"Session not found: {session_id}")
    except FocusError as e:
        _error_exit(
            str(e),
            "",
            "Make sure iTerm2's Python API is enabled:",
            "iTerm2 → Settings → General → Magic → Enable Python API",
        )


def _error_exit(*messages: str) -> NoReturn:
    """Print error messages and exit with status 1."""
    for i, msg in enumerate(messages):
        if i == 0:
            click.echo(f"Error: {msg}", err=True)
        else:
            click.echo(msg, err=True)
    sys.exit(1)


def _get_current_session_id(quiet: bool) -> None:
    """Get and display the current session ID."""
    session_id = os.environ.get("ITERM_SESSION_ID")
    if session_id:
        # Remove the prefix (e.g., "w0t5p1:") if present
        if ":" in session_id:
            session_id = session_id.split(":", 1)[1]
        click.echo(session_id)
    else:
        _error_exit(
            "ITERM_SESSION_ID environment variable not found.",
            "Are you running this from within iTerm2?",
        )


def _list_sessions() -> None:
    """List all available iTerm2 sessions."""

    async def list_all_sessions() -> List[Dict[str, Optional[str]]]:
        """Async function to get all sessions."""
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

        sessions: List[Dict[str, Optional[str]]] = []
        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    name = await session.async_get_variable("session.name")
                    hostname = await session.async_get_variable("hostname")
                    username = await session.async_get_variable("username")
                    path = await session.async_get_variable("path")

                    sessions.append(
                        {
                            "id": session.session_id,
                            "name": name or "Unnamed",
                            "window": window.window_id,
                            "tab": tab.tab_id,
                            "hostname": hostname,
                            "username": username,
                            "path": path,
                        }
                    )
        return sessions

    try:
        sessions = asyncio.run(list_all_sessions())

        if not sessions:
            click.echo("No sessions found.")
            return

        click.echo("Available iTerm2 sessions:")
        click.echo("-" * 80)

        for s in sessions:
            click.echo(f"ID: {s['id']}")
            click.echo(f"  Name: {s['name']}")
            click.echo(f"  Window: {s['window']}, Tab: {s['tab']}")

            if s.get("hostname") and s["hostname"] != "localhost":
                click.echo(f"  Host: {s['username']}@{s['hostname']}")

            if s.get("path"):
                click.echo(f"  Path: {s['path']}")

            click.echo()

    except Exception as e:
        _error_exit(f"Failed to list sessions: {e}")


if __name__ == "__main__":
    main()
