"""
Link operation handlers for TheBrain MCP server.
"""

from typing import Dict, Any


async def create_link(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a link between two thoughts with visual properties."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        # Extract parameters
        thought_id_a = args["thoughtIdA"]
        thought_id_b = args["thoughtIdB"]
        relation = args["relation"]
        name = args.get("name")
        color = args.get("color")
        thickness = args.get("thickness")
        direction = args.get("direction")
        type_id = args.get("typeId")
        
        # Create the basic link
        link_data = {
            "thoughtIdA": thought_id_a,
            "thoughtIdB": thought_id_b,
            "relation": relation,
        }
        
        if name:
            link_data["name"] = name
        
        result = await api.create_link(brain_id, link_data)
        link_id = result.get("id")
        
        # Apply visual properties if provided
        if color or thickness is not None or direction is not None or type_id:
            updates = {}
            if color:
                updates["color"] = color
            if thickness is not None:
                updates["thickness"] = thickness
            if direction is not None:
                updates["direction"] = direction
            if type_id:
                updates["typeId"] = type_id
            
            await api.update_link(brain_id, link_id, updates)
        
        return {
            "success": True,
            "link": {
                "id": link_id,
                "brainId": brain_id,
                "thoughtIdA": thought_id_a,
                "thoughtIdB": thought_id_b,
                "relation": relation,
                "name": name,
                "color": color,
                "thickness": thickness,
                "direction": direction,
                "typeId": type_id,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def update_link(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Update link properties including visual formatting."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        link_id = args["linkId"]
        
        # Collect updates
        updates = {}
        for field in ["name", "color", "thickness", "direction", "relation"]:
            if field in args and args[field] is not None:
                updates[field] = args[field]
        
        if not updates:
            return {
                "success": True,
                "message": "No updates provided",
            }
        
        await api.update_link(brain_id, link_id, updates)
        
        return {
            "success": True,
            "link": {
                "id": link_id,
                "brainId": brain_id,
                **updates,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_link(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get details about a specific link."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        link_id = args["linkId"]
        link = await api.get_link(brain_id, link_id)
        
        return {
            "success": True,
            "link": link,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def delete_link(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a link between thoughts."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        link_id = args["linkId"]
        await api.delete_link(brain_id, link_id)
        
        return {
            "success": True,
            "message": f"Link {link_id} deleted successfully",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
