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
    """Search for thoughts in a brain."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        query_text = args["queryText"]
        max_results = args.get("maxResults", 30)
        only_search_thought_names = args.get("onlySearchThoughtNames", False)
        
        results = await api.search_thoughts(
            brain_id, query_text, max_results, only_search_thought_names
        )
        
        # Debug logging (can be enabled if needed)
        # import sys
        # print(f"[DEBUG] Search query: '{query_text}', onlyNames={only_search_thought_names}, results={len(results) if results else 0}", file=sys.stderr)
        
        # Process search results - handle both thoughts and attachments
        thoughts = []
        attachments = []
        notes = []
        
        for result in results:
            # Check the search result type and entity type
            # searchResultType: 1=Thought, 2=Note?, 3=Link?, 4=Attachment
            # entityType: 1=?, 2=Thought, 3=?, 4=Attachment
            result_type = result.get("searchResultType", 1)
            entity_type = result.get("entityType")
            
            if result_type == 4 or entity_type == 4:
                # This is an attachment result
                attachment_id = result.get("attachmentId")
                source_id = result.get("sourceId")  # Parent thought ID
                
                attachments.append({
                    "attachmentId": attachment_id,
                    "thoughtId": source_id,  # Parent thought
                    "name": result.get("name"),
                    "sourceType": result.get("sourceType"),  # 1=File, 2=URL
                    "brainId": result.get("brainId") or brain_id,
                    "brainName": result.get("brainName"),
                    "type": "attachment",
                })
            elif entity_type == 2 or result_type == 1:
                # This is likely a thought result
                thought_id = result.get("id") or result.get("thoughtId")
                thought_name = result.get("name")
                
                # For entity_type=2 results, generate a placeholder ID if missing
                if not thought_id and thought_name:
                    # This is a thought found by name but without ID in search results
                    # print(f"[INFO] Found thought by name without ID: {thought_name}", file=sys.stderr)
                    thought_id = f"name:{thought_name}"  # Placeholder to indicate name-based result
                
                if thought_id:
                    thoughts.append({
                        "id": thought_id,
                        "thoughtId": thought_id,  # Include both for compatibility
                        "brainId": result.get("brainId") or brain_id,
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
                        "type": "thought",
                        "needsIdLookup": thought_id.startswith("name:"),  # Flag for name-only results
                    })
            else:
                # Unknown type - log for debugging
                # print(f"[DEBUG] Unknown result type: searchType={result_type}, entityType={entity_type}, result={result}", file=sys.stderr)
                pass
        
        # Combine results with clear labeling
        all_results = thoughts + attachments
        
        # Special handling: If searching for exact name and no thoughts found, try graph navigation
        if len(thoughts) == 0 and only_search_thought_names:
            # print(f"[INFO] No thoughts found with search, trying graph navigation for: {query_text}", file=sys.stderr)
            found_thought = await find_thought_by_name(api, brain_id, query_text)
            if found_thought:
                # print(f"[INFO] Found thought via graph: {found_thought.get('name')} (ID: {found_thought.get('id')})", file=sys.stderr)
                # Add both id and thoughtId for compatibility
                if "id" in found_thought:
                    found_thought["thoughtId"] = found_thought.get("thoughtId", found_thought["id"])
                thoughts.append({
                    **found_thought,
                    "type": "thought",
                    "foundViaGraph": True,
                })
                all_results = thoughts + attachments
        
        # Also try to resolve thoughts that need ID lookup
        for i, thought in enumerate(thoughts):
            if thought.get("needsIdLookup") and thought.get("name"):
                # Try to find the real thought ID through graph search
                found_thought = await find_thought_by_name(api, brain_id, thought.get("name"))
                if found_thought and found_thought.get("id"):
                    # Replace the placeholder with the real thought
                    thoughts[i] = {
                        **found_thought,
                        "type": "thought",
                        "foundViaGraph": True,
                        "resolvedFromPlaceholder": True,
                    }
                    # Ensure both id and thoughtId are present
                    if "id" in thoughts[i]:
                        thoughts[i]["thoughtId"] = thoughts[i].get("thoughtId", thoughts[i]["id"])
        
        # Rebuild all_results after potential updates
        all_results = thoughts + attachments
        
        return {
            "success": True,
            "results": all_results,  # Mixed results
            "thoughts": thoughts,     # Just thoughts with IDs
            "attachments": attachments,  # Just attachments
            "count": len(all_results),
            "thoughtCount": len(thoughts),
            "attachmentCount": len(attachments),
            "query": query_text,
            "note": f"Found {len(thoughts)} thoughts and {len(attachments)} attachments. Use 'thoughts' array for items with thought IDs.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_thought_graph(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get a thought with all its connections and attachments."""
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
