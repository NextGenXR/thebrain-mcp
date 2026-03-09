"""
TheBrain MCP - Python client library for TheBrain API.

Provides API client, local cache with incremental sync, graph analysis,
and metrics for integration with Spock and other MCP consumers.
"""

__version__ = "0.2.0"

from thebrain_mcp.cache import BrainCache
from thebrain_mcp.client import TheBrainAPIClient
from thebrain_mcp.exceptions import (
    TheBrainAPIError,
    TheBrainAuthError,
    TheBrainCacheError,
    TheBrainNotFoundError,
    TheBrainRateLimitError,
    TheBrainSyncError,
)
from thebrain_mcp.graph import BrainGraphAnalyzer
from thebrain_mcp.metrics import MetricsCollector, SyncMetrics
from thebrain_mcp.models import (
    EntityType,
    LinkDto,
    ModificationLogDto,
    SyncStateDto,
    ThoughtDto,
    ThoughtKind,
)
from thebrain_mcp.sync import BrainSyncEngine

__all__ = [
    "__version__",
    "BrainCache",
    "BrainGraphAnalyzer",
    "BrainSyncEngine",
    "MetricsCollector",
    "SyncMetrics",
    "SyncStateDto",
    "TheBrainAPIClient",
    "TheBrainAPIError",
    "TheBrainAuthError",
    "TheBrainCacheError",
    "TheBrainNotFoundError",
    "TheBrainRateLimitError",
    "TheBrainSyncError",
    "ThoughtDto",
    "LinkDto",
    "ThoughtKind",
    "EntityType",
    "ModificationLogDto",
]
