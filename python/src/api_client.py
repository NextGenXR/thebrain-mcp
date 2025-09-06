"""
TheBrain API Client for Python
Handles all API interactions with TheBrain REST API
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
import httpx
import aiofiles
from urllib.parse import urlencode


class TheBrainAPI:
    """Client for interacting with TheBrain API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.bra.in"):
        """
        Initialize TheBrain API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (defaults to production)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Union[Dict, bytes, str, None]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            json_data: JSON data for request body
            files: Files to upload
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data (JSON dict, bytes for files, or string)
        """
        url = f"{self.base_url}{endpoint}"
        
        # Merge headers
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)
        
        # Prepare request kwargs
        kwargs = {
            "method": method,
            "url": url,
            "headers": request_headers,
        }
        
        if json_data is not None:
            kwargs["json"] = json_data
        
        if files is not None:
            kwargs["files"] = files
            # Don't set Content-Type for multipart
            if "Content-Type" in request_headers:
                del request_headers["Content-Type"]
        
        if params:
            kwargs["params"] = params
        
        try:
            response = await self.client.request(**kwargs)
            response.raise_for_status()
            
            # Handle different response types
            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                return response.json()
            elif method == "DELETE" or response.status_code == 204:
                return {"success": True}
            elif "/file-content" in endpoint:
                # Return bytes for file content
                return response.content
            else:
                # Return text for other responses
                return response.text
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            try:
                error_body = e.response.text
                if error_body:
                    error_msg += f" - {error_body}"
            except:
                pass
            raise Exception(error_msg)
        except Exception as e:
            print(f"API request failed: {method} {endpoint} - {e}")
            raise
    
    # Brain Management
    async def list_brains(self) -> List[Dict]:
        """List all available brains."""
        return await self.request("GET", "/brains")
    
    async def get_brain(self, brain_id: str) -> Dict:
        """Get details about a specific brain."""
        return await self.request("GET", f"/brains/{brain_id}")
    
    async def get_brain_stats(self, brain_id: str) -> Dict:
        """Get statistics about a brain."""
        return await self.request("GET", f"/brains/{brain_id}/statistics")
    
    async def get_brain_modifications(
        self, 
        brain_id: str, 
        max_logs: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict:
        """Get modification history for a brain."""
        params = {}
        if max_logs:
            params["maxLogs"] = max_logs
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return await self.request("GET", f"/brains/{brain_id}/modifications", params=params)
    
    # Thought Operations
    async def create_thought(self, brain_id: str, thought_data: Dict) -> Dict:
        """Create a new thought."""
        return await self.request("POST", f"/thoughts/{brain_id}", json_data=thought_data)
    
    async def get_thought(self, brain_id: str, thought_id: str) -> Dict:
        """Get a specific thought."""
        return await self.request("GET", f"/thoughts/{brain_id}/{thought_id}")
    
    async def update_thought(self, brain_id: str, thought_id: str, updates: Dict) -> Dict:
        """
        Update a thought using JSON Patch.
        
        Args:
            brain_id: Brain ID
            thought_id: Thought ID to update  
            updates: Dictionary of fields to update
        """
        patches = []
        for key, value in updates.items():
            if value is not None:
                patches.append({
                    "op": "replace",
                    "path": f"/{key}",
                    "value": value
                })
        
        return await self.request(
            "PATCH",
            f"/thoughts/{brain_id}/{thought_id}",
            json_data={"patchDocument": patches}
        )
    
    async def delete_thought(self, brain_id: str, thought_id: str) -> Dict:
        """Delete a thought."""
        return await self.request("DELETE", f"/thoughts/{brain_id}/{thought_id}")
    
    async def get_thought_graph(
        self, 
        brain_id: str, 
        thought_id: str, 
        include_siblings: bool = False
    ) -> Dict:
        """Get a thought with all its connections."""
        params = {"includeSiblings": include_siblings}
        return await self.request("GET", f"/thoughts/{brain_id}/{thought_id}/graph", params=params)
    
    async def search_thoughts(
        self,
        brain_id: str,
        query_text: str,
        max_results: int = 30,
        only_search_thought_names: bool = False
    ) -> Dict:
        """Search for thoughts in a brain."""
        params = {
            "queryText": query_text,
            "maxResults": max_results,
            "onlySearchThoughtNames": only_search_thought_names
        }
        return await self.request("GET", f"/search/{brain_id}", params=params)
    
    async def get_types(self, brain_id: str) -> List[Dict]:
        """Get all thought types in a brain."""
        return await self.request("GET", f"/thoughts/{brain_id}/types")
    
    async def get_tags(self, brain_id: str) -> List[Dict]:
        """Get all tags in a brain."""
        return await self.request("GET", f"/thoughts/{brain_id}/tags")
    
    # Link Operations
    async def create_link(self, brain_id: str, link_data: Dict) -> Dict:
        """Create a link between thoughts."""
        return await self.request("POST", f"/links/{brain_id}", json_data=link_data)
    
    async def get_link(self, brain_id: str, link_id: str) -> Dict:
        """Get details about a link."""
        return await self.request("GET", f"/links/{brain_id}/{link_id}")
    
    async def update_link(self, brain_id: str, link_id: str, updates: Dict) -> Dict:
        """Update a link using JSON Patch."""
        patches = []
        for key, value in updates.items():
            if value is not None:
                patches.append({
                    "op": "replace",
                    "path": f"/{key}",
                    "value": value
                })
        
        return await self.request(
            "PATCH",
            f"/links/{brain_id}/{link_id}",
            json_data={"patchDocument": patches}
        )
    
    async def delete_link(self, brain_id: str, link_id: str) -> Dict:
        """Delete a link."""
        return await self.request("DELETE", f"/links/{brain_id}/{link_id}")
    
    # Attachment Operations
    async def add_file_attachment(
        self, 
        brain_id: str, 
        thought_id: str, 
        file_path: str,
        file_name: Optional[str] = None
    ) -> Dict:
        """
        Add a file attachment to a thought.
        
        Args:
            brain_id: Brain ID
            thought_id: Thought ID
            file_path: Path to the file to attach
            file_name: Optional custom name for the attachment
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        # Prepare multipart form data
        files = {
            'file': (
                file_name or path.name,
                content,
                self._get_mime_type(file_path)
            )
        }
        
        return await self.request(
            "POST",
            f"/attachments/{brain_id}/{thought_id}/file",
            files=files
        )
    
    async def add_url_attachment(
        self,
        brain_id: str,
        thought_id: str,
        url: str,
        name: Optional[str] = None
    ) -> Dict:
        """Add a URL attachment to a thought."""
        params = {"url": url}
        if name:
            params["name"] = name
        
        return await self.request(
            "POST",
            f"/attachments/{brain_id}/{thought_id}/url",
            params=params
        )
    
    async def get_attachment(self, brain_id: str, attachment_id: str) -> Dict:
        """Get attachment metadata."""
        return await self.request("GET", f"/attachments/{brain_id}/{attachment_id}/metadata")
    
    async def get_attachment_content(self, brain_id: str, attachment_id: str) -> bytes:
        """Get attachment file content."""
        return await self.request("GET", f"/attachments/{brain_id}/{attachment_id}/file-content")
    
    async def delete_attachment(self, brain_id: str, attachment_id: str) -> Dict:
        """Delete an attachment."""
        return await self.request("DELETE", f"/attachments/{brain_id}/{attachment_id}")
    
    async def list_attachments(self, brain_id: str, thought_id: str) -> List[Dict]:
        """List all attachments for a thought."""
        return await self.request("GET", f"/thoughts/{brain_id}/{thought_id}/attachments")
    
    # Note Operations
    async def get_note(
        self, 
        brain_id: str, 
        thought_id: str,
        format: str = "markdown"
    ) -> str:
        """
        Get note content for a thought.
        
        Args:
            brain_id: Brain ID
            thought_id: Thought ID
            format: Output format ('markdown', 'html', or 'text')
        """
        if format == "html":
            endpoint = f"/notes/{brain_id}/{thought_id}/html"
        elif format == "text":
            endpoint = f"/notes/{brain_id}/{thought_id}/text"
        else:
            endpoint = f"/notes/{brain_id}/{thought_id}"
        
        return await self.request("GET", endpoint)
    
    async def create_or_update_note(
        self,
        brain_id: str,
        thought_id: str,
        markdown: str
    ) -> Dict:
        """Create or update a note with markdown content."""
        return await self.request(
            "POST",
            f"/notes/{brain_id}/{thought_id}/update",
            json_data={"markdown": markdown}
        )
    
    async def append_to_note(
        self,
        brain_id: str,
        thought_id: str,
        markdown: str
    ) -> Dict:
        """Append content to an existing note."""
        return await self.request(
            "POST", 
            f"/notes/{brain_id}/{thought_id}/append",
            json_data={"markdown": markdown}
        )
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for a file based on extension."""
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.svg': 'image/svg+xml',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
        }
        return mime_types.get(ext, 'application/octet-stream')
