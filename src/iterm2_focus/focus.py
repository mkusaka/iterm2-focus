"""Core functionality for focusing iTerm2 sessions using Python API."""

import asyncio
from typing import Any

from iterm2.app import async_get_app
from iterm2.connection import Connection


class FocusError(Exception):
    """Error raised when focusing fails."""

    pass


async def async_focus_session(session_id: str) -> bool:
    """Focus the iTerm2 session with the given ID (async version).

    Args:
        session_id: The iTerm2 session ID (e.g., "w0t0p0:UUID")

    Returns:
        True if successful, False if session not found

    Raises:
        FocusError: If there's an error connecting to iTerm2
    """
    connection: Any | None = None

    try:
        connection = await Connection.async_create()
        app = await async_get_app(connection)
        if app is None:
            raise FocusError("Failed to get iTerm2 app instance.")

        # Search through all windows, tabs, and sessions
        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    if session.session_id == session_id:
                        # Focus the session
                        await session.async_activate()
                        await tab.async_select()
                        await window.async_activate()
                        return True

        return False

    except ConnectionError as e:
        raise FocusError(
            f"Failed to connect to iTerm2: {e}. "
            "Make sure iTerm2 is running and Python API is enabled."
        ) from e
    except Exception as e:
        raise FocusError(f"Unexpected error: {e}") from e
    finally:
        # Connection will be closed automatically
        pass


def focus_session(session_id: str) -> bool:
    """Focus the iTerm2 session with the given ID.

    Args:
        session_id: The iTerm2 session ID (e.g., "w0t0p0:UUID")

    Returns:
        True if successful, False if session not found

    Raises:
        FocusError: If there's an error executing the operation
    """
    # iTerm2 Python APIはasyncioベースなので、同期的に実行
    return asyncio.run(async_focus_session(session_id))
