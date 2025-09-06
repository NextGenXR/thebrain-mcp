#!/usr/bin/env python3
"""
TheBrain MCP Server for Python
Main server implementation using the MCP SDK.
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    McpError,
    ErrorCode
)

from src.api_client import TheBrainAPI
from src.tool_schemas import get_tool_schemas
from src import handlers


# Load environment variables
load_dotenv()

# Global variables
api: Optional[TheBrainAPI] = None
active_brain_id: Optional[str] = None


def format_tool_result(result: Any) -> CallToolResult:
    """
    Format tool results according to MCP protocol.
    
    Args:
        result: The result from a handler function
        
    Returns:
        Formatted CallToolResult with content array
    """
    # Convert result to string
    if isinstance(result, str):
        text_content = result
    elif result is None:
        text_content = "null"
    else:
        text_content = json.dumps(result, indent=2)
    
    # Ensure text_content is always a string
    text_content = str(text_content)
    
    return CallToolResult(
        content=[TextContent(type="text", text=text_content)]
    )


async def handle_list_tools() -> list[Tool]:
    """Return the list of available tools."""
    tool_schemas = get_tool_schemas()
    tools = []
    
    for schema in tool_schemas.values():
        tools.append(Tool(
            name=schema["name"],
            description=schema["description"],
            inputSchema=schema["inputSchema"]
        ))
    
    return tools


async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """
    Handle tool execution.
    
    Args:
        name: The name of the tool to execute
        arguments: The arguments for the tool
        
    Returns:
        Formatted tool result
    """
    global active_brain_id
    
    try:
        # Add active brain ID to args if not specified
        if active_brain_id and "brainId" not in arguments:
            arguments["brainId"] = active_brain_id
        
        result = None
        
        # Route to appropriate handler
        if name == "list_brains":
            result = await handlers.list_brains(api)
        elif name == "get_brain":
            result = await handlers.get_brain(api, arguments)
        elif name == "set_active_brain":
            result = await handlers.set_active_brain(api, arguments)
            if result.get("success"):
                active_brain_id = arguments["brainId"]
        
        # Thought Operations
        elif name == "create_thought":
            result = await handlers.create_thought(api, arguments)
        elif name == "get_thought":
            result = await handlers.get_thought(api, arguments)
        elif name == "update_thought":
            result = await handlers.update_thought(api, arguments)
        elif name == "delete_thought":
            result = await handlers.delete_thought(api, arguments)
        elif name == "search_thoughts":
            result = await handlers.search_thoughts(api, arguments)
        elif name == "get_thought_graph":
            result = await handlers.get_thought_graph(api, arguments)
        
        # Link Operations
        elif name == "create_link":
            result = await handlers.create_link(api, arguments)
        elif name == "update_link":
            result = await handlers.update_link(api, arguments)
        elif name == "get_link":
            result = await handlers.get_link(api, arguments)
        elif name == "delete_link":
            result = await handlers.delete_link(api, arguments)
        
        # Attachment Operations
        elif name == "add_file_attachment":
            result = await handlers.add_file_attachment(api, arguments)
        elif name == "add_url_attachment":
            result = await handlers.add_url_attachment(api, arguments)
        elif name == "get_attachment":
            result = await handlers.get_attachment(api, arguments)
        elif name == "get_attachment_content":
            result = await handlers.get_attachment_content(api, arguments)
        elif name == "delete_attachment":
            result = await handlers.delete_attachment(api, arguments)
        elif name == "list_attachments":
            result = await handlers.list_attachments(api, arguments)
        
        # Note Operations
        elif name == "get_note":
            result = await handlers.get_note(api, arguments)
        elif name == "create_or_update_note":
            result = await handlers.create_or_update_note(api, arguments)
        elif name == "append_to_note":
            result = await handlers.append_to_note(api, arguments)
        
        # Advanced Operations
        elif name == "get_types":
            result = await handlers.get_types(api, arguments)
        elif name == "get_tags":
            result = await handlers.get_tags(api, arguments)
        elif name == "get_brain_stats":
            result = await handlers.get_brain_stats(api, arguments)
        elif name == "get_modifications":
            result = await handlers.get_modifications(api, arguments)
        else:
            raise McpError(ErrorCode.MethodNotFound, f"Unknown tool: {name}")
        
        # Format the result according to MCP protocol
        return format_tool_result(result)
        
    except McpError:
        raise
    except Exception as e:
        print(f"Error executing tool {name}: {e}", file=sys.stderr)
        # Return error in MCP format
        return format_tool_result({
            "success": False,
            "error": str(e)
        })


async def main():
    """Main server entry point."""
    global api, active_brain_id
    
    # Validate API key
    api_key = os.getenv("THEBRAIN_API_KEY")
    if not api_key:
        print("Error: THEBRAIN_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)
    
    # Initialize API client
    api = TheBrainAPI(api_key)
    
    # Set default brain ID if provided
    active_brain_id = os.getenv("THEBRAIN_DEFAULT_BRAIN_ID")
    
    # Create and configure the server
    server = Server("thebrain-mcp")
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Handle list_tools request."""
        return await handle_list_tools()
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle call_tool request."""
        return await handle_call_tool(name, arguments)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        print("TheBrain MCP server started", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
    
    # Clean up
    await api.close()


if __name__ == "__main__":
    asyncio.run(main())
