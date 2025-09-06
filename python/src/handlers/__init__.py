"""
Handler modules for TheBrain MCP server.
Export all handler functions.
"""

from .thoughts import *
from .links import *
from .attachments import *
from .notes import *
from .stats import *

# Import hybrid handlers if available
try:
    from .hybrid_search import *
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False

__all__ = [
    # Thoughts
    'list_brains',
    'get_brain',
    'set_active_brain',
    'create_thought',
    'get_thought',
    'update_thought',
    'delete_thought',
    'search_thoughts',
    'get_thought_graph',
    'get_types',
    'get_tags',
    # Links
    'create_link',
    'update_link',
    'get_link', 
    'delete_link',
    # Attachments
    'add_file_attachment',
    'add_url_attachment',
    'get_attachment',
    'get_attachment_content',
    'delete_attachment',
    'list_attachments',
    # Notes
    'get_note',
    'create_or_update_note',
    'append_to_note',
    # Stats
    'get_brain_stats',
    'get_modifications',
]

# Add specific hybrid handlers that remain as separate tools
if HYBRID_AVAILABLE:
    __all__.extend([
        'get_tagged_thoughts',
        'sync_brain_data',
    ])
