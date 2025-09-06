# Connecting to TheBrain MCP Server

This guide explains how to connect various applications to your TheBrain MCP server.

## Running the Server

### Option 1: Using UV (Recommended)
```bash
cd python
# Windows
C:\Users\joconnor\.local\bin\uv.exe run python main.py

# Or use the convenience script
run-uv.bat
```

### Option 2: Using activated virtual environment
```bash
cd python
.venv\Scripts\activate  # Windows
python main.py
```

## Connecting from Claude Desktop

### 1. Locate your Claude Desktop configuration file

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
Typically: `C:\Users\[YourUsername]\AppData\Roaming\Claude\claude_desktop_config.json`

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Configure the MCP Server

Edit the configuration file and add your TheBrain MCP server:

```json
{
  "mcpServers": {
    "thebrain": {
      "command": "C:\\Users\\joconnor\\.local\\bin\\uv.exe",
      "args": ["run", "python", "C:\\Git\\thebrain-mcp\\python\\main.py"],
      "cwd": "C:\\Git\\thebrain-mcp\\python",
      "env": {
        "THEBRAIN_API_KEY": "your_actual_api_key_here",
        "THEBRAIN_DEFAULT_BRAIN_ID": "optional_brain_id"
      }
    }
  }
}
```

**Alternative configuration using Python directly:**
```json
{
  "mcpServers": {
    "thebrain": {
      "command": "C:\\Git\\thebrain-mcp\\python\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Git\\thebrain-mcp\\python\\main.py"],
      "env": {
        "THEBRAIN_API_KEY": "your_actual_api_key_here",
        "THEBRAIN_DEFAULT_BRAIN_ID": "optional_brain_id"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After saving the configuration:
1. Completely quit Claude Desktop (check system tray)
2. Start Claude Desktop again
3. The TheBrain tools should now be available

### 4. Verify Connection

In Claude Desktop, you can verify the connection by:
1. Starting a new conversation
2. Asking Claude to list available TheBrain tools
3. Or directly asking to "list my brains" which will use the `list_brains` tool

## Connecting from Other MCP-Compatible Applications

### Using stdio (Standard Input/Output)

The TheBrain MCP server communicates via stdio, making it compatible with any MCP client that supports stdio transport.

**Generic configuration structure:**
```json
{
  "servers": {
    "thebrain": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "/path/to/main.py"],
      "cwd": "/path/to/python",
      "env": {
        "THEBRAIN_API_KEY": "your_api_key"
      }
    }
  }
}
```

### Using as a Library

You can also import and use the server programmatically:

```python
import asyncio
from src.api_client import TheBrainAPI
from src import handlers

async def main():
    api = TheBrainAPI("your_api_key")
    
    # List brains
    result = await handlers.list_brains(api)
    print(result)
    
    # Create a thought
    result = await handlers.create_thought(api, {
        "brainId": "your_brain_id",
        "name": "Test Thought"
    })
    print(result)
    
    await api.close()

asyncio.run(main())
```

## Environment Variables

The server respects these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `THEBRAIN_API_KEY` | Yes | Your TheBrain API key |
| `THEBRAIN_DEFAULT_BRAIN_ID` | No | Default brain to use if not specified in tool calls |

You can set these in:
1. The `.env` file in the python directory
2. Your system environment variables
3. The MCP client configuration (recommended for security)

## Troubleshooting

### Server won't start
- Check that Python 3.10+ is installed
- Verify all dependencies are installed: `uv pip list`
- Check the .env file exists and has valid API key

### Claude Desktop doesn't see the tools
- Ensure Claude Desktop is completely restarted
- Check the config file JSON syntax is valid
- Verify the file paths in the config are correct
- Check Claude's developer console for errors (if available)

### API errors
- Verify your API key is correct
- Check you have internet connectivity
- Ensure your TheBrain account has API access enabled

### Testing the server standalone

You can test the server is working by running it directly and checking the output:
```bash
uv run python main.py
```

You should see: `TheBrain MCP server started`

The server will wait for input on stdin. You can press Ctrl+C to stop it.

## Available Tools

Once connected, these tools will be available:

**Brain Management:**
- `list_brains` - List all your brains
- `get_brain` - Get brain details
- `set_active_brain` - Set default brain

**Thought Operations:**
- `create_thought` - Create new thoughts
- `get_thought` - Retrieve thought details
- `update_thought` - Modify thoughts
- `delete_thought` - Remove thoughts
- `search_thoughts` - Search across thoughts
- `get_thought_graph` - Get thought connections

**Link Operations:**
- `create_link` - Connect thoughts
- `update_link` - Modify connections
- `delete_link` - Remove connections

**Attachments:**
- `add_file_attachment` - Attach files
- `add_url_attachment` - Attach URLs
- `get_attachment_content` - Download attachments

**Notes:**
- `get_note` - Read notes
- `create_or_update_note` - Write notes
- `append_to_note` - Add to existing notes

**Advanced:**
- `get_types` - List thought types
- `get_tags` - List tags
- `get_brain_stats` - Get statistics
- `get_modifications` - View history
