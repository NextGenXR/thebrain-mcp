"""
Attachment operation handlers for TheBrain MCP server.
"""

import os
import aiofiles
from pathlib import Path
from typing import Dict, Any


async def add_file_attachment(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Add a file attachment (including images) to a thought."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        file_path = args["filePath"]
        file_name = args.get("fileName")
        
        # Verify file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        stats = path.stat()
        actual_file_name = file_name or path.name
        
        await api.add_file_attachment(brain_id, thought_id, file_path, actual_file_name)
        
        return {
            "success": True,
            "message": f"File '{actual_file_name}' attached to thought {thought_id}",
            "attachment": {
                "fileName": actual_file_name,
                "filePath": file_path,
                "size": stats.st_size,
                "thoughtId": thought_id,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def add_url_attachment(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Add a URL attachment to a thought."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        url = args["url"]
        name = args.get("name")
        
        result = await api.add_url_attachment(brain_id, thought_id, url, name)
        
        return {
            "success": True,
            "message": f"URL attached to thought {thought_id}",
            "attachment": {
                "url": url,
                "name": name or url,
                "thoughtId": thought_id,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_attachment(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get metadata about an attachment."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        attachment_id = args["attachmentId"]
        attachment = await api.get_attachment(brain_id, attachment_id)
        
        return {
            "success": True,
            "attachment": attachment,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def get_attachment_content(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get the binary content of an attachment."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        attachment_id = args["attachmentId"]
        save_to_path = args.get("saveToPath")
        
        content = await api.get_attachment_content(brain_id, attachment_id)
        
        # Save to file if path provided
        if save_to_path:
            async with aiofiles.open(save_to_path, 'wb') as f:
                await f.write(content)
            
            return {
                "success": True,
                "message": f"Attachment content saved to {save_to_path}",
                "savedTo": save_to_path,
                "size": len(content),
            }
        else:
            # Return base64 encoded content for display
            import base64
            encoded_content = base64.b64encode(content).decode('utf-8')
            
            return {
                "success": True,
                "content": encoded_content,
                "size": len(content),
                "encoding": "base64",
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def delete_attachment(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """Delete an attachment."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        attachment_id = args["attachmentId"]
        await api.delete_attachment(brain_id, attachment_id)
        
        return {
            "success": True,
            "message": f"Attachment {attachment_id} deleted successfully",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def list_attachments(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """List all attachments for a thought."""
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_id = args["thoughtId"]
        attachments = await api.list_attachments(brain_id, thought_id)
        
        # Process attachment list
        processed_attachments = []
        for att in attachments:
            processed_attachments.append({
                "id": att.get("id"),
                "name": att.get("name"),
                "type": att.get("type"),  # file, url, etc.
                "sourceId": att.get("sourceId"),
                "location": att.get("location"),
                "size": att.get("size"),
                "creationDateTime": att.get("creationDateTime"),
                "modificationDateTime": att.get("modificationDateTime"),
            })
        
        return {
            "success": True,
            "attachments": processed_attachments,
            "count": len(processed_attachments),
            "thoughtId": thought_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
