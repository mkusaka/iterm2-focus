"""Core functionality for focusing iTerm2 sessions using Python API."""

import asyncio
from typing import Any, Optional

import iterm2


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
    connection: Optional[Any] = None

    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

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
