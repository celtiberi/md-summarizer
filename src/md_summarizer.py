from typing import Dict, List
import logging
import asyncio
import re

from .openai_client import OpenAIClient 
from .md_parser import MarkdownParser, Section

class MarkdownSummarizer:
    """Summarizes markdown content by recursively processing sections."""
    
    def __init__(self, openai_client: OpenAIClient):
        """Initialize summarizer with OpenAI client."""
        self.openai_client = openai_client
        self.logger = logging.getLogger(__name__)
        self.parser = MarkdownParser()

    async def summarize(self, content: str) -> str:
        """Summarize markdown content while preserving structure."""
        self.logger.info("Parsing content into sections...")
        sections = self.parser.parse(content)
        self.logger.info(f"Found sections: {list(sections.keys())}")
        
        processed = await self._process_sections(sections)
        return self._combine_sections(processed)

    async def _process_sections(self, sections: Dict[str, Section]) -> Dict[str, Section]:
        """Process all sections concurrently."""
        self.logger.info(f"Processing {len(sections)} sections: {list(sections.keys())}")
        tasks = [
            self._process_section(key, section)
            for key, section in sections.items()
        ]
        processed = await asyncio.gather(*tasks)
        return dict(zip(sections.keys(), processed))

    async def _process_section(self, name: str, section: Section) -> Section:
        """Process a section of content."""
        self.logger.info(f"Processing section '{name}' (level {section.level})")
        
        # First process any child sections
        if section.sections:
            self.logger.info(f"Processing {len(section.sections)} sections: {list(section.sections.keys())}")
            # Process all child sections in parallel
            child_tasks = [
                self._process_section(child_name, child)
                for child_name, child in section.sections.items()
            ]
            processed_children = await asyncio.gather(*child_tasks)
            processed_children_dict = dict(zip(section.sections.keys(), processed_children))
        else:
            processed_children = []
            processed_children_dict = {}
        
        # Then summarize this section's content
        if section.content:
            self.logger.info(f"Summarizing section '{name}' ({len(section.content)} chars)")
            child_summaries = [c.content for c in processed_children] if processed_children else None
            section.content = await self.openai_client.summarize_section(
                section.content, 
                section.level,
                child_summaries
            )
            self.logger.info(f"Section '{name}' summarized: {len(section.content)} chars")
        
        section.sections = processed_children_dict
        return section

    def _combine_sections(self, sections: Dict[str, Section]) -> str:
        """Combine processed sections into final document."""
        def flatten_section(section: Section) -> List[str]:
            """Recursively flatten section and children into list."""
            result = []
            
            # Only include content for leaf sections or important headers
            if not section.sections:
                header = '#' * section.level + ' ' + section.title
                result.extend([header, section.content, '---'])
            elif section.level <= 2:  # Only keep important high-level headers
                header = '#' * section.level + ' ' + section.title
                result.append(header)
            
            for child in section.sections.values():
                result.extend(flatten_section(child))
            return result
            
        content_parts = []
        for section in sections.values():
            content_parts.extend(flatten_section(section))
            
        # Filter out empty strings but keep separators
        filtered_parts = [p for p in content_parts if p.strip()]
        return '\n\n'.join(filtered_parts)