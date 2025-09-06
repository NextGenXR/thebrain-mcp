"""
Thought operation handlers for TheBrain MCP server.
"""

from typing import Dict, Any, Optional, List


async def find_thought_by_name(api, brain_id: str, name: str, start_thought_id: Optional[str] = None, max_depth: int = 3) -> Optional[Dict[str, Any]]:
    """
    Helper function to find a thought by exact name using breadth-first search.
    Since search API doesn't work well for exact names, this traverses the graph.
    """
    try:
        # If no starting point, use the home thought
        if not start_thought_id:
            brain = await api.get_brain(brain_id)
            start_thought_id = brain.get("homeThoughtId")
            if not start_thought_id:
                return None
        
        # Keep track of visited thoughts to avoid cycles
        visited = set()
        queue = [(start_thought_id, 0)]  # (thought_id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            # Skip if we've already visited this thought or exceeded max depth
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)
            
            # Get the graph for the current thought
            try:
                graph = await api.get_thought_graph(brain_id, current_id, include_siblings=False)
            except:
                continue
            
            # Check the active/central thought
            active = graph.get("activeThought", {})
            if active.get("name") == name:
                return active
            
            # Check all connected thoughts
            for connection_type in ["parents", "children", "jumps"]:
                thoughts = graph.get(connection_type, [])
                for thought in thoughts:
                    if thought.get("name") == name:
                        return thought
                    # Add to queue for deeper search
                    if depth < max_depth and thought.get("id"):
                        queue.append((thought.get("id"), depth + 1))
        
        return None
    except Exception:
        return None


async def list_brains(api) -> Dict[str, Any]:
    """List all available brains for the user."""
    try:
        brains = await api.list_brains()
        return {
            "success": True,
            "brains": [
                {
                    "id": brain.get("id"),
                    "brainId": brain.get("id"),  # Include both for compatibility
                    "name": brain.get("name"),
                    "homeThoughtId": brain.get("homeThoughtId"),
                    # Include any additional fields that might be useful
                    "description": brain.get("description"),
                    "createdDateTime": brain.get("createdDateTime"),
                    "modifiedDateTime": brain.get("modifiedDateTime"),
                }
                for brain in brains
            ],
            "count": len(brains),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_brain(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get details about a specific brain."""
    try:
        brain_id = args["brainId"]
        brain = await api.get_brain(brain_id)
        return {
            "success": True,
            "brain": {
                "id": brain.get("id"),
                "name": brain.get("name"),
                "homeThoughtId": brain.get("homeThoughtId"),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def set_active_brain(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Set the active brain for subsequent operations."""
    try:
        brain_id = args["brainId"]
        # Verify brain exists
        await api.get_brain(brain_id)
        return {
            "success": True,
            "message": f"Active brain set to {brain_id}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to set active brain: {e}",
        }


async def create_thought(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new thought with optional visual properties."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required. Use set_active_brain first or provide brainId.")
        
        # Extract parameters
        name = args["name"]
        kind = args.get("kind", 1)  # Default to Normal
        label = args.get("label")
        foreground_color = args.get("foregroundColor")
        background_color = args.get("backgroundColor")
        type_id = args.get("typeId")
        source_thought_id = args.get("sourceThoughtId")
        relation = args.get("relation")
        ac_type = args.get("acType", 0)  # Default to Public
        
        # Build thought data
        thought_data = {
            "name": name,
            "kind": kind,
            "acType": ac_type,
        }
        
        # Add optional properties
        if label:
            thought_data["label"] = label
        if type_id:
            thought_data["typeId"] = type_id
        if source_thought_id:
            thought_data["sourceThoughtId"] = source_thought_id
            thought_data["relation"] = relation or 1  # Default to Child
        
        # Create the thought
        result = await api.create_thought(brain_id, thought_data)
        thought_id = result.get("id")
        
        # Apply visual properties if provided
        if foreground_color or background_color:
            updates = {}
            if foreground_color:
                updates["foregroundColor"] = foreground_color
            if background_color:
                updates["backgroundColor"] = background_color
            
            await api.update_thought(brain_id, thought_id, updates)
        
        return {
            "success": True,
            "thought": {
                "id": thought_id,
                "brainId": brain_id,
                "name": name,
                "kind": kind,
                "label": label,
                "acType": ac_type,
                "typeId": type_id,
                "foregroundColor": foreground_color,
                "backgroundColor": background_color,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_thought(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get details about a specific thought."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        thought = await api.get_thought(brain_id, thought_id)
        
        return {
            "success": True,
            "thought": thought,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def update_thought(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Update a thought including its visual properties."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        
        # Collect updates
        updates = {}
        for field in ["name", "label", "foregroundColor", "backgroundColor", "kind", "acType", "typeId"]:
            if field in args and args[field] is not None:
                updates[field] = args[field]
        
        if not updates:
            return {
                "success": True,
                "message": "No updates provided",
            }
        
        await api.update_thought(brain_id, thought_id, updates)
        
        return {
            "success": True,
            "thought": {
                "id": thought_id,
                "brainId": brain_id,
                **updates,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def delete_thought(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a thought."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        await api.delete_thought(brain_id, thought_id)
        
        return {
            "success": True,
            "message": f"Thought {thought_id} deleted successfully",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def search_thoughts(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Search for thoughts in a brain - automatically uses local DB when available."""
    # Try to use hybrid search first (local database) with timeout
    try:
        import asyncio
        from .hybrid_search import search_thoughts_hybrid
        
        # Add timeout to prevent hanging
        result = await asyncio.wait_for(
            search_thoughts_hybrid(api, args),
            timeout=5.0  # 5 second timeout
        )
        return result
    except asyncio.TimeoutError:
        # Hybrid search timed out, fall back to API
        import sys
        print(f"[WARNING] Local database search timed out, using API", file=sys.stderr)
    except (ImportError, Exception) as e:
        # Fall back to API-only search if hybrid not available
        import sys
        print(f"[WARNING] Hybrid search failed: {e}, using API", file=sys.stderr)
    
    # Original API-based implementation as fallback
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        query_text = args["queryText"]
        max_results = args.get("maxResults", 30)
        only_search_thought_names = args.get("onlySearchThoughtNames", False)
        
        # Perform the search
        results = await api.search_thoughts(
            brain_id, query_text, max_results, only_search_thought_names
        )
        
        # Process search results - categorize by type and ID availability
        thoughts_with_ids = []
        thoughts_without_ids = []
        attachments = []
        
        for result in results:
            result_type = result.get("searchResultType", 1)
            entity_type = result.get("entityType")
            
            # Handle attachments
            if result_type == 4 or entity_type == 4:
                attachment_id = result.get("attachmentId")
                source_id = result.get("sourceId")
                
                attachments.append({
                    "attachmentId": attachment_id,
                    "thoughtId": source_id,
                    "name": result.get("name"),
                    "sourceType": result.get("sourceType"),
                    "brainId": result.get("brainId") or brain_id,
                    "brainName": result.get("brainName"),
                    "type": "attachment",
                })
            
            # Handle thoughts
            elif entity_type == 2 or result_type == 1:
                # Try multiple possible ID fields
                thought_id = (
                    result.get("id") or 
                    result.get("thoughtId") or 
                    result.get("Id") or 
                    result.get("ThoughtId") or
                    result.get("sourceId")
                )
                
                thought_name = result.get("name") or result.get("Name", "")
                
                # Create thought object
                thought_obj = {
                    "name": thought_name,
                    "label": result.get("label"),
                    "kind": result.get("kind"),
                    "creationDateTime": result.get("creationDateTime"),
                    "modificationDateTime": result.get("modificationDateTime"),
                    "matchType": result.get("matchType"),
                    "score": result.get("score"),
                    "typeId": result.get("typeId"),
                    "acType": result.get("acType"),
                    "entityType": entity_type,
                    "searchResultType": result_type,
                    "brainId": result.get("brainId") or brain_id,
                    "type": "thought",
                }
                
                if thought_id and not thought_id.startswith("name:"):
                    # We have a valid ID
                    thought_obj["id"] = thought_id
                    thought_obj["thoughtId"] = thought_id
                    thoughts_with_ids.append(thought_obj)
                else:
                    # No ID available - this is a name-only match
                    thought_obj["nameOnlyMatch"] = True
                    thoughts_without_ids.append(thought_obj)
        
        # Try alternative search for a few thoughts without IDs
        if thoughts_without_ids and len(thoughts_without_ids) <= 5:
            for thought in thoughts_without_ids[:]:
                if thought.get("name"):
                    # Try exact name search with quotes
                    try:
                        exact_search = await api.search_thoughts(
                            brain_id, 
                            f'"{thought["name"]}"',
                            max_results=5,
                            only_search_thought_names=True
                        )
                        
                        for exact_result in exact_search:
                            exact_id = (
                                exact_result.get("id") or 
                                exact_result.get("thoughtId")
                            )
                            exact_name = exact_result.get("name", "")
                            
                            if exact_id and exact_name == thought["name"]:
                                # Found it! Move to thoughts with IDs
                                thought["id"] = exact_id
                                thought["thoughtId"] = exact_id
                                thought["resolvedViaExactSearch"] = True
                                del thought["nameOnlyMatch"]
                                thoughts_without_ids.remove(thought)
                                thoughts_with_ids.append(thought)
                                break
                    except:
                        pass  # If exact search fails, keep as name-only
        
        # Combine all results
        all_thoughts = thoughts_with_ids + thoughts_without_ids
        all_results = all_thoughts + attachments
        
        # Build response with clear categorization
        response = {
            "success": True,
            "results": all_results,
            "thoughts": thoughts_with_ids,  # Only thoughts with valid IDs
            "thoughtsWithoutIds": thoughts_without_ids,  # Name matches without IDs
            "attachments": attachments,
            "count": len(all_results),
            "thoughtCount": len(thoughts_with_ids),
            "thoughtWithoutIdCount": len(thoughts_without_ids),
            "attachmentCount": len(attachments),
            "query": query_text,
        }
        
        # Add helpful notes
        if thoughts_without_ids:
            names = [t.get("name", "Unknown") for t in thoughts_without_ids[:3]]
            names_str = ", ".join(f'"{n}"' for n in names)
            if len(thoughts_without_ids) > 3:
                names_str += f" and {len(thoughts_without_ids) - 3} more"
            
            response["note"] = (
                f"Found {len(thoughts_with_ids)} thoughts with IDs and "
                f"{len(thoughts_without_ids)} name matches without IDs ({names_str}). "
                "Name-only matches indicate thoughts that exist but can't be directly accessed via API."
            )
        else:
            response["note"] = (
                f"Found {len(thoughts_with_ids)} thoughts and "
                f"{len(attachments)} attachments."
            )
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_thought_graph(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get a thought with all its connections and attachments - uses local DB when available."""
    # Try to use hybrid graph first (local database)
    try:
        from .hybrid_search import get_thought_graph_hybrid
        return await get_thought_graph_hybrid(api, args)
    except (ImportError, Exception):
        # Fall back to API-only if hybrid not available
        pass
    
    # Original API-based implementation as fallback
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        include_siblings = args.get("includeSiblings", False)
        
        graph = await api.get_thought_graph(brain_id, thought_id, include_siblings)
        
        # Process graph data - API returns activeThought and connections at root level
        central_thought = graph.get("activeThought", graph.get("centralThought", {}))
        
        # Ensure the central thought has both id and thoughtId
        if central_thought:
            if not central_thought.get("thoughtId"):
                central_thought["thoughtId"] = central_thought.get("id", thought_id)
            if not central_thought.get("id"):
                central_thought["id"] = central_thought.get("thoughtId", thought_id)
        
        # Organize connections by type and ensure all have IDs
        def ensure_ids(thoughts_list):
            """Ensure all thoughts in the list have both id and thoughtId fields."""
            if not thoughts_list:
                return []
            processed = []
            for thought in thoughts_list:
                if thought:
                    # Ensure both id and thoughtId are present
                    if "id" in thought:
                        thought["thoughtId"] = thought.get("thoughtId", thought["id"])
                    elif "thoughtId" in thought:
                        thought["id"] = thought["thoughtId"]
                    processed.append(thought)
            return processed
        
        # Get connections - API returns them at root level, not under connectedThoughts
        parents = ensure_ids(graph.get("parents", []))
        children = ensure_ids(graph.get("children", []))
        jumps = ensure_ids(graph.get("jumps", []))
        siblings = ensure_ids(graph.get("siblings", [])) if include_siblings else []
        
        # Also get tags if available
        tags = graph.get("tags", [])
        
        return {
            "success": True,
            "graph": {
                "centralThought": central_thought,
                "connections": {
                    "parents": parents,
                    "children": children,
                    "jumps": jumps,
                    "siblings": siblings,
                },
                "links": graph.get("links", []),
                "attachments": graph.get("attachments", []),
                "notes": graph.get("notes", []),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_types(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get all thought types in a brain."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        types = await api.get_types(brain_id)
        
        return {
            "success": True,
            "types": types,
            "count": len(types) if types else 0,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_tags(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get all tags in a brain."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        tags = await api.get_tags(brain_id)
        
        return {
            "success": True,
            "tags": tags,
            "count": len(tags) if tags else 0,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
