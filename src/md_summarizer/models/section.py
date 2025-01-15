from typing import Dict
from ..agent import SummarizerAgent
from ..common.signals import section_complete
from dataclasses import dataclass, field
import asyncio

@dataclass
class Section:
    """Base section class."""
    title: str
    content: str
    level: int
    sections: Dict[str, 'Section'] = field(default_factory=dict)
    
    # Section level constants
    ROOT_LEVEL = 1
    IMPORTANT_LEVEL = 2
    
    async def process(self, agent: SummarizerAgent) -> None:
        """Process section content recursively."""
        # Process subsections first
        tasks = [
            section.process(agent)
            for section in self.sections.values()
        ]
        if tasks:
            await asyncio.gather(*tasks)
        
        # Then process this section
        self.content = await agent.run(self.content)
        section_complete.send(self, section_title=self.title)
        
    def combine(self) -> str:
        """Combine this section with its children into markdown."""
        parts = []
        
        def get_header(level: int, title: str) -> str:
            """Generate header with proper level."""
            return '#' * max(1, level) + ' ' + title
        
        # Add this section's header and content
        header = get_header(self.level, self.title)
        parts.append(header)
        if self.content:
            parts.append(self.content)
        
        # Add child sections
        for section in self.sections.values():
            # Recursively combine child sections
            child_content = section.combine()
            if child_content:
                parts.append(child_content)
        
        return '\n\n'.join(filter(None, parts)) 