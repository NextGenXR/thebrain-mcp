"""
Markdown formatter for TheBrain API.

Handles conversion of markdown content to ensure proper rendering in TheBrain,
particularly addressing issues where bullet points are rendered as checkboxes.
"""

import re
from typing import Optional


class TheBrainMarkdownFormatter:
    """Formats markdown content for proper rendering in TheBrain."""
    
    @staticmethod
    def format_for_thebrain(markdown: str) -> str:
        """
        Format markdown content for TheBrain's renderer.
        
        TheBrain's markdown renderer can interpret certain patterns as checkboxes
        when they should be bullet points. This method ensures proper formatting.
        
        Args:
            markdown: The original markdown content
            
        Returns:
            Formatted markdown that will render correctly in TheBrain
        """
        if not markdown:
            return markdown
        
        lines = markdown.split('\n')
        formatted_lines = []
        
        for line in lines:
            formatted_line = TheBrainMarkdownFormatter._format_line(line)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _format_line(line: str) -> str:
        """
        Format a single line of markdown.
        
        Args:
            line: A single line of markdown text
            
        Returns:
            Formatted line
        """
        # Check if line starts with bullet point patterns
        # Match lines that start with *, -, or + followed by space
        bullet_pattern = r'^(\s*)([\*\-\+])\s+(.+)$'
        match = re.match(bullet_pattern, line)
        
        if match:
            indent = match.group(1)
            bullet = match.group(2)
            content = match.group(3)
            
            # Check if content starts with [ ] or [x] (checkbox pattern)
            # If it does, leave it as is (it's an intentional checkbox)
            checkbox_pattern = r'^\[[x\s]\]\s+'
            if re.match(checkbox_pattern, content, re.IGNORECASE):
                return line
            
            # Convert different bullet styles to a consistent format
            # Use bullet character (•) which TheBrain won't interpret as checkbox
            # Alternative: use a dash with non-breaking space
            formatted_bullet = "•"
            
            return f"{indent}{formatted_bullet} {content}"
        
        # Check for numbered lists (preserve as-is)
        numbered_pattern = r'^(\s*)(\d+)[\.\)]\s+(.+)$'
        if re.match(numbered_pattern, line):
            return line
        
        # Check for actual checkbox patterns and preserve them
        checkbox_line_pattern = r'^(\s*)-\s+\[[x\s]\]\s+'
        if re.match(checkbox_line_pattern, line, re.IGNORECASE):
            return line
        
        # Return line unchanged if no patterns match
        return line
    
    @staticmethod
    def preserve_checkmarks(markdown: str) -> str:
        """
        Convert Unicode checkmarks to a format that won't be misinterpreted.
        
        Args:
            markdown: The markdown content
            
        Returns:
            Markdown with preserved checkmarks
        """
        # Replace Unicode checkmarks with text equivalent
        replacements = {
            '✅': '[✓]',  # Green checkmark
            '✓': '[✓]',   # Regular checkmark
            '✔': '[✓]',   # Heavy checkmark
            '☑': '[✓]',   # Ballot box with check
            '☐': '[ ]',   # Empty ballot box
            '☒': '[x]',   # Ballot box with X
        }
        
        result = markdown
        for unicode_char, replacement in replacements.items():
            result = result.replace(unicode_char, replacement)
        
        return result
    
    @staticmethod
    def format_complete(markdown: str) -> str:
        """
        Apply all formatting transformations for TheBrain.
        
        Args:
            markdown: The original markdown content
            
        Returns:
            Fully formatted markdown for TheBrain
        """
        # First handle checkmarks
        formatted = TheBrainMarkdownFormatter.preserve_checkmarks(markdown)
        
        # Then handle bullet points
        formatted = TheBrainMarkdownFormatter.format_for_thebrain(formatted)
        
        return formatted


def format_markdown_for_thebrain(markdown: str) -> str:
    """
    Convenience function to format markdown for TheBrain.
    
    Args:
        markdown: The original markdown content
        
    Returns:
        Formatted markdown that will render correctly in TheBrain
    """
    formatter = TheBrainMarkdownFormatter()
    return formatter.format_complete(markdown)
