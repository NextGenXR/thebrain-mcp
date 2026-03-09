"""
Cross-platform path utilities for TheBrain local database resolution.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import logging

logger = logging.getLogger(__name__)


def expand_path(path_str: str) -> Optional[Path]:
    """
    Expand a path string with environment variables and user home directory.

    Supports:
    - ~/path or ~\\path -> User home directory
    - $HOME/path or %USERPROFILE%\\path -> Environment variables
    - Relative paths -> Resolved to absolute

    Args:
        path_str: Path string that may contain variables

    Returns:
        Expanded Path object, or None if path_str is empty
    """
    if not path_str or not path_str.strip():
        return None

    path_str = os.path.expanduser(path_str.strip())
    path_str = os.path.expandvars(path_str)
    return Path(path_str).resolve()


def get_default_brain_paths() -> List[Path]:
    """
    Get default TheBrain database search paths for the current platform.
    """
    paths: List[Path] = []
    home = Path.home()
    paths.append(home / "Brains")

    if sys.platform == "win32":
        extra = [
            home / "Documents" / "TheBrain",
            home / "Documents" / "Brains",
            Path(os.environ["APPDATA"]) / "TheBrain" / "Brains"
            if os.environ.get("APPDATA")
            else None,
            Path(os.environ["LOCALAPPDATA"]) / "TheBrain" / "Brains"
            if os.environ.get("LOCALAPPDATA")
            else None,
        ]
        paths.extend(p for p in extra if p is not None)
    elif sys.platform == "darwin":
        paths.extend(
            [
                home / "Library" / "Application Support" / "TheBrain",
                home / "Library" / "Application Support" / "TheBrain" / "Brains",
                home / "Documents" / "TheBrain",
                home / "Documents" / "Brains",
            ]
        )
    else:
        paths.extend(
            [
                home / ".local" / "share" / "thebrain",
                home / ".local" / "share" / "thebrain" / "Brains",
                home / ".thebrain",
                home / ".thebrain" / "Brains",
                home / "Documents" / "TheBrain",
                home / "Documents" / "Brains",
            ]
        )

    return [p for p in paths if p.exists()]


def find_brain_database(
    brain_id: Optional[str] = None,
    custom_path: Optional[str] = None,
) -> Optional[Path]:
    """
    Find a Brain database file.
    """
    search_paths: List[Path] = []

    if custom_path:
        expanded = expand_path(custom_path)
        if expanded and expanded.exists():
            if expanded.is_file() and expanded.name == "Brain.db":
                return expanded
            if expanded.is_dir():
                search_paths.append(expanded)

    search_paths.extend(get_default_brain_paths())

    for base_path in search_paths:
        if not base_path or not base_path.exists():
            continue

        if brain_id and len(brain_id) == 6 and brain_id.startswith("U"):
            user_part = brain_id[:3]
            brain_part = brain_id[3:]
            db_path = base_path / user_part / brain_part / "Brain.db"
            if db_path.exists():
                logger.info("Found brain database at: %s", db_path)
                return db_path

        try:
            for db_file in base_path.glob("**/Brain.db"):
                if len(db_file.relative_to(base_path).parts) <= 3:
                    logger.info("Found brain database at: %s", db_file)
                    return db_file
        except (ValueError, OSError) as e:
            logger.debug("Error searching %s: %s", base_path, e)

    return None


def get_brain_path_from_env() -> Optional[Path]:
    """Get the brain database path from THEBRAIN_LOCAL_DB_PATH env var."""
    env_path = os.getenv("THEBRAIN_LOCAL_DB_PATH")
    if env_path:
        return expand_path(env_path)
    return None


def format_path_for_display(path: Path) -> str:
    """Format a path for display, using ~ for home."""
    path_str = str(path)
    home = str(Path.home())
    if path_str.startswith(home):
        path_str = "~" + path_str[len(home) :].replace("\\", "/")
    if sys.platform == "win32" and os.environ.get("USERPROFILE"):
        userprofile = os.environ["USERPROFILE"]
        if str(path).startswith(userprofile):
            alt = "%USERPROFILE%" + str(path)[len(userprofile) :].replace("/", "\\")
            path_str = f"{path_str} ({alt})"
    return path_str
