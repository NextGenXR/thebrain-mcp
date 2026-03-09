"""
Request throttling for TheBrain API (self-imposed rate limit).
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RequestThrottle:
    """
    Semaphore-based throttling to limit concurrent requests.
    Optionally enforces a minimum delay between requests.
    """

    def __init__(
        self,
        max_concurrent: int = 3,
        min_interval_seconds: Optional[float] = 0.25,
    ) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._min_interval = min_interval_seconds
        self._last_request_time: Optional[float] = 0.0

    async def acquire(self) -> None:
        """Wait until a request slot is available and interval has elapsed."""
        await self._semaphore.acquire()
        if self._min_interval and self._last_request_time is not None:
            import time

            elapsed = time.monotonic() - self._last_request_time
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_request_time = time.monotonic()

    def release(self) -> None:
        """Release the request slot."""
        self._semaphore.release()

    async def __aenter__(self) -> "RequestThrottle":
        await self.acquire()
        return self

    async def __aexit__(self, *args: object) -> None:
        self.release()
