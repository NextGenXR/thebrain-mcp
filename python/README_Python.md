# TheBrain MCP Server - Python Version

A Python implementation of the Model Context Protocol (MCP) server for TheBrain API, enabling AI assistants to interact with TheBrain knowledge management system.

## Features

### Core Features
- **Brain Management**: List, access, and manage multiple brains
- **Thought Operations**: Create, update, delete, and search thoughts with visual properties
- **Link Management**: Create and manage links between thoughts with graphical properties  
- **Attachments**: Add files, images, and URLs to thoughts
- **Notes**: Create and manage markdown notes for thoughts
- **Search**: Full-text search across thoughts and notes
- **Statistics**: Get brain statistics and modification history

### Advanced Features
- **Graph Analysis**: Analyze brain structure using NetworkX to find patterns, communities, and insights
- **Local/Hybrid Mode**: Work with local SQLite database for performance and offline access
- **Path Finding**: Discover shortest paths and connections between thoughts
- **Duplicate Detection**: Find and manage duplicate thoughts
- **Community Detection**: Identify clusters of related concepts
- **Centrality Analysis**: Find the most important/connected thoughts in your brain

## Installation

### Prerequisites

- Python 3.10 or higher
- TheBrain API key (get it from your TheBrain account settings)

### Quick Setup with UV (Primary Dependency Manager)

**UV is the primary dependency management tool for this project.** [UV](https://github.com/astral-sh/uv) provides fast, reliable Python package management - it's 10-100x faster than pip and ensures consistent dependency resolution. UV will automatically handle Python installation, virtual environments, and all dependencies.

📚 **See [UV_SETUP_GUIDE.md](UV_SETUP_GUIDE.md) for comprehensive UV documentation.**

#### Windows

```bash
# Using Command Prompt
cd python
setup-uv.bat

# Or using PowerShell with enhanced output
cd python
powershell -ExecutionPolicy Bypass -File setup-uv.ps1
```

#### Linux/macOS

```bash
cd python
chmod +x setup-uv.sh
./setup-uv.sh
```

### Alternative Setup with pip

If you prefer traditional pip-based setup:

#### Windows

```bash
# Using Command Prompt or PowerShell
cd python
setup.bat

# Or using PowerShell with enhanced output
cd python
powershell -ExecutionPolicy Bypass -File setup.ps1
```

#### Linux/macOS

```bash
cd python
chmod +x setup.sh
./setup.sh
```

### Manual Installation

If you prefer to set up manually:

```bash
cd python

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Install as Package

To install the server as a Python package:

```bash
cd python
pip install -e .
```

## Configuration

1. Copy the `env.example` file to `.env`:
```bash
cp env.example .env
```

2. Edit `.env` and configure your settings:

```bash
# REQUIRED: Your TheBrain API key
THEBRAIN_API_KEY=your_api_key_here

# OPTIONAL: Default brain ID
THEBRAIN_DEFAULT_BRAIN_ID=optional_default_brain_id

# OPTIONAL: Path to local Brain database directory
# Leave empty to use default locations
# Supports environment variables and ~ expansion
THEBRAIN_LOCAL_DB_PATH=

# Examples for different platforms:
# Windows:   %USERPROFILE%\Brains
# Windows:   C:\Users\YourName\Documents\TheBrain
# macOS:     ~/Brains  
# macOS:     ~/Library/Application Support/TheBrain
# Linux:     ~/.local/share/thebrain
```

### Database Path Configuration

The server automatically searches for your Brain database in standard locations:

**Windows:**
- `%USERPROFILE%\Brains` (default)
- `%USERPROFILE%\Documents\TheBrain`
- `%APPDATA%\TheBrain\Brains`

**macOS:**
- `~/Brains` (default)
- `~/Library/Application Support/TheBrain`
- `~/Documents/TheBrain`

**Linux:**
- `~/Brains` (default)
- `~/.local/share/thebrain`
- `~/.thebrain`

If your Brain database is in a non-standard location, set `THEBRAIN_LOCAL_DB_PATH` in your `.env` file.

## Usage

### Running the MCP Server

#### Using UV run scripts (Recommended)

Windows:
```bash
cd python
run-uv.bat
```

Linux/macOS:
```bash
cd python
./run-uv.sh
```

#### Using traditional run scripts

Windows:
```bash
cd python
run.bat
```

Linux/macOS:
```bash
cd python
./run.sh
```

#### Manual run

First activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

Then run the server:
```bash
python main.py
```

Or if installed as a package:
```bash
thebrain-mcp
```

### Using with Claude Desktop

1. Edit your Claude Desktop configuration file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the TheBrain MCP server configuration:
```json
{
  "mcpServers": {
    "thebrain": {
      "command": "python",
      "args": ["C:/Git/thebrain-mcp/python/main.py"],
      "env": {
        "THEBRAIN_API_KEY": "your_api_key_here",
        "THEBRAIN_DEFAULT_BRAIN_ID": "optional_default_brain_id"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Available Tools

### Brain Management
- `list_brains` - List all available brains
- `get_brain` - Get details about a specific brain
- `set_active_brain` - Set the active brain for subsequent operations

### Thought Operations
- `create_thought` - Create a new thought with optional visual properties
- `get_thought` - Get details about a specific thought
- `update_thought` - Update a thought including its visual properties
- `delete_thought` - Delete a thought
- `search_thoughts` - Search for thoughts in a brain
- `get_thought_graph` - Get a thought with all its connections

### Link Operations
- `create_link` - Create a link between two thoughts
- `update_link` - Update link properties
- `get_link` - Get details about a specific link
- `delete_link` - Delete a link

### Attachment Operations
- `add_file_attachment` - Add a file attachment to a thought
- `add_url_attachment` - Add a URL attachment to a thought
- `get_attachment` - Get metadata about an attachment
- `get_attachment_content` - Get the binary content of an attachment
- `delete_attachment` - Delete an attachment
- `list_attachments` - List all attachments for a thought

### Note Operations
- `get_note` - Get the note content for a thought
- `create_or_update_note` - Create or update a note with markdown content
- `append_to_note` - Append content to an existing note

### Advanced Operations
- `get_types` - Get all thought types in a brain
- `get_tags` - Get all tags in a brain
- `get_brain_stats` - Get statistics about a brain
- `get_modifications` - Get modification history for a brain

## Graph Analysis with NetworkX

TheBrain's structure is fundamentally a directed graph (thoughts as nodes, links as edges). The Python version includes powerful graph analysis capabilities using NetworkX.

### Quick Start
```python
from src.graph_analyzer import BrainGraphAnalyzer

# Load your Brain database
analyzer = BrainGraphAnalyzer("C:/Users/YourName/Brains/U01/B02/Brain.db")

# Get statistics
stats = analyzer.get_statistics()
print(f"Total thoughts: {stats['basic']['total_thoughts']}")
print(f"Orphaned thoughts: {stats['orphaned_thoughts']['count']}")

# Find central thoughts
central = analyzer.find_central_thoughts(top_n=10)

# Detect communities
communities = analyzer.find_communities()
```

### Key Capabilities
- **Structure Analysis**: Understand connectivity, density, and organization
- **Path Finding**: Find shortest paths between concepts
- **Centrality Measures**: Identify important hub thoughts
- **Community Detection**: Find clusters of related concepts
- **Duplicate Detection**: Find thoughts with duplicate names
- **Cycle Detection**: Identify circular references
- **Visualization**: Export to Gephi, create interactive HTML graphs

📚 **See [Graph Analysis Guide](docs/graph-analysis-guide.md) for comprehensive documentation on using NetworkX with TheBrain.**

## Development

### Documentation

- [API Integration Guide](THEBRAIN_API_GUIDE.md) - Detailed guide on TheBrain API quirks and patterns
- [Brain Database Structure](docs/BRAIN_DATABASE_STRUCTURE.md) - Complete analysis of local SQLite database
- [Graph Analysis Guide](docs/graph-analysis-guide.md) - **Comprehensive guide to using NetworkX for brain analysis**
- [Hybrid Architecture](docs/hybrid-architecture.md) - Local/hybrid mode for performance optimization
- [Performance Optimization](memory_bank/status/PERFORMANCE_OPTIMIZATION.md) - Strategies for handling large brains  
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Client Setup Guide](docs/SETUP_CLIENT.md) - How to connect to Claude Desktop and other clients
- [API Learnings](docs/API_LEARNINGS.md) - Key discoveries about API behavior vs documentation

## Project Structure
```
python/
├── main.py                 # Main server entry point
├── pyproject.toml         # Project configuration for UV/pip
├── requirements.txt        # Python dependencies (pip)
├── setup.py               # Package setup configuration
├── README.md              # This file
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore patterns
├── test_installation.py  # Installation test script
├── setup-uv.bat          # Windows UV setup script
├── setup-uv.sh           # Unix/Linux UV setup script
├── setup-uv.ps1          # PowerShell UV setup script
├── run-uv.bat            # Windows UV run script
├── run-uv.sh             # Unix/Linux UV run script
├── setup.bat             # Windows pip setup script
├── setup.sh              # Unix/Linux pip setup script
├── setup.ps1             # PowerShell pip setup script
├── run.bat               # Windows pip run script
├── run.sh                # Unix/Linux pip run script
└── src/
    ├── __init__.py              # Package initialization
    ├── api_client.py            # TheBrain API client
    ├── graph_analyzer.py        # NetworkX-based graph analysis
    ├── hybrid_brain_manager.py  # Hybrid local/remote mode manager
    ├── local_brain_cache.py     # Local SQLite database interface
    ├── markdown_formatter.py    # Markdown formatting utilities
    ├── tool_schemas.py          # Tool schema definitions
    └── handlers/                # Tool implementation handlers
        ├── __init__.py
        ├── thoughts.py          # Thought operations
        ├── thoughts_optimized.py # Performance-optimized thought operations
        ├── links.py             # Link operations
        ├── attachments.py       # Attachment operations
        ├── notes.py             # Note operations
        ├── stats.py             # Statistics operations
        ├── graph.py             # Graph analysis handlers
        └── hybrid_search.py     # Hybrid search operations
```

### Testing

Run the installation test script to verify everything is set up correctly:
```bash
# Make sure virtual environment is activated first
python test_installation.py
```

Or run basic import tests:
```bash
python -c "from src.api_client import TheBrainAPI; print('API client imports successfully')"
python -c "from src.tool_schemas import get_tool_schemas; print(f'Found {len(get_tool_schemas())} tools')"
```

## Migration from JavaScript

This is a Python port of the original JavaScript implementation. The functionality is identical, but the implementation follows Python best practices:

- Async/await using Python's `asyncio`
- Type hints for better IDE support
- Python-style error handling
- HTTPX instead of node-fetch
- Python MCP SDK instead of JavaScript SDK
- Modern dependency management with UV (optional)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues with:
- TheBrain API: Contact TheBrain support
- MCP Server: Open an issue on GitHub
- Python implementation: Check the documentation or open an issue
