#!/usr/bin/env python3
"""Version bump script for iterm2-focus."""

import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple

VALID_BUMP_TYPES = ["patch", "minor", "major"]


def get_current_version(pyproject_path: Path) -> str:
    """Get current version from pyproject.toml."""
    content = pyproject_path.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into tuple of integers."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(version: str, bump_type: str) -> str:
    """Bump version based on type."""
    major, minor, patch = parse_version(version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_pyproject_toml(pyproject_path: Path, new_version: str) -> None:
    """Update version in pyproject.toml."""
    content = pyproject_path.read_text()
    updated_content = re.sub(
        r'^version = "[^"]+"',
        f'version = "{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE
    )
    pyproject_path.write_text(updated_content)


def update_init_py(init_path: Path, new_version: str) -> None:
    """Update version in __init__.py."""
    content = init_path.read_text()
    updated_content = re.sub(
        r'^__version__: str = "[^"]+"',
        f'__version__: str = "{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE
    )
    init_path.write_text(updated_content)


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def main():
    """Main function."""
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_BUMP_TYPES:
        print(f"Usage: {sys.argv[0]} <{'/'.join(VALID_BUMP_TYPES)}>")
        sys.exit(1)
    
    bump_type = sys.argv[1]
    
    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    pyproject_path = project_root / "pyproject.toml"
    init_path = project_root / "src" / "iterm2_focus" / "__init__.py"
    
    # Check if files exist
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found")
        sys.exit(1)
    
    if not init_path.exists():
        print(f"Error: {init_path} not found")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version(pyproject_path)
    print(f"Current version: {current_version}")
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")
    
    # Update version in files
    print("Updating pyproject.toml...")
    update_pyproject_toml(pyproject_path, new_version)
    
    print("Updating __init__.py...")
    update_init_py(init_path, new_version)
    
    # Run uv sync to update uv.lock
    print("Running uv sync to update uv.lock...")
    result = run_command(["uv", "sync", "--all-extras", "--dev"], check=False)
    if result.returncode != 0:
        print(f"Error running uv sync: {result.stderr}")
        sys.exit(1)
    
    # Git add changes
    print("Adding changes to git...")
    run_command(["git", "add", "pyproject.toml", str(init_path), "uv.lock"])
    
    # Git commit
    commit_message = f"chore: bump version to {new_version}"
    print(f"Committing changes: {commit_message}")
    run_command(["git", "commit", "-m", commit_message])
    
    # Git tag
    tag_name = f"v{new_version}"
    print(f"Creating tag: {tag_name}")
    run_command(["git", "tag", tag_name])
    
    print(f"\nVersion bumped successfully from {current_version} to {new_version}")
    print(f"Tag {tag_name} created")
    print("\nTo push changes:")
    print("  git push")
    print(f"  git push origin {tag_name}")


if __name__ == "__main__":
    main()