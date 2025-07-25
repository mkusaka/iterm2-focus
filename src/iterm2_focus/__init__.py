"""iTerm2 Focus - Focus iTerm2 sessions by ID."""

__version__: str = "0.0.11"
__author__: str = "mkusaka"
__email__: str = "hinoshita1992@gmail.com"

__all__: list[str] = [
    "focus_session",
    "FocusError",
    "get_session_info",
    "get_all_sessions",
    "focus_session_by_name",
    "__version__",
]

from .focus import FocusError, focus_session
from .utils import focus_session_by_name, get_all_sessions, get_session_info
