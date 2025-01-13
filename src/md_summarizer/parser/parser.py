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
        
    def _find_headings(self, content: str, level: int) -> List[tuple[int, str]]:
        """Find all headings at specified level, ignoring those in code blocks."""
        headings = []
        in_code_block = False
        
        for line_num, line in enumerate(content.splitlines()):
            stripped = line.strip()
            
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if not in_code_block:
                heading_match = re.match(f'^#{{{level}}}\\s+(.+)$', stripped)
                if heading_match:
                    headings.append((line_num, heading_match.group(1)))
        
        return headings

    def _split_content_at_lines(self, content: str, split_points: List[int]) -> List[str]:
        """Split content at specified line numbers."""
        lines = content.splitlines()
        sections = []
        
        for i, start in enumerate(split_points):
            end = split_points[i + 1] if i < len(split_points) - 1 else len(lines)
            section_lines = lines[start:end]
            # Remove the heading line
            section_content = '\n'.join(section_lines[1:])
            sections.append(section_content)
            
        return sections

    def _split_at_level(self, content: str, level: int) -> List[Section]:
        """Split content at specified heading level."""
        # Find all headings at this level
        headings = self._find_headings(content, level)
        if not headings:
            return []
        
        # Get line numbers where splits should occur
        split_points = [pos for pos, _ in headings]
        
        # Split content at heading positions
        section_contents = self._split_content_at_lines(content, split_points)
        
        # Validate we have matching headings and contents
        if len(headings) != len(section_contents):
            self.logger.error("Mismatch between headings and content sections")
            return []
        
        # Create sections
        sections = []
        for (_, title), content in zip(headings, section_contents):
            section = Section(
                title=title,
                content=content.strip(),
                level=level
            )
            
            # Recursively process subsections if not at max depth
            if level < 6:  # Don't process beyond h6
                subsections = self._split_at_level(section.content, level + 1)
                if subsections:
                    section.sections = {
                        self._make_key(s.title): s 
                        for s in subsections
                    }
                    
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