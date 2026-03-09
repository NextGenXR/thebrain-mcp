"""
Metrics collection for sync, cache, and API operations.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SyncMetrics:
    """Metrics for a single sync run."""

    brain_id: str
    started_at: str
    completed_at: str
    duration_ms: int
    full_sync: bool
    thoughts_synced: int = 0
    links_synced: int = 0
    notes_synced: int = 0
    modifications_processed: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MetricsCollector:
    """
    Collects and optionally persists metrics for sync, cache hits, and API latency.
    """

    def __init__(self, persist_path: str | None = None) -> None:
        self._persist_path = persist_path
        self._sync_history: list[SyncMetrics] = []
        self._cache_hits = 0
        self._cache_misses = 0
        self._api_call_count = 0
        self._api_latency_ms: list[float] = []

    def record_sync(self, metrics: SyncMetrics) -> None:
        """Record a sync run."""
        self._sync_history.append(metrics)
        if len(self._sync_history) > 100:
            self._sync_history = self._sync_history[-100:]
        logger.info(
            "sync_completed",
            extra={"brain_id": metrics.brain_id, "duration_ms": metrics.duration_ms},
        )
        if self._persist_path:
            self._append_metric("sync", metrics.to_dict())

    def record_cache_hit(self) -> None:
        self._cache_hits += 1

    def record_cache_miss(self) -> None:
        self._cache_misses += 1

    def record_api_call(self, latency_ms: float) -> None:
        self._api_call_count += 1
        self._api_latency_ms.append(latency_ms)
        if len(self._api_latency_ms) > 200:
            self._api_latency_ms = self._api_latency_ms[-200:]

    @property
    def cache_hit_rate(self) -> float:
        total = self._cache_hits + self._cache_misses
        if total == 0:
            return 0.0
        return self._cache_hits / total

    @property
    def average_api_latency_ms(self) -> float:
        if not self._api_latency_ms:
            return 0.0
        return sum(self._api_latency_ms) / len(self._api_latency_ms)

    def get_summary(self) -> dict[str, Any]:
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(self.cache_hit_rate, 4),
            "api_call_count": self._api_call_count,
            "average_api_latency_ms": round(self.average_api_latency_ms, 2),
            "sync_runs_recorded": len(self._sync_history),
        }

    def _append_metric(self, metric_name: str, value: dict[str, Any]) -> None:
        if not self._persist_path:
            return
        try:
            line = json.dumps({"metric_name": metric_name, **value}) + "\n"
            with open(self._persist_path, "a") as f:
                f.write(line)
        except OSError as e:
            logger.warning("Could not persist metric: %s", e)
