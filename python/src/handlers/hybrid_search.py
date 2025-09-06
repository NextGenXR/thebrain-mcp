"""
Enhanced search handlers using hybrid local/cloud approach.

These handlers provide comprehensive search capabilities by using:
- Local database for reads (complete access with tags, types, etc.)
- Cloud API for writes (maintains synchronization)
"""

from typing import Dict, Any, List, Optional
import logging
from ..hybrid_brain_manager import HybridBrainManager

logger = logging.getLogger(__name__)

# Cache for hybrid managers per brain
_manager_cache: Dict[str, HybridBrainManager] = {}


async def get_or_create_manager(api, brain_id: str) -> HybridBrainManager:
    """Get or create a hybrid manager for a brain."""
    if brain_id not in _manager_cache:
        manager = HybridBrainManager(api)
        if await manager.initialize(brain_id):
            _manager_cache[brain_id] = manager
        else:
            raise ValueError(f"Failed to initialize hybrid manager for brain {brain_id}")
    
    return _manager_cache[brain_id]


async def search_thoughts_hybrid(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced search using hybrid local/cloud approach.
    
    This provides:
    - Full access to all thought IDs
    - Tag-based searching that actually works
    - Content search in notes
    - Type-based filtering
    - Recent modifications tracking
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        query_text = args["queryText"]
        max_results = args.get("maxResults", 100)
        search_in_notes = args.get("searchInNotes", True)
        
        # Get or create hybrid manager
        manager = await get_or_create_manager(api, brain_id)
        
        # Check for special search syntax
        results = []
        search_type = "general"
        
        if query_text.startswith("tag:"):
            # Tag-based search
            tag_name = query_text[4:].strip()
            results = await manager.get_thoughts_by_tag(brain_id, tag_name)
            search_type = "tag"
            
        elif query_text.startswith("type:"):
            # Type-based search
            type_name = query_text[5:].strip()
            results = await search_by_type(manager, brain_id, type_name)
            search_type = "type"
            
        elif query_text.startswith("recent:"):
            # Recent modifications
            days = int(query_text[7:].strip()) if query_text[7:].strip().isdigit() else 7
            results = await manager.get_recent_modifications_local(brain_id, days)
            search_type = "recent"
            
        else:
            # General search
            results = await manager.search_thoughts_local(
                brain_id, 
                query_text,
                search_in_notes=search_in_notes,
                max_results=max_results
            )
        
        # Process results to ensure consistent format
        processed_results = []
        for result in results:
            thought = {
                "id": result.get("Id"),
                "thoughtId": result.get("Id"),
                "name": result.get("Name"),
                "label": result.get("Label"),
                "kind": result.get("Kind"),
                "typeId": result.get("TypeId"),
                "brainId": brain_id,
                "creationDateTime": manager._ticks_to_datetime(result.get("CreationDateTime")),
                "modificationDateTime": manager._ticks_to_datetime(result.get("ModificationDateTime")),
                "foregroundColor": result.get("ForegroundColor"),
                "backgroundColor": result.get("BackgroundColor"),
                "type": "thought",
                "searchType": search_type,
            }
            
            # Add additional metadata based on search type
            if search_type == "tag":
                thought["tagName"] = result.get("tagName")
                thought["tagId"] = result.get("tagId")
            elif result.get("foundInNote"):
                thought["foundInNote"] = True
                thought["notePreview"] = result.get("NoteContent", "")[:200]
            
            processed_results.append(thought)
        
        return {
            "success": True,
            "results": processed_results,
            "thoughts": processed_results,  # All have IDs!
            "count": len(processed_results),
            "searchType": search_type,
            "query": query_text,
            "usingLocalDatabase": True,
            "note": f"Found {len(processed_results)} results using local database (complete access)"
        }
        
    except Exception as e:
        logger.error(f"Hybrid search error: {e}")
        # Fall back to regular API search
        logger.info("Falling back to API search")
        from .thoughts import search_thoughts
        return await search_thoughts(api, args)


async def search_by_type(manager: HybridBrainManager, brain_id: str, type_name: str) -> List[Dict]:
    """Search for thoughts of a specific type."""
    if not manager.db_conn:
        return []
    
    cursor = manager.db_conn.cursor()
    
    # First find the type ID
    cursor.execute("""
        SELECT Id FROM Types WHERE BrainId = ? AND Name LIKE ?
    """, (brain_id, f"%{type_name}%"))
    
    type_row = cursor.fetchone()
    if not type_row:
        return []
    
    type_id = type_row[0]
    
    # Get all thoughts of this type
    cursor.execute("""
        SELECT * FROM Thoughts 
        WHERE BrainId = ? AND TypeId = ?
        ORDER BY ModificationDateTime DESC
    """, (brain_id, type_id))
    
    results = []
    for row in cursor.fetchall():
        thought_dict = dict(row)
        thought_dict["typeName"] = type_name
        results.append(thought_dict)
    
    return results


async def get_thought_graph_hybrid(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get complete thought graph using hybrid approach.
    
    Provides:
    - All connections with proper IDs
    - Tag associations
    - Note content
    - Attachments
    - Complete relationship data
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        
        # Get or create hybrid manager
        manager = await get_or_create_manager(api, brain_id)
        
        # Get complete graph from local database
        graph = await manager.get_thought_graph_local(brain_id, thought_id)
        
        if "error" in graph:
            # Fall back to API if thought not found locally
            from .thoughts import get_thought_graph
            return await get_thought_graph(api, args)
        
        # Format response
        return {
            "success": True,
            "graph": graph,
            "usingLocalDatabase": True,
            "note": "Complete graph with all relationships from local database"
        }
        
    except Exception as e:
        logger.error(f"Hybrid graph error: {e}")
        # Fall back to regular API
        from .thoughts import get_thought_graph
        return await get_thought_graph(api, args)


async def get_tagged_thoughts(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get all thoughts with a specific tag.
    
    This actually works, unlike the API's tag search!
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        tag_name = args["tagName"]
        
        # Get or create hybrid manager
        manager = await get_or_create_manager(api, brain_id)
        
        # Get thoughts by tag from local database
        results = await manager.get_thoughts_by_tag(brain_id, tag_name)
        
        # Process results
        processed_results = []
        for result in results:
            thought = {
                "id": result.get("Id"),
                "thoughtId": result.get("Id"),
                "name": result.get("Name"),
                "label": result.get("Label"),
                "kind": result.get("Kind"),
                "typeId": result.get("TypeId"),
                "brainId": brain_id,
                "tagName": tag_name,
                "tagId": result.get("tagId"),
                "type": "thought"
            }
            processed_results.append(thought)
        
        return {
            "success": True,
            "thoughts": processed_results,
            "count": len(processed_results),
            "tagName": tag_name,
            "usingLocalDatabase": True,
            "note": f"Found {len(processed_results)} thoughts tagged with '{tag_name}'"
        }
        
    except Exception as e:
        logger.error(f"Tag search error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def sync_brain_data(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync local database with cloud data.
    
    Can be called periodically to ensure local data is up to date.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        force_download = args.get("forceDownload", False)
        
        # Get or create hybrid manager
        manager = await get_or_create_manager(api, brain_id)
        
        if force_download:
            # Re-download everything
            success = await manager.download_and_index_brain(brain_id)
            return {
                "success": success,
                "action": "full_download",
                "message": "Brain data downloaded and indexed" if success else "Download failed"
            }
        else:
            # Incremental sync
            stats = await manager.sync_with_cloud(brain_id)
            return {
                "success": True,
                "action": "incremental_sync",
                "stats": stats,
                "message": f"Synced {sum(stats.values())} items"
            }
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_brain_statistics(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get comprehensive statistics about a brain using local database.
    
    Provides accurate counts and metadata that the API might not expose.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        # Get or create hybrid manager
        manager = await get_or_create_manager(api, brain_id)
        
        if not manager.db_conn:
            return {"success": False, "error": "No local database"}
        
        cursor = manager.db_conn.cursor()
        stats = {}
        
        # Count thoughts
        cursor.execute("SELECT COUNT(*) FROM Thoughts WHERE BrainId = ?", (brain_id,))
        stats["totalThoughts"] = cursor.fetchone()[0]
        
        # Count by type
        cursor.execute("""
            SELECT Kind, COUNT(*) as count 
            FROM Thoughts 
            WHERE BrainId = ? 
            GROUP BY Kind
        """, (brain_id,))
        stats["thoughtsByKind"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count links
        cursor.execute("""
            SELECT COUNT(*) FROM Links l
            JOIN Thoughts t ON (l.ThoughtIdA = t.Id OR l.ThoughtIdB = t.Id)
            WHERE t.BrainId = ?
        """, (brain_id,))
        stats["totalLinks"] = cursor.fetchone()[0]
        
        # Count tags
        cursor.execute("SELECT COUNT(*) FROM Tags WHERE BrainId = ?", (brain_id,))
        stats["totalTags"] = cursor.fetchone()[0]
        
        # Count tagged thoughts
        cursor.execute("""
            SELECT COUNT(DISTINCT ThoughtId) FROM ThoughtTags tt
            JOIN Thoughts t ON tt.ThoughtId = t.Id
            WHERE t.BrainId = ?
        """, (brain_id,))
        stats["taggedThoughts"] = cursor.fetchone()[0]
        
        # Count types
        cursor.execute("SELECT COUNT(*) FROM Types WHERE BrainId = ?", (brain_id,))
        stats["totalTypes"] = cursor.fetchone()[0]
        
        # Count notes
        cursor.execute("""
            SELECT COUNT(*) FROM Notes n
            JOIN Thoughts t ON n.ThoughtId = t.Id
            WHERE t.BrainId = ?
        """, (brain_id,))
        stats["totalNotes"] = cursor.fetchone()[0]
        
        # Count attachments
        cursor.execute("""
            SELECT COUNT(*) FROM Attachments a
            JOIN Thoughts t ON a.ThoughtId = t.Id
            WHERE t.BrainId = ?
        """, (brain_id,))
        stats["totalAttachments"] = cursor.fetchone()[0]
        
        # Get most recent modification
        cursor.execute("""
            SELECT MAX(ModificationDateTime) FROM Thoughts WHERE BrainId = ?
        """, (brain_id,))
        last_mod_ticks = cursor.fetchone()[0]
        if last_mod_ticks:
            stats["lastModified"] = str(manager._ticks_to_datetime(last_mod_ticks))
        
        # Get orphaned thoughts (no links)
        cursor.execute("""
            SELECT COUNT(*) FROM Thoughts t
            WHERE t.BrainId = ? 
            AND NOT EXISTS (
                SELECT 1 FROM Links l 
                WHERE l.ThoughtIdA = t.Id OR l.ThoughtIdB = t.Id
            )
        """, (brain_id,))
        stats["orphanedThoughts"] = cursor.fetchone()[0]
        
        return {
            "success": True,
            "statistics": stats,
            "usingLocalDatabase": True,
            "databasePath": manager.local_db_path
        }
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
