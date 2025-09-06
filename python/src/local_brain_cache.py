"""
Local brain cache implementation using TheBrain's local database files.

This module provides direct access to TheBrain's local SQLite database files,
enabling instant search and retrieval without API calls.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

class LocalBrainCache:
    """
    Access TheBrain's local SQLite database for ultra-fast thought retrieval.
    
    TheBrain stores data locally in:
    - C:/Users/{username}/Brains/U{XX}/B{XX}/Brain.db - SQLite database
    - C:/Users/{username}/Brains/U{XX}/B{XX}/{thought-uuid}/Notes.md - Note content
    """
    
    def __init__(self, brain_path: str):
        """
        Initialize the local brain cache.
        
        Args:
            brain_path: Path to the brain folder (e.g., ~/Brains/U01/B02)
        """
        self.brain_path = Path(brain_path)
        self.db_path = self.brain_path / "Brain.db"
        self.thoughts_cache = {}
        self.index_built = False
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Brain database not found at {self.db_path}")
        
        # Connect to the database
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Discover the schema
        self._discover_schema()
    
    def _discover_schema(self):
        """Discover the database schema."""
        cursor = self.conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        self.tables = [row[0] for row in cursor.fetchall()]
        
        # Common TheBrain table names to look for
        expected_tables = [
            'Thought', 'Thoughts', 'thoughts',
            'Link', 'Links', 'links',
            'Attachment', 'Attachments', 'attachments',
            'Note', 'Notes', 'notes'
        ]
        
        self.thought_table = None
        self.link_table = None
        
        for table in self.tables:
            if 'thought' in table.lower():
                self.thought_table = table
            elif 'link' in table.lower():
                self.link_table = table
        
        print(f"[LocalCache] Found tables: {self.tables}")
        print(f"[LocalCache] Thought table: {self.thought_table}")
        print(f"[LocalCache] Link table: {self.link_table}")
        
        # Get schema for thought table
        if self.thought_table:
            cursor.execute(f"PRAGMA table_info({self.thought_table})")
            self.thought_columns = [row[1] for row in cursor.fetchall()]
            print(f"[LocalCache] Thought columns: {self.thought_columns}")
    
    def build_index(self):
        """Build an in-memory index of all thoughts for fast searching."""
        if not self.thought_table:
            print("[LocalCache] No thought table found, cannot build index")
            return False
        
        cursor = self.conn.cursor()
        
        # Try to get all thoughts with common column names
        query = f"SELECT * FROM {self.thought_table}"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        print(f"[LocalCache] Indexing {len(rows)} thoughts...")
        
        for row in rows:
            # Convert row to dict
            thought = dict(row)
            
            # Try to find ID and name columns
            thought_id = None
            thought_name = None
            
            for col in self.thought_columns:
                col_lower = col.lower()
                if 'id' in col_lower and not thought_id:
                    thought_id = thought[col]
                elif 'name' in col_lower and not thought_name:
                    thought_name = thought[col]
            
            if thought_id:
                # Store in cache with normalized name for searching
                self.thoughts_cache[thought_id] = thought
                if thought_name:
                    # Also index by lowercase name
                    name_key = thought_name.lower() if thought_name else ""
                    if name_key:
                        if name_key not in self.thoughts_cache:
                            self.thoughts_cache[name_key] = []
                        self.thoughts_cache[name_key].append(thought)
        
        self.index_built = True
        print(f"[LocalCache] Index built with {len(self.thoughts_cache)} entries")
        return True
    
    def search_thoughts(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Search for thoughts by name using the local cache.
        
        This is INSTANT - no API calls needed!
        """
        if not self.index_built:
            self.build_index()
        
        query_lower = query.lower()
        results = []
        
        # Exact match first
        if query_lower in self.thoughts_cache:
            match = self.thoughts_cache[query_lower]
            if isinstance(match, list):
                results.extend(match[:max_results])
            else:
                results.append(match)
        
        # Partial matches
        if len(results) < max_results:
            for key, value in self.thoughts_cache.items():
                if isinstance(key, str) and query_lower in key:
                    if isinstance(value, list):
                        for v in value:
                            if v not in results:
                                results.append(v)
                                if len(results) >= max_results:
                                    break
                    elif value not in results:
                        results.append(value)
                    
                    if len(results) >= max_results:
                        break
        
        return results[:max_results]
    
    def get_thought_by_id(self, thought_id: str) -> Optional[Dict]:
        """Get a thought by its UUID."""
        if not self.index_built:
            self.build_index()
        
        return self.thoughts_cache.get(thought_id)
    
    def get_thought_note(self, thought_id: str) -> Optional[str]:
        """
        Get the note content for a thought.
        
        Notes are stored as markdown files in the thought's folder.
        """
        note_path = self.brain_path / thought_id / "Notes.md"
        if note_path.exists():
            with open(note_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def get_all_thoughts(self) -> List[Dict]:
        """Get all thoughts from the database."""
        if not self.index_built:
            self.build_index()
        
        # Filter out string keys (name indexes) and return only thought dicts
        thoughts = []
        for key, value in self.thoughts_cache.items():
            if not isinstance(key, str) or '-' in key:  # UUIDs have dashes
                if isinstance(value, dict):
                    thoughts.append(value)
        
        return thoughts
    
    def get_links(self, thought_id: str) -> List[Dict]:
        """Get all links for a thought."""
        if not self.link_table:
            return []
        
        cursor = self.conn.cursor()
        
        # Try common column names for links
        query = f"""
        SELECT * FROM {self.link_table}
        WHERE thoughtIdA = ? OR thoughtIdB = ?
           OR source_id = ? OR target_id = ?
           OR from_thought = ? OR to_thought = ?
        """
        
        try:
            cursor.execute(query, (thought_id,) * 6)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Column names might be different
            return []
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


class HybridBrainCache:
    """
    Hybrid cache that uses local database when available, falls back to API.
    """
    
    def __init__(self, api_client, local_brain_path: Optional[str] = None):
        """
        Initialize hybrid cache.
        
        Args:
            api_client: TheBrain API client
            local_brain_path: Optional path to local brain database
        """
        self.api = api_client
        self.local_cache = None
        
        if local_brain_path and os.path.exists(local_brain_path):
            try:
                self.local_cache = LocalBrainCache(local_brain_path)
                self.local_cache.build_index()
                print(f"[HybridCache] Local cache initialized with {len(self.local_cache.thoughts_cache)} thoughts")
            except Exception as e:
                print(f"[HybridCache] Failed to initialize local cache: {e}")
                self.local_cache = None
    
    async def search_thoughts(self, brain_id: str, query: str, max_results: int = 30) -> List[Dict]:
        """
        Search thoughts using local cache first, then API.
        """
        results = []
        
        # Try local cache first (INSTANT!)
        if self.local_cache:
            local_results = self.local_cache.search_thoughts(query, max_results)
            if local_results:
                print(f"[HybridCache] Found {len(local_results)} results in local cache")
                
                # Convert local format to API format
                for r in local_results:
                    # Map local columns to API format
                    results.append({
                        "id": r.get("id") or r.get("Id") or r.get("thoughtId"),
                        "name": r.get("name") or r.get("Name") or r.get("title"),
                        "brainId": brain_id,
                        "source": "local_cache"
                    })
                
                return results
        
        # Fall back to API if no local results
        print(f"[HybridCache] Falling back to API search")
        api_results = await self.api.search_thoughts(brain_id, query, max_results, False)
        
        for r in api_results:
            r["source"] = "api"
            results.append(r)
        
        return results
    
    async def get_thought(self, brain_id: str, thought_id: str) -> Optional[Dict]:
        """
        Get thought details using local cache first, then API.
        """
        # Try local cache first
        if self.local_cache:
            local_thought = self.local_cache.get_thought_by_id(thought_id)
            if local_thought:
                # Also get the note content
                note = self.local_cache.get_thought_note(thought_id)
                
                result = {
                    "id": thought_id,
                    "brainId": brain_id,
                    "name": local_thought.get("name") or local_thought.get("Name"),
                    "note": note,
                    "source": "local_cache",
                    **local_thought
                }
                
                print(f"[HybridCache] Found thought in local cache: {result.get('name')}")
                return result
        
        # Fall back to API
        print(f"[HybridCache] Falling back to API for thought {thought_id}")
        return await self.api.get_thought(brain_id, thought_id)


# Example usage
if __name__ == "__main__":
    # Test with your local brain
    brain_path = os.path.expanduser("~/Brains/U01/B02")
    
    cache = LocalBrainCache(brain_path)
    cache.build_index()
    
    # Instant search!
    results = cache.search_thoughts("Project Lead")
    print(f"Found {len(results)} results for 'Project Lead'")
    
    if results:
        thought = results[0]
        thought_id = thought.get("id") or thought.get("Id")
        print(f"Thought ID: {thought_id}")
        
        # Get note content
        note = cache.get_thought_note(thought_id)
        if note:
            print(f"Note preview: {note[:200]}...")
    
    cache.close()
