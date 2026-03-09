"""
TheBrain REST API client with retries, throttling, and typed errors.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from thebrain_mcp._throttle import RequestThrottle
from thebrain_mcp.exceptions import (
    TheBrainAPIError,
    TheBrainAuthError,
    TheBrainNotFoundError,
    TheBrainRateLimitError,
)

logger = logging.getLogger(__name__)


def _wrap_http_error(e: httpx.HTTPStatusError) -> TheBrainAPIError:
    """Map HTTP errors to domain exceptions."""
    status = e.response.status_code
    try:
        body = e.response.text or ""
    except Exception:
        body = ""
    msg = f"HTTP {status}: {e.response.reason_phrase}"
    if body:
        msg += f" - {body[:200]}"
    if status == 401:
        return TheBrainAuthError(msg)
    if status == 404:
        return TheBrainNotFoundError(msg)
    if status == 429:
        return TheBrainRateLimitError(msg)
    return TheBrainAPIError(msg)


class TheBrainAPIClient:
    """Async client for TheBrain REST API with throttling and retries."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.bra.in",
        throttle: Optional[RequestThrottle] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self._client = httpx.AsyncClient(timeout=timeout)
        self._throttle = throttle or RequestThrottle(max_concurrent=3, min_interval_seconds=0.25)

    async def close(self) -> None:
        await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TransportError, TheBrainRateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], bytes, str, None]:
        """Make an HTTP request with throttling and retries."""
        url = f"{self.base_url}{endpoint}"
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)

        kwargs: Dict[str, Any] = {"method": method, "url": url, "headers": request_headers}
        if json_data is not None:
            kwargs["json"] = json_data
        if files is not None:
            kwargs["files"] = files
            request_headers.pop("Content-Type", None)
        if params:
            kwargs["params"] = params

        async with self._throttle:
            start = time.monotonic()
            try:
                response = await self._client.request(**kwargs)
                elapsed_ms = (time.monotonic() - start) * 1000
                logger.debug("API %s %s %s ms", method, endpoint, round(elapsed_ms, 1))
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise _wrap_http_error(e)
            except httpx.HTTPError as e:
                raise TheBrainAPIError(str(e)) from e

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        if method == "DELETE" or response.status_code == 204:
            return {"success": True}
        if "/file-content" in endpoint:
            return response.content
        return response.text

    # Brain Management
    async def list_brains(self) -> List[Dict[str, Any]]:
        data = await self.request("GET", "/brains")
        return data if isinstance(data, list) else []

    async def get_brain(self, brain_id: str) -> Dict[str, Any]:
        return await self.request("GET", f"/brains/{brain_id}")

    async def get_brain_stats(self, brain_id: str) -> Dict[str, Any]:
        return await self.request("GET", f"/brains/{brain_id}/statistics")

    async def get_brain_modifications(
        self,
        brain_id: str,
        max_logs: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if max_logs is not None:
            params["maxLogs"] = max_logs
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        data = await self.request("GET", f"/brains/{brain_id}/modifications", params=params or None)
        return data if isinstance(data, list) else []

    # Thought Operations
    async def create_thought(self, brain_id: str, thought_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("POST", f"/thoughts/{brain_id}", json_data=thought_data)

    async def get_thought(self, brain_id: str, thought_id: str) -> Dict[str, Any]:
        return await self.request("GET", f"/thoughts/{brain_id}/{thought_id}")

    async def update_thought(
        self, brain_id: str, thought_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        patches = [
            {"op": "replace", "path": f"/{key}", "value": value}
            for key, value in updates.items()
            if value is not None
        ]
        return await self.request(
            "PATCH",
            f"/thoughts/{brain_id}/{thought_id}",
            json_data={"patchDocument": patches},
        )

    async def delete_thought(self, brain_id: str, thought_id: str) -> Dict[str, Any]:
        return await self.request("DELETE", f"/thoughts/{brain_id}/{thought_id}")

    async def get_thought_graph(
        self,
        brain_id: str,
        thought_id: str,
        include_siblings: bool = False,
    ) -> Dict[str, Any]:
        params = {"includeSiblings": include_siblings}
        return await self.request(
            "GET", f"/thoughts/{brain_id}/{thought_id}/graph", params=params
        )

    async def search_thoughts(
        self,
        brain_id: str,
        query_text: str,
        max_results: int = 30,
        only_search_thought_names: bool = False,
    ) -> Dict[str, Any]:
        params = {
            "queryText": query_text,
            "maxResults": max_results,
            "onlySearchThoughtNames": only_search_thought_names,
        }
        return await self.request("GET", f"/search/{brain_id}", params=params)

    async def get_types(self, brain_id: str) -> List[Dict[str, Any]]:
        data = await self.request("GET", f"/thoughts/{brain_id}/types")
        return data if isinstance(data, list) else []

    async def get_tags(self, brain_id: str) -> List[Dict[str, Any]]:
        data = await self.request("GET", f"/thoughts/{brain_id}/tags")
        return data if isinstance(data, list) else []

    # Link Operations
    async def create_link(self, brain_id: str, link_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("POST", f"/links/{brain_id}", json_data=link_data)

    async def get_link(self, brain_id: str, link_id: str) -> Dict[str, Any]:
        return await self.request("GET", f"/links/{brain_id}/{link_id}")

    async def update_link(
        self, brain_id: str, link_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        patches = [
            {"op": "replace", "path": f"/{key}", "value": value}
            for key, value in updates.items()
            if value is not None
        ]
        return await self.request(
            "PATCH",
            f"/links/{brain_id}/{link_id}",
            json_data={"patchDocument": patches},
        )

    async def delete_link(self, brain_id: str, link_id: str) -> Dict[str, Any]:
        return await self.request("DELETE", f"/links/{brain_id}/{link_id}")

    # Attachments
    async def add_file_attachment(
        self,
        brain_id: str,
        thought_id: str,
        file_path: str,
        file_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise TheBrainNotFoundError(f"File not found: {file_path}")
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
        files = {
            "file": (
                file_name or path.name,
                content,
                self._get_mime_type(file_path),
            )
        }
        return await self.request(
            "POST",
            f"/attachments/{brain_id}/{thought_id}/file",
            files=files,
        )

    async def add_url_attachment(
        self,
        brain_id: str,
        thought_id: str,
        url: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"url": url}
        if name:
            params["name"] = name
        return await self.request(
            "POST",
            f"/attachments/{brain_id}/{thought_id}/url",
            params=params,
        )

    async def get_attachment(self, brain_id: str, attachment_id: str) -> Dict[str, Any]:
        return await self.request(
            "GET", f"/attachments/{brain_id}/{attachment_id}/metadata"
        )

    async def get_attachment_content(self, brain_id: str, attachment_id: str) -> bytes:
        out = await self.request(
            "GET", f"/attachments/{brain_id}/{attachment_id}/file-content"
        )
        return out if isinstance(out, bytes) else b""

    async def delete_attachment(
        self, brain_id: str, attachment_id: str
    ) -> Dict[str, Any]:
        return await self.request(
            "DELETE", f"/attachments/{brain_id}/{attachment_id}"
        )

    async def list_attachments(
        self, brain_id: str, thought_id: str
    ) -> List[Dict[str, Any]]:
        data = await self.request(
            "GET", f"/thoughts/{brain_id}/{thought_id}/attachments"
        )
        return data if isinstance(data, list) else []

    # Notes
    async def get_note(
        self,
        brain_id: str,
        thought_id: str,
        format: str = "markdown",
    ) -> str:
        if format == "html":
            endpoint = f"/notes/{brain_id}/{thought_id}/html"
        elif format == "text":
            endpoint = f"/notes/{brain_id}/{thought_id}/text"
        else:
            endpoint = f"/notes/{brain_id}/{thought_id}"
        out = await self.request("GET", endpoint)
        return out if isinstance(out, str) else str(out)

    async def create_or_update_note(
        self,
        brain_id: str,
        thought_id: str,
        markdown: str,
    ) -> Dict[str, Any]:
        return await self.request(
            "POST",
            f"/notes/{brain_id}/{thought_id}/update",
            json_data={"markdown": markdown},
        )

    async def append_to_note(
        self,
        brain_id: str,
        thought_id: str,
        markdown: str,
    ) -> Dict[str, Any]:
        return await self.request(
            "POST",
            f"/notes/{brain_id}/{thought_id}/append",
            json_data={"markdown": markdown},
        )

    def _get_mime_type(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".md": "text/markdown",
        }
        return mime_types.get(ext, "application/octet-stream")
