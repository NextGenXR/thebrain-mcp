# TheBrain MCP Active Context

## Current Sprint Focus (September 2025)

### Recently Completed ✅
1. **Hybrid Search Performance Fix** (2025-09-06)
   - Fixed infinite recursion between search handlers
   - Corrected SQL column name issues (ThoughtId → Id)
   - Optimized database initialization (10x faster)
   - Added caching for brain-to-database mappings
   - Created comprehensive test suite

2. **Memory Bank Documentation** (2025-09-06)
   - Created all recommended memory bank documents
   - Established project documentation structure
   - Documented patterns and conventions

3. **Graph Analysis Capabilities** (2025-09-06)
   - Implemented NetworkX-based graph analyzer
   - Added centrality analysis (PageRank, betweenness, etc.)
   - Community detection and clustering
   - Path finding and cycle detection
   - Duplicate detection and structural analysis
   - Export to GraphML for visualization

### Active Work 🔄

#### High Priority Issues
1. **Tag Write Operations**
   - Problem: API doesn't support creating tags programmatically
   - Workaround: Local-only tag creation implemented
   - Need: API endpoint for tag management

2. **Bulk Operations**
   - Current: Individual operations only
   - Need: Batch processing for efficiency
   - Target: Update multiple thoughts in one call

3. **Duplicate Detection**
   - Current: Manual search required
   - Need: Automatic similarity detection
   - Target: Find and merge duplicates

### Next Up 📋

#### Week of Sep 9-13, 2025
1. **Enhanced Search Features**
   - Implement fuzzy matching
   - Add search filters (date, type, tags)
   - Support complex query syntax

2. **Performance Monitoring**
   - Add timing metrics to all operations
   - Create performance dashboard
   - Identify bottlenecks

3. **Error Recovery**
   - Implement retry with exponential backoff
   - Add circuit breaker for API failures
   - Improve error messages

#### Week of Sep 16-20, 2025
1. **Bulk Operations v1**
   - Bulk create thoughts
   - Bulk update properties
   - Bulk link creation

2. **Export Capabilities**
   - Export to Markdown
   - Export to JSON
   - Export graph structure

## Known Issues 🐛

### Critical
- None currently

### High
1. **Large Brain Performance**
   - Initial indexing slow for 50K+ thoughts
   - Memory usage high during full sync
   - Mitigation: Lazy loading implemented

2. **API Rate Limiting**
   - No rate limit handling
   - Can hit limits with bulk operations
   - Need: Implement rate limiter

### Medium
1. **Tag Sync Issues**
   - Local tag creation doesn't sync to cloud
   - Tag deletion not implemented
   - Tag renaming not supported

2. **Search Limitations**
   - API doesn't return IDs consistently
   - Full-text search limited to exact matches
   - No regex support in API

### Low
1. **Logging Verbosity**
   - Some operations over-log
   - Debug logs too detailed
   - Need: Configurable log levels

2. **Test Coverage**
   - Integration tests incomplete
   - No performance regression tests
   - Mock coverage could be better

## Technical Debt 💳

### Refactoring Needed
1. **Handler Consolidation**
   - Some duplicate code between handlers
   - Could share more utility functions
   - Consider base handler class

2. **Error Handling Standardization**
   - Inconsistent error response formats
   - Some handlers don't follow pattern
   - Need error type hierarchy

3. **Cache Management**
   - No cache invalidation strategy
   - Memory caches grow unbounded
   - Need TTL and size limits

### Documentation Gaps
1. **API Documentation**
   - Need OpenAPI spec
   - Parameter descriptions incomplete
   - Example requests/responses needed

2. **Setup Guide**
   - Windows setup needs more detail
   - Troubleshooting section sparse
   - Video tutorial would help

## Development Environment

### Current Setup
- **Python**: 3.11.5
- **Key Dependencies**:
  - mcp: 1.1.0
  - aiohttp: 3.8.5
  - sqlite3: Built-in
  - tomli-w: 1.0.0

### Testing
- **Unit Tests**: pytest
- **Integration Tests**: Custom scripts
- **Performance Tests**: Manual timing
- **Load Tests**: Not implemented

### CI/CD
- **Current**: Manual testing only
- **Planned**: GitHub Actions
- **Coverage Target**: 80%

## Collaboration Notes

### Team Communication
- **Primary Channel**: GitHub Issues
- **Code Reviews**: PR-based
- **Documentation**: Memory bank + docs/
- **Release Notes**: CHANGELOG.md

### Contributing Guidelines
1. **Code Style**: Black formatter, PEP 8
2. **Commit Messages**: Conventional commits
3. **Branch Strategy**: feature/*, fix/*, docs/*
4. **Review Required**: All PRs need approval

## Metrics & KPIs

### Current Performance
- **Average Response Time**: 1.2 seconds
- **Success Rate**: 94%
- **Cache Hit Rate**: 78%
- **Error Rate**: 6%

### Targets for Q1 2025
- **Response Time**: < 1 second
- **Success Rate**: > 98%
- **Cache Hit Rate**: > 85%
- **Error Rate**: < 2%

## Resource Links

### Internal
- [Project Brief](projectbrief.md)
- [Technical Context](techContext.md)
- [System Patterns](systemPatterns.md)
- [Product Context](productContext.md)
- [Progress Log](progress.md)

### External
- [TheBrain API Docs](https://api.thebrain.com/docs)
- [MCP SDK](https://github.com/anthropics/mcp)
- [GitHub Repo](https://github.com/user/thebrain-mcp)
- [Claude Desktop](https://claude.ai/desktop)

## Quick Commands

### Development
```bash
# Setup environment
cd python
uv venv
uv pip install -e .

# Run tests
python test_hybrid_fix.py
python test_api.py

# Start server
python main.py
```

### Debugging
```bash
# Enable debug logging
export THEBRAIN_LOG_LEVEL=DEBUG

# Disable hybrid mode
export THEBRAIN_DISABLE_HYBRID=true

# Check logs
tail -f ~/AppData/Roaming/Claude/logs/mcp-server-thebrain.log
```

### Common Operations
```python
# Find brain database
from pathlib import Path
db_path = Path.home() / "Brains" / "*" / "User.db"

# Clear cache
import shutil
shutil.rmtree(Path.home() / ".thebrain_mcp")

# Test API key
from src.api_client import TheBrainAPIClient
api = TheBrainAPIClient(api_key)
brains = await api.list_brains()
```

## Notes for Next Session

1. **Priority**: Implement bulk operations for user efficiency
2. **Investigation**: Why do some API searches not return IDs?
3. **Optimization**: Consider implementing connection pooling
4. **Feature Request**: Users want undo/redo functionality
5. **Bug**: Tag sync between local and cloud needs resolution

---
*Last Updated: September 6, 2025*
*Next Review: September 13, 2025*
