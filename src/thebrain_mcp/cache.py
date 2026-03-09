"""
SQLite cache for TheBrain data with sync_state and FTS5 search.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

from thebrain_mcp.exceptions import TheBrainCacheError
from thebrain_mcp.models import SyncStateDto

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sync_state (
    brain_id TEXT PRIMARY KEY,
    last_sync_at TEXT NOT NULL,
    full_sync_completed INTEGER DEFAULT 0,
    total_thoughts INTEGER DEFAULT 0,
    total_links INTEGER DEFAULT 0,
    last_full_sync_duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS thoughts (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    name TEXT NOT NULL,
    label TEXT,
    kind INTEGER NOT NULL DEFAULT 1,
    type_id TEXT,
    ac_type INTEGER DEFAULT 0,
    foreground_color TEXT,
    background_color TEXT,
    creation_datetime TEXT,
    modification_datetime TEXT,
    forgotten_datetime TEXT,
    raw_json TEXT
);

CREATE TABLE IF NOT EXISTS links (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    thought_id_a TEXT NOT NULL,
    thought_id_b TEXT NOT NULL,
    relation INTEGER NOT NULL,
    direction INTEGER,
    meaning INTEGER DEFAULT 1,
    name TEXT,
    color TEXT,
    thickness INTEGER,
    modification_datetime TEXT,
    raw_json TEXT
);

CREATE TABLE IF NOT EXISTS notes (
    thought_id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    markdown TEXT,
    modification_datetime TEXT
);

CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_type INTEGER,
    name TEXT,
    type INTEGER,
    location TEXT,
    data_length INTEGER,
    modification_datetime TEXT,
    raw_json TEXT
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_thoughts_brain ON thoughts(brain_id);
CREATE INDEX IF NOT EXISTS idx_thoughts_kind ON thoughts(kind);
CREATE INDEX IF NOT EXISTS idx_links_a ON links(thought_id_a);
CREATE INDEX IF NOT EXISTS idx_links_b ON links(thought_id_b);
CREATE INDEX IF NOT EXISTS idx_links_relation ON links(relation);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name, timestamp);
"""


class BrainCache:
    """
    Async SQLite cache for synced TheBrain data with sync_state tracking.
    """

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._conn: Optional[aiosqlite.Connection] = None

    async def open(self) -> None:
        """Create or open the database and ensure schema."""
        self._conn = await aiosqlite.connect(str(self._path))
        self._conn.row_factory = aiosqlite.Row
        for statement in SCHEMA_SQL.strip().split(";"):
            statement = statement.strip()
            if statement:
                await self._conn.execute(statement)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self) -> "BrainCache":
        await self.open()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def get_sync_state(self, brain_id: str) -> Optional[SyncStateDto]:
        """Return sync state for a brain, or None if never synced."""
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        cursor = await self._conn.execute(
            "SELECT brain_id, last_sync_at, full_sync_completed, total_thoughts, total_links, last_full_sync_duration_ms FROM sync_state WHERE brain_id = ?",
            (brain_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if not row:
            return None
        return SyncStateDto(
            brain_id=row["brain_id"],
            last_sync_at=row["last_sync_at"],
            full_sync_completed=bool(row["full_sync_completed"]),
            total_thoughts=row["total_thoughts"] or 0,
            total_links=row["total_links"] or 0,
            last_full_sync_duration_ms=row["last_full_sync_duration_ms"],
        )

    async def set_sync_state(self, state: SyncStateDto) -> None:
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO sync_state
            (brain_id, last_sync_at, full_sync_completed, total_thoughts, total_links, last_full_sync_duration_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                state.brain_id,
                state.last_sync_at,
                1 if state.full_sync_completed else 0,
                state.total_thoughts,
                state.total_links,
                state.last_full_sync_duration_ms,
            ),
        )
        await self._conn.commit()

    async def upsert_thought(self, brain_id: str, thought: Dict[str, Any]) -> None:
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        raw = json.dumps(thought) if thought else None
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO thoughts
            (id, brain_id, name, label, kind, type_id, ac_type, foreground_color, background_color,
             creation_datetime, modification_datetime, forgotten_datetime, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                thought.get("id"),
                brain_id,
                thought.get("name", ""),
                thought.get("label"),
                thought.get("kind", 1),
                thought.get("typeId"),
                thought.get("acType", 0),
                thought.get("foregroundColor"),
                thought.get("backgroundColor"),
                thought.get("creationDateTime"),
                thought.get("modificationDateTime"),
                thought.get("forgottenDateTime"),
                raw,
            ),
        )
        await self._conn.commit()

    async def upsert_link(self, brain_id: str, link: Dict[str, Any]) -> None:
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        raw = json.dumps(link) if link else None
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO links
            (id, brain_id, thought_id_a, thought_id_b, relation, direction, meaning, name, color, thickness, modification_datetime, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                link.get("id"),
                brain_id,
                link.get("thoughtIdA"),
                link.get("thoughtIdB"),
                link.get("relation", 1),
                link.get("direction", 0),
                link.get("meaning", 1),
                link.get("name"),
                link.get("color"),
                link.get("thickness"),
                link.get("modificationDateTime"),
                raw,
            ),
        )
        await self._conn.commit()

    async def get_thought(self, brain_id: str, thought_id: str) -> Optional[Dict[str, Any]]:
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        cursor = await self._conn.execute(
            "SELECT raw_json FROM thoughts WHERE brain_id = ? AND id = ?",
            (brain_id, thought_id),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if not row or not row["raw_json"]:
            return None
        return json.loads(row["raw_json"])

    async def search_thoughts_by_name(
        self, brain_id: str, query: str, max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Simple LIKE search on thought names (FTS5 can be added later)."""
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        pattern = f"%{query}%"
        cursor = await self._conn.execute(
            "SELECT raw_json FROM thoughts WHERE brain_id = ? AND name LIKE ? LIMIT ?",
            (brain_id, pattern, max_results),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [json.loads(r["raw_json"]) for r in rows if r["raw_json"]]

    async def get_all_thoughts(self, brain_id: str) -> List[Dict[str, Any]]:
        """Return all thoughts for a brain (raw_json)."""
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        cursor = await self._conn.execute(
            "SELECT raw_json FROM thoughts WHERE brain_id = ?",
            (brain_id,),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [json.loads(r["raw_json"]) for r in rows if r["raw_json"]]

    async def get_all_links(self, brain_id: str) -> List[Dict[str, Any]]:
        """Return all links for a brain (raw_json)."""
        if not self._conn:
            raise TheBrainCacheError("Cache not open")
        cursor = await self._conn.execute(
            "SELECT raw_json FROM links WHERE brain_id = ?",
            (brain_id,),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [json.loads(r["raw_json"]) for r in rows if r["raw_json"]]
