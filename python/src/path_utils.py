"""
Cross-platform path utilities for TheBrain MCP Server.

Handles path resolution with environment variables and platform-specific defaults.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def expand_path(path_str: str) -> Path:
    """
    Expand a path string with environment variables and user home directory.
    
    Supports:
    - ~/path or ~\\path -> User home directory
    - $HOME/path or %USERPROFILE%\\path -> Environment variables
    - Relative paths -> Resolved to absolute
    
    Args:
        path_str: Path string that may contain variables
        
    Returns:
        Expanded Path object
    """
    if not path_str:
        return None
    
    # First expand user home directory (~)
    path_str = os.path.expanduser(path_str)
    
    # Then expand environment variables
    path_str = os.path.expandvars(path_str)
    
    # Convert to Path and resolve
    return Path(path_str).resolve()


def get_default_brain_paths() -> List[Path]:
    """
    Get default TheBrain database search paths for the current platform.
    
    Returns:
        List of Path objects to search for Brain databases
    """
    paths = []
    home = Path.home()
    
    # Primary location used by TheBrain (cross-platform)
    paths.append(home / "Brains")
    
    if sys.platform == "win32":
        # Windows-specific paths
        paths.extend([
            home / "Documents" / "TheBrain",
            home / "Documents" / "Brains",
            Path(os.environ.get("APPDATA", "")) / "TheBrain" / "Brains" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("LOCALAPPDATA", "")) / "TheBrain" / "Brains" if os.environ.get("LOCALAPPDATA") else None,
        ])
    elif sys.platform == "darwin":
        # macOS-specific paths
        paths.extend([
            home / "Library" / "Application Support" / "TheBrain",
            home / "Library" / "Application Support" / "TheBrain" / "Brains",
            home / "Documents" / "TheBrain",
            home / "Documents" / "Brains",
        ])
    else:
        # Linux/Unix paths
        paths.extend([
            home / ".local" / "share" / "thebrain",
            home / ".local" / "share" / "thebrain" / "Brains",
            home / ".thebrain",
            home / ".thebrain" / "Brains",
            home / "Documents" / "TheBrain",
            home / "Documents" / "Brains",
        ])
    
    # Filter out None values and non-existent paths
    return [p for p in paths if p and p.exists()]


def find_brain_database(brain_id: Optional[str] = None, custom_path: Optional[str] = None) -> Optional[Path]:
    """
    Find a Brain database file.
    
    Args:
        brain_id: Optional brain ID (e.g., "U01B02")
        custom_path: Optional custom path from environment variable
        
    Returns:
        Path to Brain.db if found, None otherwise
    """
    search_paths = []
    
    # If custom path provided, check it first
    if custom_path:
        custom = expand_path(custom_path)
        if custom and custom.exists():
            if custom.is_file() and custom.name == "Brain.db":
                return custom
            elif custom.is_dir():
                search_paths.append(custom)
    
    # Add default paths
    search_paths.extend(get_default_brain_paths())
    
    # Search for Brain.db files
    for base_path in search_paths:
        if not base_path or not base_path.exists():
            continue
            
        # If brain_id provided, look for specific structure (U01/B02)
        if brain_id:
            # Handle different ID formats
            if len(brain_id) == 6 and brain_id.startswith("U"):
                # Format: U01B02
                user_part = brain_id[:3]
                brain_part = brain_id[3:]
                db_path = base_path / user_part / brain_part / "Brain.db"
                if db_path.exists():
                    logger.info(f"Found brain database at: {db_path}")
                    return db_path
                    
        # Search recursively for any Brain.db files (up to 3 levels deep)
        try:
            for db_file in base_path.glob("**/Brain.db"):
                # Limit search depth to avoid long searches
                if len(db_file.relative_to(base_path).parts) <= 3:
                    logger.info(f"Found brain database at: {db_file}")
                    return db_file
        except Exception as e:
            logger.debug(f"Error searching {base_path}: {e}")
            
    return None


def get_brain_path_from_env() -> Optional[Path]:
    """
    Get the brain database path from environment variable.
    
    Returns:
        Expanded path from THEBRAIN_LOCAL_DB_PATH env var, or None
    """
    env_path = os.getenv("THEBRAIN_LOCAL_DB_PATH")
    if env_path:
        return expand_path(env_path)
    return None


def format_path_for_display(path: Path) -> str:
    """
    Format a path for display, using environment variables where appropriate.
    
    Args:
        path: Path to format
        
    Returns:
        Human-readable path string
    """
    path_str = str(path)
    home = str(Path.home())
    
    # Replace home directory with ~
    if path_str.startswith(home):
        path_str = "~" + path_str[len(home):].replace("\\", "/")
        
    # On Windows, also show %USERPROFILE% format
    if sys.platform == "win32" and os.environ.get("USERPROFILE"):
        userprofile = os.environ["USERPROFILE"]
        if str(path).startswith(userprofile):
            alt_format = "%USERPROFILE%" + str(path)[len(userprofile):].replace("/", "\\")
            path_str = f"{path_str} ({alt_format})"
            
    return path_str
