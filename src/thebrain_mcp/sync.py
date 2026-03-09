"""
Incremental sync engine: full sync (BFS from home thought) and delta sync (modifications API).
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from thebrain_mcp.cache import BrainCache
from thebrain_mcp.client import TheBrainAPIClient
from thebrain_mcp.exceptions import TheBrainSyncError
from thebrain_mcp.metrics import MetricsCollector, SyncMetrics
from thebrain_mcp.models import SyncStateDto

logger = logging.getLogger(__name__)


class BrainSyncEngine:
    """
    Full sync via BFS from homeThoughtId; delta sync via modifications API.
    """

    def __init__(
        self,
        client: TheBrainAPIClient,
        cache: BrainCache,
        metrics: Optional[MetricsCollector] = None,
    ) -> None:
        self._client = client
        self._cache = cache
        self._metrics = metrics or MetricsCollector()

    async def run_full_sync(self, brain_id: str) -> SyncMetrics:
        """
        Perform full sync by BFS from the brain's home thought.
        Fetches thought graph for each discovered thought and upserts into cache.
        """
        started = datetime.utcnow().isoformat() + "Z"
        start_ms = time.monotonic() * 1000
        thoughts_synced = 0
        links_synced = 0
        try:
            brain = await self._client.get_brain(brain_id)
            home_id = brain.get("homeThoughtId")
            if not home_id:
                raise TheBrainSyncError("Brain has no homeThoughtId")

            seen: set[str] = set()
            queue: List[str] = [home_id]

            while queue:
                thought_id = queue.pop(0)
                if thought_id in seen:
                    continue
                seen.add(thought_id)

                graph = await self._client.get_thought_graph(brain_id, thought_id)
                active = graph.get("activeThought") or {}
                if active:
                    await self._cache.upsert_thought(brain_id, active)
                    thoughts_synced += 1

                for key in ("parents", "children", "jumps", "siblings"):
                    for item in graph.get(key) or []:
                        tid = item.get("id") if isinstance(item, dict) else None
                        if tid and tid not in seen:
                            queue.append(tid)
                        if isinstance(item, dict):
                            await self._cache.upsert_thought(brain_id, item)
                            thoughts_synced += 1

                for link in graph.get("links") or []:
                    if isinstance(link, dict) and link.get("id"):
                        await self._cache.upsert_link(brain_id, link)
                        links_synced += 1

            duration_ms = int((time.monotonic() * 1000) - start_ms)
            completed = datetime.utcnow().isoformat() + "Z"
            state = SyncStateDto(
                brain_id=brain_id,
                last_sync_at=completed,
                full_sync_completed=True,
                total_thoughts=thoughts_synced,
                total_links=links_synced,
                last_full_sync_duration_ms=duration_ms,
            )
            await self._cache.set_sync_state(state)

            metrics = SyncMetrics(
                brain_id=brain_id,
                started_at=started,
                completed_at=completed,
                duration_ms=duration_ms,
                full_sync=True,
                thoughts_synced=thoughts_synced,
                links_synced=links_synced,
            )
            self._metrics.record_sync(metrics)
            logger.info("Full sync completed for brain %s: %s thoughts, %s links", brain_id, thoughts_synced, links_synced)
            return metrics
        except Exception as e:
            logger.exception("Full sync failed for brain %s", brain_id)
            completed = datetime.utcnow().isoformat() + "Z"
            duration_ms = int((time.monotonic() * 1000) - start_ms)
            metrics = SyncMetrics(
                brain_id=brain_id,
                started_at=started,
                completed_at=completed,
                duration_ms=duration_ms,
                full_sync=True,
                error=str(e),
            )
            self._metrics.record_sync(metrics)
            raise

    async def run_delta_sync(self, brain_id: str) -> SyncMetrics:
        """
        Fetch modifications since last_sync_at and apply creates/updates/deletes.
        """
        started = datetime.utcnow().isoformat() + "Z"
        start_ms = time.monotonic() * 1000
        modifications_processed = 0
        state = await self._cache.get_sync_state(brain_id)
        start_time = state.last_sync_at if state else None
        if not start_time:
            return await self.run_full_sync(brain_id)

        try:
            logs = await self._client.get_brain_modifications(
                brain_id, max_logs=1000, start_time=start_time
            )
            latest_ts = start_time
            for log in logs:
                modifications_processed += 1
                source_id = log.get("sourceId")
                source_type = log.get("sourceType")
                mod_type = log.get("modType")
                creation_dt = log.get("creationDateTime") or log.get("modificationDateTime")
                if creation_dt:
                    latest_ts = creation_dt

                if mod_type == 102:  # Deleted
                    # Soft delete: set forgotten_datetime on thought
                    if source_type == 2:  # Thought
                        thought = await self._cache.get_thought(brain_id, source_id)
                        if thought:
                            thought["forgottenDateTime"] = latest_ts
                            await self._cache.upsert_thought(brain_id, thought)
                    continue

                if source_type == 2:  # Thought
                    thought = await self._client.get_thought(brain_id, source_id)
                    if thought:
                        await self._cache.upsert_thought(brain_id, thought)
                elif source_type == 3:  # Link
                    link = await self._client.get_link(brain_id, source_id)
                    if link:
                        await self._cache.upsert_link(brain_id, link)

            duration_ms = int((time.monotonic() * 1000) - start_ms)
            completed = datetime.utcnow().isoformat() + "Z"
            new_state = SyncStateDto(
                brain_id=brain_id,
                last_sync_at=latest_ts,
                full_sync_completed=state.full_sync_completed if state else False,
                total_thoughts=state.total_thoughts if state else 0,
                total_links=state.total_links if state else 0,
                last_full_sync_duration_ms=state.last_full_sync_duration_ms if state else None,
            )
            await self._cache.set_sync_state(new_state)

            metrics = SyncMetrics(
                brain_id=brain_id,
                started_at=started,
                completed_at=completed,
                duration_ms=duration_ms,
                full_sync=False,
                modifications_processed=modifications_processed,
            )
            self._metrics.record_sync(metrics)
            logger.info("Delta sync completed for brain %s: %s modifications", brain_id, modifications_processed)
            return metrics
        except Exception as e:
            logger.exception("Delta sync failed for brain %s", brain_id)
            completed = datetime.utcnow().isoformat() + "Z"
            duration_ms = int((time.monotonic() * 1000) - start_ms)
            metrics = SyncMetrics(
                brain_id=brain_id,
                started_at=started,
                completed_at=completed,
                duration_ms=duration_ms,
                full_sync=False,
                error=str(e),
            )
            self._metrics.record_sync(metrics)
            raise
