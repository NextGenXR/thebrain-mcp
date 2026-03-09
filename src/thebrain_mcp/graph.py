"""
Graph analysis for TheBrain data using NetworkX.

Works with either TheBrain's local Brain.db (Thoughts/Links) or
thebrain_mcp cache (thoughts/links).
"""

import json
import logging
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from thebrain_mcp.path_utils import expand_path, format_path_for_display

logger = logging.getLogger(__name__)


def _ticks_to_datetime(ticks: Optional[int]) -> Optional[str]:
    """Convert .NET ticks to ISO string if needed (for TheBrain local DB)."""
    if ticks is None:
        return None
    try:
        # .NET ticks are 100-nanosecond intervals since 1 Jan 0001
        from datetime import datetime, timedelta

        epoch = datetime(1, 1, 1)
        delta = timedelta(microseconds=ticks // 10)
        return (epoch + delta).isoformat()
    except Exception:
        return str(ticks)


class BrainGraphAnalyzer:
    """
    Analyze TheBrain database as a NetworkX directed graph.
    Supports both TheBrain local Brain.db and thebrain_mcp cache schema.
    """

    def __init__(self, db_path: str) -> None:
        expanded = expand_path(db_path) if db_path else None
        if not expanded or not expanded.exists():
            raise FileNotFoundError(
                f"Brain database not found at {format_path_for_display(Path(db_path or ''))}"
            )
        self.db_path = str(expanded)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.graph: Optional[nx.DiGraph] = None
        self.thought_data: Dict[str, Dict] = {}
        self.link_data: Dict[str, Dict] = {}
        self._thought_table: Optional[str] = None
        self._link_table: Optional[str] = None

    def _discover_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        for t in tables:
            if t.lower() == "thoughts":
                self._thought_table = t
            elif t.lower() == "links":
                self._link_table = t
        if not self._thought_table or not self._link_table:
            raise ValueError("Database must have 'thoughts' and 'links' tables")

    def load_graph(self, brain_id: Optional[str] = None) -> nx.DiGraph:
        """Load the brain into a NetworkX DiGraph."""
        if not self._thought_table or not self._link_table:
            self._discover_tables()
        assert self._thought_table and self._link_table

        self.graph = nx.DiGraph()
        cursor = self.conn.cursor()

        query = f"SELECT * FROM {self._thought_table}"
        params: List[Any] = []
        if brain_id:
            cursor.execute(
                f"SELECT 1 FROM {self._thought_table} WHERE brain_id = ? LIMIT 1",
                (brain_id,),
            )
            if cursor.fetchone():
                query += " WHERE brain_id = ?"
                params.append(brain_id)
        cursor.execute(query, params)

        for row in cursor.fetchall():
            thought = dict(row)
            tid = thought.get("id") or thought.get("Id")
            if not tid:
                continue
            self.thought_data[tid] = thought
            name = thought.get("name") or thought.get("Name", "")
            self.graph.add_node(
                tid,
                name=name,
                label=thought.get("label") or thought.get("Label"),
                kind=thought.get("kind", thought.get("Kind", 1)),
                type_id=thought.get("type_id") or thought.get("TypeId"),
            )

        cursor.execute(f"SELECT * FROM {self._link_table}")
        for row in cursor.fetchall():
            link = dict(row)
            lid = link.get("id") or link.get("Id")
            src = link.get("thought_id_a") or link.get("ThoughtIdA")
            tgt = link.get("thought_id_b") or link.get("ThoughtIdB")
            if not lid or not src or not tgt:
                continue
            if src not in self.graph or tgt not in self.graph:
                continue
            self.link_data[lid] = link
            self.graph.add_edge(
                src,
                tgt,
                link_id=lid,
                relation=link.get("relation", link.get("Relation", 1)),
            )

        logger.info(
            "Loaded graph: %s nodes, %s edges",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )
        return self.graph

    def get_statistics(self) -> Dict[str, Any]:
        """Basic graph statistics."""
        if not self.graph:
            self.load_graph()
        assert self.graph is not None
        n = self.graph.number_of_nodes()
        return {
            "total_thoughts": n,
            "total_links": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph),
            "orphaned_count": len(list(nx.isolates(self.graph))),
        }

    def find_shortest_path(
        self, source_name: str, target_name: str
    ) -> Optional[List[str]]:
        """Find shortest path between two thoughts by name."""
        if not self.graph:
            self.load_graph()
        assert self.graph is not None
        source_id = None
        target_id = None
        for tid, data in self.thought_data.items():
            name = data.get("name") or data.get("Name", "")
            if name == source_name:
                source_id = tid
            if name == target_name:
                target_id = tid
        if not source_id or not target_id:
            return None
        try:
            path_ids = nx.shortest_path(self.graph, source_id, target_id)
            return [
                (self.thought_data[tid].get("name") or self.thought_data[tid].get("Name", ""))
                for tid in path_ids
            ]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
