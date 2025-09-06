"""
Thought operation handlers for TheBrain MCP server.
"""

from typing import Dict, Any, Optional


async def list_brains(api) -> Dict[str, Any]:
    """List all available brains for the user."""
    try:
        brains = await api.list_brains()
        return {
            "success": True,
            "brains": [
                {
                    "id": brain.get("id"),
                    "name": brain.get("name"),
                    "homeThoughtId": brain.get("homeThoughtId"),
                }
                for brain in brains
            ],
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
        
        # Process search results
        thoughts = []
        for result in results:
            thoughts.append({
                "id": result.get("id"),
                "brainId": result.get("brainId"),
                "name": result.get("name"),
                "label": result.get("label"),
                "kind": result.get("kind"),
                "creationDateTime": result.get("creationDateTime"),
                "modificationDateTime": result.get("modificationDateTime"),
                "matchType": result.get("matchType"),
                "score": result.get("score"),
            })
        
        return {
            "success": True,
            "results": thoughts,
            "count": len(thoughts),
            "query": query_text,
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
        
        # Process graph data
        central_thought = graph.get("centralThought", {})
        connected_thoughts = graph.get("connectedThoughts", {})
        
        # Organize connections by type
        parents = connected_thoughts.get("parents", [])
        children = connected_thoughts.get("children", [])
        jumps = connected_thoughts.get("jumps", [])
        siblings = connected_thoughts.get("siblings", []) if include_siblings else []
        
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
