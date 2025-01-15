from dataclasses import dataclass, field
from typing import Dict, Optional, List
import re
import logging
from ..models import Section

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
        headings = self._find_headings(content, level)
        if not headings:
            return []
        
        split_points = [pos for pos, _ in headings]
        section_contents = self._split_content_at_lines(content, split_points)
        
        sections = []
        for (_, title), content in zip(headings, section_contents):
            # Find where child sections begin
            child_matches = list(re.finditer(f'^#{{{level+1}}}\\s+', content, re.MULTILINE))
            
            if child_matches:
                # Only keep content up to first child section
                parent_content = content[:child_matches[0].start()].strip()
            else:
                parent_content = content.strip()
            
            section = Section(
                title=title,
                content=parent_content,
                level=level
            )
            
            # Process subsections
            if level < 6:
                subsections = self._split_at_level(content, level + 1)
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

    def _create_section(self, match: re.Match) -> Section:
        """Create section from regex match."""
        level = len(match.group(1))  # Count #'s
        title = match.group(2).strip()
        content = match.group(3).strip() if match.group(3) else ""
        
        return Section(
            title=title,
            content=content,
            level=level,  # Level is already correct from markdown
            sections={}
        )