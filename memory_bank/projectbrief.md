# TheBrain MCP Project Brief

## Project Overview
TheBrain MCP (Model Context Protocol) Server is a bridge that enables AI assistants like Claude to interact with TheBrain knowledge management software. It provides comprehensive API access to thoughts, links, tags, notes, and attachments within TheBrain's knowledge graphs.

## Core Mission
Enable seamless AI-powered knowledge exploration and management within TheBrain by providing:
- Full read/write access to TheBrain data structures
- Hybrid local/cloud architecture for optimal performance
- Rich search and navigation capabilities
- Automatic formatting and organization features

## Key Goals
1. **Complete API Coverage** - Expose all TheBrain functionality through MCP tools
2. **Performance Optimization** - Use local databases when available for fast access
3. **Reliability** - Graceful fallbacks and error handling
4. **User Experience** - Intuitive tool names and clear responses
5. **Maintainability** - Clean architecture with proper separation of concerns

## Target Users
- Knowledge workers using TheBrain for personal knowledge management
- Researchers organizing complex information networks
- Teams collaborating on shared brain databases
- AI enthusiasts integrating Claude with their knowledge bases

## Success Metrics
- Response time < 2 seconds for most operations
- Support for all major TheBrain features
- Zero data loss or corruption
- Seamless switching between local and cloud modes
- Clear error messages and recovery paths

## Project Status
- ✅ Core API functionality implemented
- ✅ Hybrid local/cloud architecture working
- ✅ Search and navigation tools complete
- ✅ Performance optimizations applied
- 🔄 Continuous improvements ongoing

## Technology Stack
- **Language**: Python 3.8+
- **Frameworks**: MCP SDK, asyncio
- **Database**: SQLite (local cache)
- **API**: TheBrain REST API
- **Protocols**: JSON-RPC over stdio

## Repository Structure
```
thebrain-mcp/
├── python/           # Python implementation
├── src/              # JavaScript implementation (legacy)
├── memory_bank/      # Working notes and context
├── docs/             # Formal documentation
└── tests/            # Test suites
```
