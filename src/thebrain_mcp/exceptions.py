"""
Custom exception hierarchy for TheBrain API and sync operations.
"""


class TheBrainAPIError(Exception):
    """Base exception for TheBrain API and library errors."""

    pass


class TheBrainAuthError(TheBrainAPIError):
    """Authentication failed (invalid or missing API key)."""

    pass


class TheBrainNotFoundError(TheBrainAPIError):
    """Requested resource (brain, thought, link, etc.) not found."""

    pass


class TheBrainRateLimitError(TheBrainAPIError):
    """Rate limit exceeded; retry after backoff."""

    pass


class TheBrainSyncError(TheBrainAPIError):
    """Error during sync (full or incremental)."""

    pass


class TheBrainCacheError(TheBrainAPIError):
    """Error during cache read/write or schema migration."""

    pass
