"""Integration tests using tmux as a terminal multiplexer proxy."""

import os
import subprocess
import time
from typing import Optional

import pytest

from iterm2_focus import __version__


def is_tmux_available() -> bool:
    """Check if tmux is available."""
    try:
        result = subprocess.run(
            ["which", "tmux"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def create_tmux_session(session_name: str) -> bool:
    """Create a new tmux session."""
    try:
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def list_tmux_sessions() -> list[str]:
    """List all tmux sessions."""
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def kill_tmux_session(session_name: str) -> None:
    """Kill a tmux session."""
    try:
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            check=True
        )
    except subprocess.CalledProcessError:
        pass


@pytest.fixture
def tmux_test_session():
    """Create a test tmux session and clean up after."""
    session_name = f"iterm2_focus_test_{int(time.time())}"
    
    # Kill any existing test sessions
    for session in list_tmux_sessions():
        if session.startswith("iterm2_focus_test_"):
            kill_tmux_session(session)
    
    # Create new session
    if create_tmux_session(session_name):
        yield session_name
        # Cleanup
        kill_tmux_session(session_name)
    else:
        pytest.skip("Failed to create tmux session")


@pytest.mark.skipif(not is_tmux_available(), reason="tmux not available")
@pytest.mark.tmux
def test_tmux_session_simulation(tmux_test_session):
    """Test basic tmux session operations as a proxy for iTerm2."""
    # Verify session was created
    sessions = list_tmux_sessions()
    assert tmux_test_session in sessions
    
    # Run a command in the session
    subprocess.run([
        "tmux", "send-keys", "-t", tmux_test_session,
        "echo 'Testing iterm2-focus'", "Enter"
    ], check=True)
    
    # Capture pane content
    result = subprocess.run([
        "tmux", "capture-pane", "-t", tmux_test_session, "-p"
    ], capture_output=True, text=True, check=True)
    
    assert "Testing iterm2-focus" in result.stdout


@pytest.mark.skipif(not is_tmux_available(), reason="tmux not available")
@pytest.mark.tmux
def test_multiple_tmux_sessions():
    """Test handling multiple sessions."""
    session_names = []
    
    try:
        # Create multiple sessions
        for i in range(3):
            name = f"iterm2_test_multi_{i}_{int(time.time())}"
            if create_tmux_session(name):
                session_names.append(name)
        
        # Verify all sessions exist
        existing_sessions = list_tmux_sessions()
        for name in session_names:
            assert name in existing_sessions
        
    finally:
        # Cleanup
        for name in session_names:
            kill_tmux_session(name)


@pytest.mark.skipif(not is_tmux_available(), reason="tmux not available")
@pytest.mark.tmux
def test_tmux_window_switching():
    """Test switching between tmux windows."""
    session_name = f"iterm2_window_test_{int(time.time())}"
    
    try:
        # Create session with multiple windows
        subprocess.run([
            "tmux", "new-session", "-d", "-s", session_name, "-n", "window1"
        ], check=True)
        
        subprocess.run([
            "tmux", "new-window", "-t", session_name, "-n", "window2"
        ], check=True)
        
        # List windows
        result = subprocess.run([
            "tmux", "list-windows", "-t", session_name, "-F", "#{window_name}"
        ], capture_output=True, text=True, check=True)
        
        windows = result.stdout.strip().split('\n')
        assert "window1" in windows
        assert "window2" in windows
        
        # Switch to window2
        subprocess.run([
            "tmux", "select-window", "-t", f"{session_name}:window2"
        ], check=True)
        
    finally:
        kill_tmux_session(session_name)


@pytest.mark.skipif(not is_tmux_available(), reason="tmux not available")
@pytest.mark.tmux 
def test_tmux_pane_operations():
    """Test tmux pane operations as proxy for iTerm2 tabs."""
    session_name = f"iterm2_pane_test_{int(time.time())}"
    
    try:
        # Create session
        subprocess.run([
            "tmux", "new-session", "-d", "-s", session_name
        ], check=True)
        
        # Split pane horizontally
        subprocess.run([
            "tmux", "split-window", "-h", "-t", session_name
        ], check=True)
        
        # List panes
        result = subprocess.run([
            "tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"
        ], capture_output=True, text=True, check=True)
        
        panes = result.stdout.strip().split('\n')
        assert len(panes) == 2
        
    finally:
        kill_tmux_session(session_name)