# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-01-20

### Fixed
- **Markdown Formatting**: Fixed issue where bullet points were rendering as checkboxes in TheBrain
  - Regular bullet points (`*`, `-`, `+`) now render correctly as bullets using `•` character
  - Actual checkboxes (`- [ ]`, `- [x]`) are preserved when intentional
  - Unicode checkmarks (✅, ✓) are converted to safe format `[✓]`
  - Nested lists maintain proper indentation
  - All other markdown formatting (headers, bold, italic, etc.) is preserved

- **Search Results**: Fixed issue where search results showed "placeholder thoughts that need ID lookup"
  - Improved ID extraction from search results (checks multiple possible ID fields)
  - Better categorization of thoughts with IDs vs name-only matches
  - Added automatic retry with exact name search for better ID resolution
  - Clear response format distinguishing accessible thoughts from name-only matches
  - More informative error messages explaining why some thoughts can't be accessed

### Added
- **Markdown Formatter Module**: New `src/markdown_formatter.py` module
  - `TheBrainMarkdownFormatter` class for handling markdown conversions
  - Automatic formatting applied to `create_or_update_note` and `append_to_note` operations
  - Transparent to API users - no code changes required

- **Automatic Hybrid Local/Cloud Architecture**: Intelligent zero-configuration system
  - **Automatic Detection**: Standard functions now automatically use local DB when available
  - **Zero Configuration**: No need to call special "_hybrid" functions
  - **Smart Discovery**: Automatically finds Brain databases in `~/Brains/` directory
  - **Multi-Brain Support**: Checks all U00, U01, etc. subdirectories automatically
  - **Bandwidth Efficient**: Only downloads from cloud if brain not found locally
  - **Complete Results**: All thought IDs work (no more placeholders!)
  - **Enhanced Search Syntax**:
    - `tag:TagName` - Tag search that actually works!
    - `type:TypeName` - Filter by thought type
    - `recent:7` - Get modifications from last 7 days
    - Full-text search in notes with `searchInNotes` option
  
- **Automatic Function Upgrades** (no code changes needed!):
  - `search_thoughts` - Now automatically uses local DB for complete results
  - `get_thought_graph` - Automatically returns full relationships with tags
  - `get_brain_stats` - Automatically provides comprehensive statistics
  
- **New Specialized Tools**:
  - `get_tagged_thoughts` - Direct tag search (returns all thoughts with a tag)
  - `sync_brain_data` - Manual sync control between local and cloud

## [1.1.0] - 2025-06-18

### 🎉 Major Fixes - JSON Patch Format Resolution

#### Fixed
- **Critical Bug**: Fixed JSON Patch format for update operations
  - `update_thought` no longer returns "patchDocument field required" error
  - `update_link` no longer returns "patchDocument field required" error
  - Root cause: TheBrain API expects `{"patchDocument": [...]}` structure, not direct patch array

#### Enhanced  
- **Full-Featured Create Operations**: 
  - `create_thought` now works with all visual properties (backgroundColor, foregroundColor, etc.)
  - `create_link` now works with all visual properties (color, thickness, direction, etc.)
  - Both functions use two-step process: create basic object, then apply visual properties via update

#### Technical Details
- **API Integration**: Fixed request body format in `src/api-client.js`
- **Before**: `body: [patch_operations]` 
- **After**: `body: { "patchDocument": [patch_operations] }`
- **Content-Type**: Removed incorrect `application/json-patch+json`, now uses standard `application/json`

#### Testing
- ✅ Comprehensive test suite confirms all update operations working
- ✅ Full-featured create operations tested with visual properties
- ✅ All previously broken functionality now operational

#### Commits
- `8907035` - Fix JSON Patch format for update operations
- `1d127b2` - Fix critical bug: Authorization header was being overwritten by custom headers  
- `e479f88` - Fix MCP tool result format - use direct string in text field, not nested object

## [1.0.0] - 2025-04-07

### Added
- **Initial Implementation**: Complete TheBrain MCP server
- **Brain Management**: List, get, set active brain, statistics
- **Thought Operations**: Create, read, update, delete with visual properties
- **Link Operations**: Create styled links with colors, thickness, direction
- **Attachment Management**: File uploads, URL attachments, content retrieval
- **Note Operations**: Markdown support, HTML export, append functionality
- **Search**: Full-text search across thoughts, notes, attachments
- **Visual Features**: 
  - Thought colors (foreground/background)
  - Link styling (color, thickness, direction)
  - Thought kinds and types
  - Rich formatting support

### Technical Implementation
- **MCP Protocol**: Full compliance with Model Context Protocol
- **REST API**: Complete TheBrain API integration
- **File Handling**: Multipart form data for uploads
- **Error Handling**: Comprehensive error messages
- **Modular Architecture**: Separated handlers for each feature domain

### Documentation
- **README**: Comprehensive usage guide with examples
- **API Reference**: Complete tool documentation
- **Visual Property Guide**: Color codes, thickness values, direction flags
- **Usage Examples**: Mind mapping, visual content creation
