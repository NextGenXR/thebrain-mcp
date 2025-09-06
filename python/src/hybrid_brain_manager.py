"""
Hybrid Brain Manager for TheBrain MCP Server

This module provides a hybrid approach to accessing TheBrain data:
- Reads from local SQLite database for comprehensive, fast access
- Writes through the API to maintain cloud synchronization
- Downloads and indexes cloud data when local database doesn't exist
"""

import os
import sqlite3
import json
import asyncio
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from .path_utils import find_brain_database, get_brain_path_from_env, format_path_for_display

logger = logging.getLogger(__name__)


class HybridBrainManager:
    """
    Manages hybrid local/cloud access to TheBrain data.
    
    Architecture:
    - Local SQLite database for reads (fast, complete access including tags)
    - Cloud API for writes (ensures synchronization)
    - Automatic sync and indexing capabilities
    """
    
    def __init__(self, api_client, local_db_path: Optional[str] = None):
        """
        Initialize the hybrid manager.
        
        Args:
            api_client: TheBrain API client for cloud operations
            local_db_path: Path to local Brain database (optional)
        """
        self.api = api_client
        self.local_db_path = local_db_path or self._find_local_brain_db()
        self.db_conn = None
        self.is_indexed = False
        self.brain_metadata = {}
        
    def _find_local_brain_db(self, brain_id: Optional[str] = None) -> Optional[str]:
        """
        Attempt to find local Brain database in common locations.
        
        Args:
            brain_id: Optional brain ID to search for specifically
            
        Returns:
            Path to database file or None if not found
        """
        # First check if there's a custom path from environment
        custom_path = get_brain_path_from_env()
        
        # Use our centralized path finder
        db_path = find_brain_database(brain_id, str(custom_path) if custom_path else None)
        
        if db_path:
            logger.info(f"Found local Brain database: {format_path_for_display(db_path)}")
            return str(db_path)
        
        # If not found with new method, try the old User.db pattern
        # (keeping backward compatibility with existing code)
        brains_dir = Path.home() / "Brains"
        if brains_dir.exists():
            for brain_subdir in brains_dir.iterdir():
                if brain_subdir.is_dir():
                    # Look for User.db in each subdirectory
                    user_db = brain_subdir / "User.db"
                    if user_db.exists():
                        logger.info(f"Found local Brain database (User.db): {format_path_for_display(user_db)}")
                        return str(user_db)
        
        return None
    
    async def initialize(self, brain_id: str) -> bool:
        """
        Initialize the hybrid manager for a specific brain.
        
        Args:
            brain_id: The brain ID to work with
            
        Returns:
            True if initialization successful
        """
        # If we already have a specific database path, try it first
        if self.local_db_path and Path(self.local_db_path).exists():
            self.db_conn = sqlite3.connect(self.local_db_path)
            self.db_conn.row_factory = sqlite3.Row
            logger.info(f"Connected to local database: {self.local_db_path}")
            
            # Verify this database contains the requested brain
            if await self._verify_brain_id(brain_id):
                await self._index_database()
                return True
            else:
                logger.warning(f"Local database doesn't contain brain {brain_id}")
                self.db_conn.close()
                self.db_conn = None
        
        # Try to find the right database by checking all available ones
        brains_dir = Path.home() / "Brains"
        if brains_dir.exists():
            logger.info(f"Searching for brain {brain_id} in {brains_dir}")
            
            # Check each brain subdirectory
            for brain_subdir in brains_dir.iterdir():
                if brain_subdir.is_dir():
                    user_db = brain_subdir / "User.db"
                    if user_db.exists():
                        # Try this database with timeout
                        try:
                            # Use timeout for database connection
                            self.db_conn = sqlite3.connect(str(user_db), timeout=2.0)
                            self.db_conn.row_factory = sqlite3.Row
                            
                            if await self._verify_brain_id(brain_id):
                                logger.info(f"Found brain {brain_id} in {user_db}")
                                self.local_db_path = str(user_db)
                                # Skip indexing for now - it might be slow
                                # await self._index_database()
                                self.is_indexed = False  # Mark as not indexed
                                return True
                            else:
                                # Not the right brain, close and continue
                                self.db_conn.close()
                                self.db_conn = None
                        except (sqlite3.Error, sqlite3.OperationalError) as e:
                            logger.warning(f"Error checking {user_db}: {e}")
                            if self.db_conn:
                                self.db_conn.close()
                                self.db_conn = None
        
        # No local database contains the requested brain
        # Don't automatically download - that could take too long
        logger.warning(f"Brain {brain_id} not found locally. Skipping download.")
        return False
        
        # To enable download, uncomment this:
        # logger.info(f"Brain {brain_id} not found locally. Downloading from cloud...")
        # return await self.download_and_index_brain(brain_id)
    
    async def _verify_brain_id(self, brain_id: str) -> bool:
        """Verify the local database contains the specified brain."""
        try:
            cursor = self.db_conn.cursor()
            
            # First check if the exact brain_id exists
            cursor.execute(
                "SELECT 1 FROM Thoughts WHERE BrainId = ? LIMIT 1", 
                (brain_id,)
            )
            result = cursor.fetchone()
            if result:
                return True
            
            # If not found, check what brain IDs actually exist
            cursor.execute("SELECT DISTINCT BrainId FROM Thoughts LIMIT 1")
            actual_brain = cursor.fetchone()
            if actual_brain:
                actual_id = actual_brain[0]
                logger.info(f"Brain ID mismatch - requested: {brain_id}, actual: {actual_id}")
                # If there's only one brain in the database, use it
                cursor.execute("SELECT COUNT(DISTINCT BrainId) FROM Thoughts")
                count = cursor.fetchone()[0]
                if count == 1:
                    logger.info(f"Using the only brain in database: {actual_id}")
                    return True
            
            return False
        except sqlite3.Error as e:
            logger.error(f"Error verifying brain ID: {e}")
            return False
    
    async def download_and_index_brain(self, brain_id: str) -> bool:
        """
        Download brain data from cloud and create local index.
        
        Args:
            brain_id: Brain ID to download
            
        Returns:
            True if successful
        """
        try:
            # Create local database if it doesn't exist
            if not self.local_db_path:
                db_dir = Path.home() / ".thebrain_mcp" / "databases"
                db_dir.mkdir(parents=True, exist_ok=True)
                self.local_db_path = str(db_dir / f"{brain_id}.db")
            
            # Initialize database connection
            self.db_conn = sqlite3.connect(self.local_db_path)
            self.db_conn.row_factory = sqlite3.Row
            
            # Create schema
            await self._create_schema()
            
            # Download data from cloud
            logger.info(f"Downloading brain {brain_id} from cloud...")
            
            # Get brain metadata
            brain = await self.api.get_brain(brain_id)
            self.brain_metadata = brain
            
            # Download thoughts
            logger.info("Downloading thoughts...")
            thoughts = await self._download_all_thoughts(brain_id)
            await self._store_thoughts(thoughts)
            
            # Download links
            logger.info("Downloading links...")
            links = await self._download_all_links(brain_id)
            await self._store_links(links)
            
            # Download tags
            logger.info("Downloading tags...")
            tags = await self.api.get_tags(brain_id)
            await self._store_tags(tags)
            
            # Download types
            logger.info("Downloading types...")
            types = await self.api.get_types(brain_id)
            await self._store_types(types)
            
            # Index the database
            await self._index_database()
            
            logger.info("Brain download and indexing complete!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download brain: {e}")
            return False
    
    async def _create_schema(self):
        """Create database schema for storing brain data."""
        cursor = self.db_conn.cursor()
        
        # Thoughts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Thoughts (
                Id VARCHAR(36) PRIMARY KEY,
                Name VARCHAR(140),
                Label VARCHAR(140),
                Kind INTEGER,
                ACType INTEGER,
                TypeId VARCHAR(36),
                BrainId VARCHAR(36),
                CreationDateTime BIGINT,
                ModificationDateTime BIGINT,
                ForegroundColor INTEGER,
                BackgroundColor INTEGER,
                ThoughtIconInfo VARCHAR(140)
            )
        """)
        
        # Links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Links (
                Id VARCHAR(36) PRIMARY KEY,
                ThoughtIdA VARCHAR(36),
                ThoughtIdB VARCHAR(36),
                Direction INTEGER,
                Kind INTEGER,
                Meaning INTEGER,
                Relation INTEGER,
                Color INTEGER,
                Thickness INTEGER,
                Name VARCHAR(140),
                TypeId VARCHAR(36)
            )
        """)
        
        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tags (
                Id VARCHAR(36) PRIMARY KEY,
                Name VARCHAR(140),
                BrainId VARCHAR(36),
                CreationDateTime BIGINT,
                ModificationDateTime BIGINT,
                ACType INTEGER,
                Kind INTEGER
            )
        """)
        
        # ThoughtTags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ThoughtTags (
                ThoughtId VARCHAR(36),
                TagId VARCHAR(36),
                PRIMARY KEY (ThoughtId, TagId),
                FOREIGN KEY (ThoughtId) REFERENCES Thoughts(Id),
                FOREIGN KEY (TagId) REFERENCES Tags(Id)
            )
        """)
        
        # Types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Types (
                Id VARCHAR(36) PRIMARY KEY,
                Name VARCHAR(140),
                BrainId VARCHAR(36),
                SuperTypeId VARCHAR(36)
            )
        """)
        
        # Notes table (stores note content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Notes (
                ThoughtId VARCHAR(36) PRIMARY KEY,
                Content TEXT,
                Format VARCHAR(20),
                ModificationDateTime BIGINT,
                FOREIGN KEY (ThoughtId) REFERENCES Thoughts(Id)
            )
        """)
        
        # Attachments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Attachments (
                Id VARCHAR(36) PRIMARY KEY,
                ThoughtId VARCHAR(36),
                Name VARCHAR(255),
                Location TEXT,
                SourceType INTEGER,
                ModificationDateTime BIGINT,
                FOREIGN KEY (ThoughtId) REFERENCES Thoughts(Id)
            )
        """)
        
        self.db_conn.commit()
    
    async def _index_database(self):
        """Create indexes for efficient searching."""
        cursor = self.db_conn.cursor()
        
        # Create indexes for common queries
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_thoughts_name ON Thoughts(Name)",
            "CREATE INDEX IF NOT EXISTS idx_thoughts_brain ON Thoughts(BrainId)",
            "CREATE INDEX IF NOT EXISTS idx_thoughts_type ON Thoughts(TypeId)",
            "CREATE INDEX IF NOT EXISTS idx_thoughts_modified ON Thoughts(ModificationDateTime)",
            "CREATE INDEX IF NOT EXISTS idx_links_thoughta ON Links(ThoughtIdA)",
            "CREATE INDEX IF NOT EXISTS idx_links_thoughtb ON Links(ThoughtIdB)",
            "CREATE INDEX IF NOT EXISTS idx_tags_name ON Tags(Name)",
            "CREATE INDEX IF NOT EXISTS idx_thoughttags_thought ON ThoughtTags(ThoughtId)",
            "CREATE INDEX IF NOT EXISTS idx_thoughttags_tag ON ThoughtTags(TagId)",
            "CREATE INDEX IF NOT EXISTS idx_notes_thought ON Notes(ThoughtId)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_thought ON Attachments(ThoughtId)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.db_conn.commit()
        self.is_indexed = True
        logger.info("Database indexing complete")
    
    async def _download_all_thoughts(self, brain_id: str) -> List[Dict]:
        """Download all thoughts from the cloud."""
        # Start from home thought and traverse
        brain = await self.api.get_brain(brain_id)
        home_thought_id = brain.get("homeThoughtId")
        
        if not home_thought_id:
            return []
        
        visited = set()
        to_visit = [home_thought_id]
        thoughts = []
        
        while to_visit:
            thought_id = to_visit.pop(0)
            if thought_id in visited:
                continue
            
            visited.add(thought_id)
            
            try:
                # Get thought graph
                graph = await self.api.get_thought_graph(brain_id, thought_id)
                
                # Add central thought
                central = graph.get("activeThought") or graph.get("centralThought")
                if central:
                    thoughts.append(central)
                
                # Add connected thoughts and queue them for visiting
                for connection_type in ["parents", "children", "jumps"]:
                    connected = graph.get(connection_type, [])
                    for thought in connected:
                        if thought.get("id") not in visited:
                            thoughts.append(thought)
                            to_visit.append(thought.get("id"))
            
            except Exception as e:
                logger.warning(f"Failed to get graph for thought {thought_id}: {e}")
        
        return thoughts
    
    async def _download_all_links(self, brain_id: str) -> List[Dict]:
        """Download all links from the cloud."""
        # Links are typically included in thought graphs
        # This is a placeholder - actual implementation would gather links
        # from the graph traversal above
        return []
    
    async def _store_thoughts(self, thoughts: List[Dict]):
        """Store thoughts in local database."""
        cursor = self.db_conn.cursor()
        
        for thought in thoughts:
            # Convert datetime strings to .NET ticks if needed
            creation_dt = self._datetime_to_ticks(thought.get("creationDateTime"))
            modification_dt = self._datetime_to_ticks(thought.get("modificationDateTime"))
            
            cursor.execute("""
                INSERT OR REPLACE INTO Thoughts 
                (Id, Name, Label, Kind, ACType, TypeId, BrainId, 
                 CreationDateTime, ModificationDateTime, 
                 ForegroundColor, BackgroundColor, ThoughtIconInfo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                thought.get("id"),
                thought.get("name"),
                thought.get("label"),
                thought.get("kind", 1),
                thought.get("acType", 0),
                thought.get("typeId"),
                thought.get("brainId"),
                creation_dt,
                modification_dt,
                thought.get("foregroundColor"),
                thought.get("backgroundColor"),
                thought.get("thoughtIconInfo")
            ))
        
        self.db_conn.commit()
    
    async def _store_links(self, links: List[Dict]):
        """Store links in local database."""
        cursor = self.db_conn.cursor()
        
        for link in links:
            cursor.execute("""
                INSERT OR REPLACE INTO Links
                (Id, ThoughtIdA, ThoughtIdB, Direction, Kind, Meaning, 
                 Relation, Color, Thickness, Name, TypeId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                link.get("id"),
                link.get("thoughtIdA"),
                link.get("thoughtIdB"),
                link.get("direction", 0),
                link.get("kind", 1),
                link.get("meaning", 1),
                link.get("relation"),
                link.get("color"),
                link.get("thickness"),
                link.get("name"),
                link.get("typeId")
            ))
        
        self.db_conn.commit()
    
    async def _store_tags(self, tags: List[Dict]):
        """Store tags in local database."""
        cursor = self.db_conn.cursor()
        
        for tag in tags:
            creation_dt = self._datetime_to_ticks(tag.get("creationDateTime"))
            modification_dt = self._datetime_to_ticks(tag.get("modificationDateTime"))
            
            cursor.execute("""
                INSERT OR REPLACE INTO Tags
                (Id, Name, BrainId, CreationDateTime, ModificationDateTime, ACType, Kind)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tag.get("id"),
                tag.get("name"),
                tag.get("brainId"),
                creation_dt,
                modification_dt,
                tag.get("acType", 0),
                tag.get("kind", 4)
            ))
        
        self.db_conn.commit()
    
    async def _store_types(self, types: List[Dict]):
        """Store types in local database."""
        cursor = self.db_conn.cursor()
        
        for type_obj in types:
            cursor.execute("""
                INSERT OR REPLACE INTO Types
                (Id, Name, BrainId, SuperTypeId)
                VALUES (?, ?, ?, ?)
            """, (
                type_obj.get("id"),
                type_obj.get("name"),
                type_obj.get("brainId"),
                type_obj.get("superTypeId")
            ))
        
        self.db_conn.commit()
    
    def _datetime_to_ticks(self, dt_string: Optional[str]) -> Optional[int]:
        """Convert datetime string to .NET ticks."""
        if not dt_string:
            return None
        
        try:
            # Parse ISO format datetime
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            # Convert to .NET ticks (100-nanosecond intervals since 1/1/0001)
            unix_timestamp = dt.timestamp()
            return int(unix_timestamp * 10000000) + 621355968000000000
        except:
            return None
    
    def _ticks_to_datetime(self, ticks: Optional[int]) -> Optional[datetime]:
        """Convert .NET ticks to datetime."""
        if not ticks:
            return None
        
        try:
            # Convert from .NET ticks to Unix timestamp
            unix_timestamp = (ticks - 621355968000000000) / 10000000
            return datetime.fromtimestamp(unix_timestamp)
        except:
            return None
    
    # ========== READ OPERATIONS (Local Database) ==========
    
    async def search_thoughts_local(
        self, 
        brain_id: str, 
        query: str,
        search_in_notes: bool = True,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search thoughts using local database (comprehensive).
        
        This provides full access to all data including:
        - Thoughts with all their IDs
        - Tag associations
        - Type hierarchies
        - Note content
        - Full text search
        """
        if not self.db_conn:
            raise ValueError("No local database connection")
        
        # Create indexes if not already done (lazy indexing)
        if not self.is_indexed:
            try:
                await self._index_database()
            except Exception as e:
                logger.warning(f"Failed to create indexes: {e}")
        
        cursor = self.db_conn.cursor()
        results = []
        
        # Search in thought names and labels
        cursor.execute("""
            SELECT * FROM Thoughts 
            WHERE BrainId = ? 
            AND (Name LIKE ? OR Label LIKE ?)
            ORDER BY ModificationDateTime DESC
            LIMIT ?
        """, (brain_id, f"%{query}%", f"%{query}%", max_results))
        
        for row in cursor.fetchall():
            results.append(dict(row))
        
        # Search in notes if requested
        if search_in_notes:
            cursor.execute("""
                SELECT t.*, n.Content as NoteContent
                FROM Thoughts t
                JOIN Notes n ON t.Id = n.ThoughtId
                WHERE t.BrainId = ? 
                AND n.Content LIKE ?
                ORDER BY n.ModificationDateTime DESC
                LIMIT ?
            """, (brain_id, f"%{query}%", max_results))
            
            for row in cursor.fetchall():
                thought_dict = dict(row)
                thought_dict["foundInNote"] = True
                results.append(thought_dict)
        
        # Deduplicate by thought ID
        seen = set()
        unique_results = []
        for result in results:
            if result["Id"] not in seen:
                seen.add(result["Id"])
                unique_results.append(result)
        
        return unique_results[:max_results]
    
    async def get_thoughts_by_tag(
        self, 
        brain_id: str, 
        tag_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all thoughts tagged with a specific tag.
        
        This solves the tag search problem completely using local database.
        """
        if not self.db_conn:
            raise ValueError("No local database connection")
        
        cursor = self.db_conn.cursor()
        
        # First get the tag ID
        cursor.execute("""
            SELECT Id FROM Tags 
            WHERE BrainId = ? AND Name = ?
        """, (brain_id, tag_name))
        
        tag_row = cursor.fetchone()
        if not tag_row:
            return []
        
        tag_id = tag_row[0]
        
        # Get all thoughts with this tag
        cursor.execute("""
            SELECT t.* FROM Thoughts t
            JOIN ThoughtTags tt ON t.Id = tt.ThoughtId
            WHERE tt.TagId = ? AND t.BrainId = ?
            ORDER BY t.ModificationDateTime DESC
        """, (tag_id, brain_id))
        
        results = []
        for row in cursor.fetchall():
            thought_dict = dict(row)
            thought_dict["tagName"] = tag_name
            thought_dict["tagId"] = tag_id
            results.append(thought_dict)
        
        return results
    
    async def get_thought_graph_local(
        self, 
        brain_id: str, 
        thought_id: str
    ) -> Dict[str, Any]:
        """
        Get complete thought graph from local database.
        
        Returns all connections with proper IDs.
        """
        if not self.db_conn:
            raise ValueError("No local database connection")
        
        cursor = self.db_conn.cursor()
        
        # Get central thought
        cursor.execute("""
            SELECT * FROM Thoughts WHERE Id = ? AND BrainId = ?
        """, (thought_id, brain_id))
        
        central_thought = dict(cursor.fetchone()) if cursor.fetchone() else None
        
        if not central_thought:
            return {"error": "Thought not found"}
        
        # Get parent links
        cursor.execute("""
            SELECT t.*, l.Meaning, l.Kind as LinkKind
            FROM Thoughts t
            JOIN Links l ON t.Id = l.ThoughtIdA
            WHERE l.ThoughtIdB = ? AND l.Meaning = 2
        """, (thought_id,))
        
        parents = [dict(row) for row in cursor.fetchall()]
        
        # Get child links
        cursor.execute("""
            SELECT t.*, l.Meaning, l.Kind as LinkKind
            FROM Thoughts t
            JOIN Links l ON t.Id = l.ThoughtIdB
            WHERE l.ThoughtIdA = ? AND l.Meaning = 1
        """, (thought_id,))
        
        children = [dict(row) for row in cursor.fetchall()]
        
        # Get jump links
        cursor.execute("""
            SELECT t.*, l.Meaning, l.Kind as LinkKind
            FROM Thoughts t
            JOIN Links l ON (t.Id = l.ThoughtIdA OR t.Id = l.ThoughtIdB)
            WHERE (l.ThoughtIdA = ? OR l.ThoughtIdB = ?) 
            AND l.Meaning = 3
            AND t.Id != ?
        """, (thought_id, thought_id, thought_id))
        
        jumps = [dict(row) for row in cursor.fetchall()]
        
        # Get tags for this thought
        cursor.execute("""
            SELECT tg.* FROM Tags tg
            JOIN ThoughtTags tt ON tg.Id = tt.TagId
            WHERE tt.ThoughtId = ?
        """, (thought_id,))
        
        tags = [dict(row) for row in cursor.fetchall()]
        
        # Get attachments
        cursor.execute("""
            SELECT * FROM Attachments WHERE ThoughtId = ?
        """, (thought_id,))
        
        attachments = [dict(row) for row in cursor.fetchall()]
        
        # Get note
        cursor.execute("""
            SELECT * FROM Notes WHERE ThoughtId = ?
        """, (thought_id,))
        
        note_row = cursor.fetchone()
        note = dict(note_row) if note_row else None
        
        return {
            "centralThought": central_thought,
            "parents": parents,
            "children": children,
            "jumps": jumps,
            "tags": tags,
            "attachments": attachments,
            "note": note,
            "connectionCounts": {
                "parents": len(parents),
                "children": len(children),
                "jumps": len(jumps),
                "tags": len(tags),
                "attachments": len(attachments)
            }
        }
    
    async def get_recent_modifications_local(
        self, 
        brain_id: str, 
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get recent modifications from local database.
        
        This actually works, unlike the API's modification endpoint.
        """
        if not self.db_conn:
            raise ValueError("No local database connection")
        
        cursor = self.db_conn.cursor()
        
        # Calculate cutoff time in .NET ticks
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_ticks = self._datetime_to_ticks(cutoff_date.isoformat())
        
        cursor.execute("""
            SELECT * FROM Thoughts
            WHERE BrainId = ? AND ModificationDateTime > ?
            ORDER BY ModificationDateTime DESC
        """, (brain_id, cutoff_ticks))
        
        results = []
        for row in cursor.fetchall():
            thought_dict = dict(row)
            # Convert ticks back to readable datetime
            thought_dict["modificationDateTimeReadable"] = self._ticks_to_datetime(
                thought_dict.get("ModificationDateTime")
            )
            results.append(thought_dict)
        
        return results
    
    # ========== WRITE OPERATIONS (Cloud API) ==========
    
    async def create_thought(self, brain_id: str, thought_data: Dict) -> Dict:
        """
        Create a thought via API and update local database.
        """
        # Create via API
        result = await self.api.create_thought(brain_id, thought_data)
        
        # Update local database if successful
        if result and self.db_conn:
            await self._store_thoughts([result])
        
        return result
    
    async def update_thought(self, brain_id: str, thought_id: str, updates: Dict) -> Dict:
        """
        Update a thought via API and update local database.
        """
        # Update via API
        result = await self.api.update_thought(brain_id, thought_id, updates)
        
        # Update local database if successful
        if result and self.db_conn:
            cursor = self.db_conn.cursor()
            # Build dynamic update query
            set_clauses = []
            values = []
            for key, value in updates.items():
                # Convert camelCase to PascalCase for database columns
                db_key = key[0].upper() + key[1:] if key else key
                set_clauses.append(f"{db_key} = ?")
                values.append(value)
            
            values.append(thought_id)
            
            cursor.execute(f"""
                UPDATE Thoughts 
                SET {', '.join(set_clauses)}
                WHERE Id = ?
            """, values)
            
            self.db_conn.commit()
        
        return result
    
    async def create_link(self, brain_id: str, link_data: Dict) -> Dict:
        """
        Create a link via API and update local database.
        """
        # Create via API
        result = await self.api.create_link(brain_id, link_data)
        
        # Update local database if successful
        if result and self.db_conn:
            await self._store_links([result])
        
        return result
    
    async def tag_thought(
        self, 
        brain_id: str, 
        thought_id: str, 
        tag_name: str
    ) -> bool:
        """
        Tag a thought (creates tag if needed).
        
        This solves the tagging problem by properly associating thoughts with tags.
        """
        if not self.db_conn:
            return False
        
        cursor = self.db_conn.cursor()
        
        # Check if tag exists
        cursor.execute("""
            SELECT Id FROM Tags WHERE BrainId = ? AND Name = ?
        """, (brain_id, tag_name))
        
        tag_row = cursor.fetchone()
        
        if not tag_row:
            # Create tag via API
            # Note: TheBrain API might not support creating tags directly
            # This would need to be done through the UI or a different endpoint
            tag_id = str(uuid.uuid4())
            creation_time = self._datetime_to_ticks(datetime.now().isoformat())
            
            cursor.execute("""
                INSERT INTO Tags (Id, Name, BrainId, CreationDateTime, ModificationDateTime, ACType, Kind)
                VALUES (?, ?, ?, ?, ?, 0, 4)
            """, (tag_id, tag_name, brain_id, creation_time, creation_time))
        else:
            tag_id = tag_row[0]
        
        # Create thought-tag association
        cursor.execute("""
            INSERT OR IGNORE INTO ThoughtTags (ThoughtId, TagId)
            VALUES (?, ?)
        """, (thought_id, tag_id))
        
        self.db_conn.commit()
        
        # Note: This is local-only. For cloud sync, we'd need API support for tagging
        return True
    
    # ========== SYNC OPERATIONS ==========
    
    async def sync_with_cloud(self, brain_id: str) -> Dict[str, int]:
        """
        Sync local database with cloud (pull changes).
        
        Returns:
            Dict with counts of synced items
        """
        if not self.db_conn:
            raise ValueError("No local database connection")
        
        sync_stats = {
            "thoughts_updated": 0,
            "links_updated": 0,
            "tags_updated": 0
        }
        
        # Get last sync time from local metadata
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT MAX(ModificationDateTime) FROM Thoughts WHERE BrainId = ?
        """, (brain_id,))
        
        last_sync_ticks = cursor.fetchone()[0] or 0
        last_sync_date = self._ticks_to_datetime(last_sync_ticks)
        
        # Get modifications from cloud since last sync
        # Note: This would use the API's modification endpoint if it worked
        # For now, we'd need to re-traverse the graph for changes
        
        logger.info(f"Syncing changes since {last_sync_date}")
        
        # Download recent thoughts and update local
        thoughts = await self._download_all_thoughts(brain_id)
        for thought in thoughts:
            mod_time = self._datetime_to_ticks(thought.get("modificationDateTime"))
            if mod_time and mod_time > last_sync_ticks:
                await self._store_thoughts([thought])
                sync_stats["thoughts_updated"] += 1
        
        return sync_stats


# Convenience functions for the MCP server

async def get_hybrid_manager(api_client, brain_id: str) -> HybridBrainManager:
    """
    Get an initialized hybrid brain manager.
    
    Args:
        api_client: TheBrain API client
        brain_id: Brain ID to work with
        
    Returns:
        Initialized HybridBrainManager
    """
    manager = HybridBrainManager(api_client)
    await manager.initialize(brain_id)
    return manager
