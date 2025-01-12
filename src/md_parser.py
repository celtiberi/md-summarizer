from dataclasses import dataclass, field
from typing import Dict, Optional, List
import re
import logging

@dataclass
class Section:
    """Represents a section of markdown content."""
    title: str = ""
    content: str = ""
    level: int = 0
    sections: Dict[str, "Section"] = field(default_factory=dict)

class MarkdownParser:
    def __init__(self):
        """Initialize markdown parser."""
        self.logger = logging.getLogger(__name__)
        
    def _split_at_level(self, content: str, level: int) -> List[Section]:
        """Split content at specified heading level."""
        # Find all level N headings and their positions
        positions = []
        current_pos = 0
        in_code_block = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # Toggle code block state
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                current_pos += len(line) + 1
                continue
                
            # Only look for headings when not in code block
            if not in_code_block:
                heading_match = re.match(f'^#{{{level}}}\\s+(.+)$', stripped)
                if heading_match:
                    positions.append((current_pos, heading_match.group(1)))
                    
            current_pos += len(line) + 1  # +1 for newline
        
        if not positions:
            return []
            
        # Split content at heading positions
        sections = []
        for i, (pos, title) in enumerate(positions):
            # Get content up to next heading or end
            next_pos = positions[i+1][0] if i < len(positions)-1 else len(content)
            section_content = content[pos:next_pos].strip()
            
            # Remove the heading line from content
            section_content = '\n'.join(section_content.splitlines()[1:])
            
            # Create section
            section = Section(
                title=title,
                content=section_content,
                level=level
            )
            
            # Recursively process subsections
            if level < 6:  # Don't process beyond h6
                subsections = self._split_at_level(section_content, level + 1)
                if subsections:
                    section.sections = {
                        self._make_key(s.title): s 
                        for s in subsections
                    }
                    # Set parent reference for each subsection
                    for subsection in section.sections.values():
                        subsection.parent = section
                    
            sections.append(section)
            
        return sections
    
    def _make_key(self, title: str) -> str:
        """Create a safe section key from title."""
        key = title.lower()
        key = re.sub(r'[^a-z0-9]+', '_', key)
        key = re.sub(r'_+', '_', key)
        return key.strip('_')
        
    def parse(self, content: str) -> Dict[str, Section]:
        """Parse markdown content into hierarchical sections."""
        self.logger.info("Starting markdown parsing...")
        
        if not content.strip():
            return {}
            
        # Find the highest level heading used (smallest number of #s)
        # but ignore headings in code blocks
        headings = []
        in_code_block = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if not in_code_block:
                heading_match = re.match(r'^(#{1,6})\s', stripped)
                if heading_match:
                    headings.append(heading_match.group(1))
        
        if not headings:
            self.logger.info("No headings found, creating root section")
            return {
                'root': Section(
                    title='root',
                    content=content,
                    level=1
                )
            }
            
        min_level = min(len(h) for h in headings)
        self.logger.info(f"Found minimum heading level: {min_level}")
        
        # Split at the highest level found and normalize levels
        sections = self._split_at_level(content, min_level)
        
        # Normalize all levels by subtracting (min_level - 1)
        def normalize_levels(section: Section, level_adjust: int):
            section.level -= level_adjust
            for subsection in section.sections.values():
                normalize_levels(subsection, level_adjust)
        
        # Adjust all levels so minimum becomes level 1
        level_adjust = min_level - 1
        for section in sections:
            normalize_levels(section, level_adjust)
        
        # Convert to dictionary
        return {
            self._make_key(section.title): section
            for section in sections
        }

    def _add_section(self, sections: Dict[str, Section], title: str, content: str, level: int) -> None:
        """Add a new section to the sections dict."""
        key = self._normalize_title(title)
        section = Section(title=title, content=content, level=level)
        sections[key] = section
        
        # Set parent for any existing child sections
        for child in section.sections.values():
            child.parent = section