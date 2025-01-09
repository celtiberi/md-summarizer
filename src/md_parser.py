from typing import List, Tuple
import re
import logging

class MarkdownParser:
    """Splits markdown into manageable sections."""
    
    def __init__(self, max_section_size: int = 2000):
        self.max_section_size = max_section_size
        self.header_pattern = re.compile(r'^#{1,6}\s+.+$', re.MULTILINE)

    def parse_file(self, file_path: str) -> List[str]:
        """Parse markdown file into sections."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split on headers
            sections = self.header_pattern.split(content)
            return [s.strip() for s in sections if s.strip()]
            
        except Exception as e:
            raise ValueError(f"Failed to parse {file_path}: {e}") 