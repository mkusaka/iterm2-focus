"""MCP tools for iTerm2 session management."""

import iterm2
from pydantic import BaseModel, Field

from ..server import mcp


class SessionInfo(BaseModel):
    """Information about an iTerm2 session."""

    session_id: str = Field(description="The unique session ID")
    window_id: str = Field(description="The window ID containing this session")
    tab_id: str = Field(description="The tab ID containing this session")
    is_active: bool = Field(description="Whether this is the currently active session")
    title: str | None = Field(
        default=None, description="The session title if available"
    )
    name: str | None = Field(default=None, description="The session name if available")


class FocusResult(BaseModel):
    """Result of a focus operation."""

    success: bool = Field(description="Whether the operation was successful")
    session_id: str = Field(description="The session ID that was targeted")
    message: str = Field(description="A descriptive message about the operation")


@mcp.tool()
async def list_sessions() -> list[SessionInfo]:
    """List all available iTerm2 sessions.

    Returns a list of all sessions across all windows and tabs,
    including their IDs and whether they're currently active.
    """
    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)
        sessions = []

        # Get the current active session for comparison
        current_window = app.current_terminal_window
        current_session_id = None
        if current_window and current_window.current_tab:
            current_session = current_window.current_tab.current_session
            if current_session:
                current_session_id = current_session.session_id

        # Iterate through all windows, tabs, and sessions
        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    # Get session metadata
                    title = None
                    name = None
                    try:
                        profile = await session.async_get_profile()
                        if profile:
                            title = profile.get("Title")
                            name = profile.get("Name")
                    except Exception:
                        # Ignore errors getting profile info
                        pass

                    sessions.append(
                        SessionInfo(
                            session_id=session.session_id,
                            window_id=window.window_id,
                            tab_id=tab.tab_id,
                            is_active=session.session_id == current_session_id,
                            title=title,
                            name=name,
                        )
                    )

        return sessions

    except Exception:
        # Return empty list on error rather than failing
        return []


@mcp.tool()
async def focus_session(session_id: str) -> FocusResult:
    """Focus a specific iTerm2 session by ID.

    Args:
        session_id: The iTerm2 session ID to focus (e.g., "w0t0p0:UUID")

    Returns:
        FocusResult indicating success or failure with a descriptive message
    """
    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

        # Search for the session
        for window in app.terminal_windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    if session.session_id == session_id:
                        # Focus the session, tab, and window
                        await session.async_activate()
                        await tab.async_select()
                        await window.async_activate()

                        return FocusResult(
                            success=True,
                            session_id=session_id,
                            message=f"Successfully focused session {session_id}",
                        )

        return FocusResult(
            success=False,
            session_id=session_id,
            message=f"Session {session_id} not found",
        )

    except ConnectionError as e:
        return FocusResult(
            success=False,
            session_id=session_id,
            message=f"Failed to connect to iTerm2: {str(e)}. Make sure iTerm2 is running and Python API is enabled.",
        )
    except Exception as e:
        return FocusResult(
            success=False,
            session_id=session_id,
            message=f"Failed to focus session: {str(e)}",
        )


@mcp.tool()
async def get_current_session() -> SessionInfo | None:
    """Get information about the currently focused iTerm2 session.

    Returns:
        SessionInfo about the current session, or None if no session is active
    """
    try:
        connection = await iterm2.Connection.async_create()
        app = await iterm2.async_get_app(connection)

        window = app.current_terminal_window
        if not window:
            return None

        tab = window.current_tab
        if not tab:
            return None

        session = tab.current_session
        if not session:
            return None

        # Get session metadata
        title = None
        name = None
        try:
            profile = await session.async_get_profile()
            if profile:
                title = profile.get("Title")
                name = profile.get("Name")
        except Exception:
            # Ignore errors getting profile info
            pass

        return SessionInfo(
            session_id=session.session_id,
            window_id=window.window_id,
            tab_id=tab.tab_id,
            is_active=True,
            title=title,
            name=name,
        )

    except Exception:
        return None
