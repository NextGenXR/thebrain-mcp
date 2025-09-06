"""
Optimized thought search strategies for TheBrain MCP server.

This module provides alternative approaches to deal with TheBrain API's search limitations
without resorting to deep graph traversal which can be prohibitively slow.
"""

from typing import Dict, Any, Optional, List, Set
import asyncio
from datetime import datetime, timedelta

# Cache for frequently accessed thoughts
THOUGHT_CACHE = {}
CACHE_EXPIRY = {}
CACHE_TTL = 300  # 5 minutes

async def search_thoughts_with_strategies(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced search with multiple strategies to avoid slow graph traversal.
    
    Strategies:
    1. Direct API search (always try first)
    2. Cache lookup for recent searches
    3. Modifications-based search (recent activity)
    4. Limited graph search (only if absolutely necessary)
    """
    brain_id = args.get("brainId")
    query_text = args["queryText"]
    max_results = args.get("maxResults", 30)
    only_search_thought_names = args.get("onlySearchThoughtNames", False)
    
    # Strategy 1: Try direct API search first
    results = await api.search_thoughts(
        brain_id, query_text, max_results, only_search_thought_names
    )
    
    thoughts = []
    attachments = []
    
    # Process API results
    for result in results:
        entity_type = result.get("entityType")
        result_type = result.get("searchResultType")
        
        if result_type == 4 or entity_type == 4:
            attachments.append(result)
        elif entity_type == 2 or result_type == 1:
            thought_id = result.get("id") or result.get("thoughtId")
            if thought_id:
                thoughts.append(result)
    
    # If we found thoughts, return them
    if thoughts:
        return {
            "success": True,
            "results": thoughts + attachments,
            "thoughts": thoughts,
            "attachments": attachments,
            "count": len(thoughts) + len(attachments),
            "thoughtCount": len(thoughts),
            "attachmentCount": len(attachments),
            "query": query_text,
            "searchStrategy": "direct_api"
        }
    
    # Strategy 2: Check cache for exact name matches
    cache_key = f"{brain_id}:{query_text.lower()}"
    if cache_key in THOUGHT_CACHE:
        expiry = CACHE_EXPIRY.get(cache_key)
        if expiry and datetime.now() < expiry:
            cached_thought = THOUGHT_CACHE[cache_key]
            return {
                "success": True,
                "results": [cached_thought],
                "thoughts": [cached_thought],
                "attachments": [],
                "count": 1,
                "thoughtCount": 1,
                "attachmentCount": 0,
                "query": query_text,
                "searchStrategy": "cache",
                "note": "Found in cache"
            }
    
    # Strategy 3: Try searching recent modifications
    if only_search_thought_names:
        try:
            # Get recent modifications to find recently active thoughts
            mods = await api.get_brain_modifications(brain_id, max_logs=100)
            
            # Look for the thought name in recent modifications
            for mod in mods:
                thought_name = mod.get("thoughtName", "")
                if thought_name.lower() == query_text.lower():
                    thought_id = mod.get("thoughtId")
                    if thought_id:
                        # Get the full thought
                        try:
                            thought = await api.get_thought(brain_id, thought_id)
                            if thought:
                                # Cache it for future use
                                THOUGHT_CACHE[cache_key] = thought
                                CACHE_EXPIRY[cache_key] = datetime.now() + timedelta(seconds=CACHE_TTL)
                                
                                return {
                                    "success": True,
                                    "results": [thought],
                                    "thoughts": [thought],
                                    "attachments": [],
                                    "count": 1,
                                    "thoughtCount": 1,
                                    "attachmentCount": 0,
                                    "query": query_text,
                                    "searchStrategy": "modifications",
                                    "note": "Found in recent modifications"
                                }
                        except:
                            pass
        except:
            pass
    
    # Strategy 4: Limited graph search (only 1 level deep from home)
    # This is much faster than deep traversal but still helps with common cases
    if only_search_thought_names and len(thoughts) == 0:
        try:
            brain = await api.get_brain(brain_id)
            home_id = brain.get("homeThoughtId")
            
            if home_id:
                # Only check immediate connections of home thought
                graph = await api.get_thought_graph(brain_id, home_id, include_siblings=False)
                
                # Check active thought
                active = graph.get("activeThought", {})
                if active.get("name", "").lower() == query_text.lower():
                    thoughts.append(active)
                
                # Check immediate connections only (no recursion)
                for conn_type in ["parents", "children", "jumps"]:
                    for thought in graph.get(conn_type, []):
                        if thought.get("name", "").lower() == query_text.lower():
                            thoughts.append(thought)
                            break
                    if thoughts:
                        break
                
                if thoughts:
                    # Cache the found thought
                    THOUGHT_CACHE[cache_key] = thoughts[0]
                    CACHE_EXPIRY[cache_key] = datetime.now() + timedelta(seconds=CACHE_TTL)
                    
                    return {
                        "success": True,
                        "results": thoughts,
                        "thoughts": thoughts,
                        "attachments": [],
                        "count": len(thoughts),
                        "thoughtCount": len(thoughts),
                        "attachmentCount": 0,
                        "query": query_text,
                        "searchStrategy": "limited_graph",
                        "note": "Found via limited graph search (1 level only)"
                    }
        except:
            pass
    
    # No results found with any strategy
    return {
        "success": True,
        "results": attachments,
        "thoughts": [],
        "attachments": attachments,
        "count": len(attachments),
        "thoughtCount": 0,
        "attachmentCount": len(attachments),
        "query": query_text,
        "searchStrategy": "none",
        "note": f"No thoughts found for '{query_text}'. Try: 1) Partial search terms, 2) Navigate from known thoughts, 3) Check recent modifications"
    }


async def populate_cache_from_modifications(api, brain_id: str, max_items: int = 50):
    """
    Pre-populate cache with recently modified thoughts.
    This can be called periodically to improve search performance.
    """
    try:
        mods = await api.get_brain_modifications(brain_id, max_logs=max_items)
        
        # Get unique thought IDs from modifications
        thought_ids = set()
        for mod in mods:
            thought_id = mod.get("thoughtId")
            if thought_id:
                thought_ids.add(thought_id)
        
        # Fetch thoughts in parallel (but limit concurrency)
        async def fetch_and_cache(thought_id):
            try:
                thought = await api.get_thought(brain_id, thought_id)
                if thought and thought.get("name"):
                    cache_key = f"{brain_id}:{thought['name'].lower()}"
                    THOUGHT_CACHE[cache_key] = thought
                    CACHE_EXPIRY[cache_key] = datetime.now() + timedelta(seconds=CACHE_TTL)
                return thought
            except:
                return None
        
        # Limit concurrent requests to avoid overwhelming the API
        semaphore = asyncio.Semaphore(5)
        
        async def fetch_with_limit(thought_id):
            async with semaphore:
                return await fetch_and_cache(thought_id)
        
        tasks = [fetch_with_limit(tid) for tid in list(thought_ids)[:max_items]]
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r is not None)
        return {
            "success": True,
            "cached": successful,
            "message": f"Pre-cached {successful} thoughts from recent modifications"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def clear_cache():
    """Clear the thought cache."""
    global THOUGHT_CACHE, CACHE_EXPIRY
    THOUGHT_CACHE = {}
    CACHE_EXPIRY = {}
    return {"success": True, "message": "Cache cleared"}


def get_cache_stats():
    """Get statistics about the cache."""
    now = datetime.now()
    valid_entries = sum(1 for key in CACHE_EXPIRY if CACHE_EXPIRY[key] > now)
    return {
        "total_entries": len(THOUGHT_CACHE),
        "valid_entries": valid_entries,
        "expired_entries": len(THOUGHT_CACHE) - valid_entries
    }
