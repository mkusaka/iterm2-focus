"""Utility functions for iterm2-focus."""

import asyncio
from typing import Any

import iterm2


async def get_session_info(session_id: str) -> dict[str, Any] | None:
    """Get detailed information about a session.

    Args:
        session_id: The iTerm2 session ID

    Returns:
        Dictionary with session information or None if not found
    """
    connection: Any | None = None

    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    if session.session_id == session_id:
                        name: str | None = await session.async_get_variable(
                            "session.name"
                        )
                        hostname: str | None = await session.async_get_variable(
                            "hostname"
                        )
                        username: str | None = await session.async_get_variable(
                            "username"
                        )
                        path: str | None = await session.async_get_variable("path")
                        tty: str | None = await session.async_get_variable("tty")

                        return {
                            "id": session_id,
                            "name": name,
                            "hostname": hostname,
                            "username": username,
                            "path": path,
                            "tty": tty,
                            "window_id": window.window_id,
                            "tab_id": tab.tab_id,
                        }
        return None
    finally:
        # Connection will be closed automatically
        pass


async def focus_session_by_name(name_pattern: str) -> bool:
    """Focus a session by name pattern (partial match).

    Args:
        name_pattern: Pattern to search in session names (case-insensitive)

    Returns:
        True if a matching session was found and focused, False otherwise
    """
    connection: Any | None = None

    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

        name_lower = name_pattern.lower()

        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    session_name: str | None = await session.async_get_variable(
                        "session.name"
                    )
                    if session_name and name_lower in session_name.lower():
                        await session.async_activate()
                        await tab.async_select()
                        await window.async_activate()
                        return True

        return False
    finally:
        # Connection will be closed automatically
        pass


async def get_all_sessions() -> list[dict[str, Any]]:
    """Get information about all sessions.

    Returns:
        List of dictionaries with session information
    """
    connection: Any | None = None

    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

        sessions: list[dict[str, Any]] = []

        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    name: str | None = await session.async_get_variable("session.name")
                    hostname: str | None = await session.async_get_variable("hostname")
                    username: str | None = await session.async_get_variable("username")
                    path: str | None = await session.async_get_variable("path")

                    sessions.append(
                        {
                            "id": session.session_id,
                            "name": name or "Unnamed",
                            "window_id": window.window_id,
                            "tab_id": tab.tab_id,
                            "hostname": hostname,
                            "username": username,
                            "path": path,
                        }
                    )
        return sessions
    finally:
        # Connection will be closed automatically
        pass


def run_async(coro: Any) -> Any:
    """Run an async coroutine in a sync context.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine
    """
    return asyncio.run(coro)
