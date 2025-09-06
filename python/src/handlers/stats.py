"""
Statistics and modification handlers for TheBrain MCP server.
"""

from typing import Dict, Any, Optional


def format_bytes(size_bytes: Optional[int]) -> str:
    """Format bytes to human readable string."""
    if size_bytes is None or size_bytes == 0:
        return "0 B"
    
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


async def get_brain_stats(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get statistics about a brain."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        stats = await api.get_brain_stats(brain_id)
        
        return {
            "success": True,
            "stats": {
                "brainName": stats.get("brainName"),
                "brainId": stats.get("brainId"),
                "dateGenerated": stats.get("dateGenerated"),
                "thoughts": stats.get("thoughts"),
                "forgottenThoughts": stats.get("forgottenThoughts"),
                "links": stats.get("links"),
                "linksPerThought": stats.get("linksPerThought"),
                "thoughtTypes": stats.get("thoughtTypes"),
                "linkTypes": stats.get("linkTypes"),
                "tags": stats.get("tags"),
                "notes": stats.get("notes"),
                "attachments": {
                    "internalFiles": stats.get("internalFiles"),
                    "internalFolders": stats.get("internalFolders"),
                    "externalFiles": stats.get("externalFiles"),
                    "externalFolders": stats.get("externalFolders"),
                    "webLinks": stats.get("webLinks"),
                    "totalInternalSize": format_bytes(stats.get("internalFilesSize")),
                    "totalIconSize": format_bytes(stats.get("iconsFilesSize")),
                },
                "visual": {
                    "assignedIcons": stats.get("assignedIcons"),
                },
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_modifications(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get modification history for a brain."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        max_logs = args.get("maxLogs", 100)
        start_time = args.get("startTime")
        end_time = args.get("endTime")
        
        mods = await api.get_brain_modifications(
            brain_id,
            max_logs=max_logs,
            start_time=start_time,
            end_time=end_time
        )
        
        # Process modifications
        modifications = []
        if isinstance(mods, list):
            for mod in mods:
                modifications.append({
                    "id": mod.get("id"),
                    "dateTime": mod.get("dateTime"),
                    "type": mod.get("type"),
                    "action": mod.get("action"),
                    "thoughtId": mod.get("thoughtId"),
                    "thoughtName": mod.get("thoughtName"),
                    "details": mod.get("details"),
                })
        
        return {
            "success": True,
            "modifications": modifications,
            "count": len(modifications),
            "query": {
                "brainId": brain_id,
                "maxLogs": max_logs,
                "startTime": start_time,
                "endTime": end_time,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
