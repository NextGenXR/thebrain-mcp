"""
TheBrain MCP Server - Source Package
"""

from .api_client import TheBrainAPI
from .tool_schemas import get_tool_schemas
from . import handlers

__version__ = "1.0.0"

__all__ = [
    "TheBrainAPI",
    "get_tool_schemas",
    "handlers",
]
