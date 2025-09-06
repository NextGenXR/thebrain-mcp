# TheBrain MCP Product Context

## User Personas

### 1. Knowledge Worker - "Sarah"
- **Role**: Research Analyst
- **Uses TheBrain for**: Organizing research, connecting ideas, tracking sources
- **Needs**: Fast search, bulk operations, markdown notes
- **Pain Points**: Manual linking, finding orphaned thoughts, organizing tags

### 2. Personal Knowledge Manager - "David"
- **Role**: Lifelong Learner
- **Uses TheBrain for**: Personal wiki, learning notes, project planning
- **Needs**: Quick capture, easy navigation, visual exploration
- **Pain Points**: Duplicate thoughts, maintaining consistency, finding old notes

### 3. Team Collaborator - "Maria"
- **Role**: Project Manager
- **Uses TheBrain for**: Shared knowledge base, team documentation
- **Needs**: Sync reliability, access control, change tracking
- **Pain Points**: Merge conflicts, permission management, bulk updates

### 4. AI Power User - "Alex"
- **Role**: Developer/Researcher
- **Uses TheBrain for**: AI-augmented thinking, automated organization
- **Needs**: API access, scripting capabilities, Claude integration
- **Pain Points**: Manual operations, limited automation, API restrictions

## Core Features

### 1. Thought Management
- **Create Thought**: Add new thoughts with automatic placement
- **Update Thought**: Modify names, labels, types, colors
- **Delete Thought**: Safe deletion with relationship cleanup
- **Find Thought**: Search by name, content, tags, or type
- **Navigate Graph**: Traverse parents, children, jumps

### 2. Relationship Management
- **Create Links**: Connect thoughts with typed relationships
- **Link Types**: Parent/Child (hierarchical), Jump (lateral)
- **Bulk Linking**: Connect multiple thoughts at once
- **Unlink**: Remove specific relationships
- **Relationship Analysis**: Find orphans, cycles, patterns

### 3. Content Management
- **Notes**: Rich text and markdown support
- **Attachments**: Files, URLs, and references
- **Tags**: Flexible categorization system
- **Types**: Thought templates and schemas
- **Search**: Full-text across all content

### 4. Organization Features
- **Activate Thought**: Set working context
- **Pin/Unpin**: Keep important thoughts visible
- **Forget/Remember**: Archive and restore
- **Reports**: Statistics, recent changes, forgotten items
- **Bulk Operations**: Mass tagging, moving, updating

### 5. AI-Enhanced Features
- **Smart Search**: Natural language queries
- **Auto-Organization**: Suggested links and hierarchy
- **Content Generation**: Note templates and summaries
- **Duplicate Detection**: Find and merge similar thoughts
- **Knowledge Gaps**: Identify missing connections

## User Workflows

### Research Workflow
1. **Capture**: Quick-add thoughts while reading
2. **Connect**: Link related concepts
3. **Annotate**: Add notes and sources
4. **Tag**: Organize by topic/project
5. **Review**: Find patterns and insights

### Learning Workflow
1. **Create Topic**: Main subject thought
2. **Add Subtopics**: Child thoughts for details
3. **Cross-Reference**: Jump links between related concepts
4. **Add Examples**: Attachments and notes
5. **Test Knowledge**: Navigate without search

### Project Management Workflow
1. **Project Root**: Main project thought
2. **Task Breakdown**: Child thoughts for tasks
3. **Resource Links**: Jump links to people/tools
4. **Status Tags**: Track progress with tags
5. **Reports**: Review recent changes

### AI-Assisted Workflow
1. **Query Claude**: "What do I know about X?"
2. **Explore Results**: Navigate suggested thoughts
3. **Fill Gaps**: "Create thoughts for missing concepts"
4. **Organize**: "Suggest better structure for this area"
5. **Generate**: "Create summary note for this topic"

## Feature Priorities

### Must Have (P0)
- ✅ List brains
- ✅ Search thoughts
- ✅ Get thought details
- ✅ Navigate relationships
- ✅ Read notes
- ✅ Basic CRUD operations

### Should Have (P1)
- ✅ Tag operations
- ✅ Type management
- ✅ Attachment handling
- ✅ Statistics/reports
- ✅ Hybrid local/cloud mode
- ⏳ Bulk operations

### Nice to Have (P2)
- ⏳ Smart suggestions
- ⏳ Duplicate detection
- ⏳ Auto-organization
- ⏳ Template support
- ⏳ Export capabilities
- ⏳ Backup/restore

### Future Vision (P3)
- 🔮 Multi-brain operations
- 🔮 Real-time collaboration
- 🔮 Version control
- 🔮 AI-powered insights
- 🔮 Custom workflows
- 🔮 Plugin system

## Success Metrics

### Performance Metrics
- **Search Speed**: < 1 second for 10K thoughts
- **Navigation**: < 500ms thought activation
- **Sync Time**: < 5 seconds for typical changes
- **Startup**: < 2 seconds to ready state

### Usability Metrics
- **Tool Discovery**: Users find needed tools quickly
- **Error Recovery**: Clear messages and next steps
- **Learning Curve**: Productive within 30 minutes
- **Completion Rate**: 90%+ operations succeed

### Adoption Metrics
- **Daily Active Users**: Growing month-over-month
- **Operations per Session**: 20+ tool calls
- **Return Rate**: 80%+ weekly retention
- **User Satisfaction**: 4.5+ star rating

## Common Use Cases

### 1. "Find Everything About X"
```
User: "Show me everything related to 'machine learning'"
System: Searches thoughts, notes, tags, and attachments
Result: Comprehensive view of all ML-related content
```

### 2. "Organize This Mess"
```
User: "Find duplicate thoughts about Python"
System: Identifies similar thoughts by name/content
Result: List of potential duplicates to merge
```

### 3. "What Did I Work on Recently?"
```
User: "Show me thoughts modified this week"
System: Queries recent modifications
Result: Chronological list with changes
```

### 4. "Connect These Ideas"
```
User: "Link all thoughts tagged 'Q4' to 'Planning'"
System: Finds tagged thoughts, creates links
Result: Bulk connection established
```

### 5. "Generate Documentation"
```
User: "Create a summary of my 'Project X' subtree"
System: Traverses hierarchy, extracts key points
Result: Markdown document with structure and notes
```

## Competitive Advantages

### vs. Traditional Note Apps
- **Non-linear structure**: Not limited to folders
- **Relationship types**: Multiple connection types
- **Visual thinking**: See connections graphically
- **AI integration**: Claude understands structure

### vs. Mind Mapping Tools
- **Unlimited depth**: No canvas limitations
- **Rich content**: Full notes and attachments
- **Persistent state**: Not session-based
- **Programmatic access**: Full API control

### vs. Wiki Systems
- **Automatic linking**: Relationships without markup
- **Multiple hierarchies**: Not just one taxonomy
- **Personal focus**: Optimized for individuals
- **Desktop integration**: Native app performance

## User Feedback Themes

### Positive Feedback
- "Finally, my AI assistant understands my brain!"
- "Search actually works now with local DB"
- "Love the tag operations - game changer"
- "Bulk operations save hours of work"

### Common Requests
- "Need better duplicate detection"
- "Want to merge brains"
- "Batch operations for large changes"
- "Export to standard formats"
- "Undo/redo functionality"

### Pain Points Addressed
- ✅ Slow search → Hybrid mode with local DB
- ✅ Missing IDs → Enhanced search with fallbacks
- ✅ Tag search broken → Direct DB queries
- ✅ No bulk operations → Batch processing support
- ⏳ Manual organization → AI suggestions (planned)
