"""
Note operation handlers for TheBrain MCP server.
"""

from typing import Dict, Any
from ..markdown_formatter import format_markdown_for_thebrain


async def get_note(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get the note content for a thought."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        format_type = args.get("format", "markdown")
        
        note = await api.get_note(brain_id, thought_id, format_type)
        
        # Handle different response types
        if isinstance(note, str):
            content = note
            note_data = {
                "brainId": brain_id,
                "thoughtId": thought_id,
                "format": format_type,
                "content": content,
            }
        else:
            # If it's a dict response with metadata
            content = note.get(format_type) or note.get("markdown") or note.get("text") or ""
            note_data = {
                "brainId": note.get("brainId", brain_id),
                "thoughtId": note.get("sourceId", thought_id),
                "format": format_type,
                "content": content,
                "modificationDateTime": note.get("modificationDateTime"),
            }
        
        return {
            "success": True,
            "note": note_data,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def create_or_update_note(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update a note with markdown content."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        markdown = args["markdown"]
        
        # Format markdown for proper rendering in TheBrain
        formatted_markdown = format_markdown_for_thebrain(markdown)
        
        await api.create_or_update_note(brain_id, thought_id, formatted_markdown)
        
        return {
            "success": True,
            "message": f"Note for thought {thought_id} updated successfully",
            "thoughtId": thought_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def append_to_note(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Append content to an existing note."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        markdown = args["markdown"]
        
        # Format markdown for proper rendering in TheBrain
        formatted_markdown = format_markdown_for_thebrain(markdown)
        
        await api.append_to_note(brain_id, thought_id, formatted_markdown)
        
        return {
            "success": True,
            "message": f"Content appended to note for thought {thought_id}",
            "thoughtId": thought_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
