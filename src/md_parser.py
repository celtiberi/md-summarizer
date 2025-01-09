from typing import List
import re

class MarkdownParser:
    def __init__(self, max_tokens: int = 2000):
        """Initialize markdown parser."""
        self.max_tokens = max_tokens
        
        # Match any header line
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.MULTILINE)

    def parse_file(self, file_path: str) -> List[str]:
        """Parse markdown file into sections."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                return []

            # Split content at headers
            sections = []
            lines = content.split('\n')
            current_section = []
            
            for line in lines:
                match = self.header_pattern.match(line)
                if match:
                    # Start new section at every header
                    if current_section:
                        sections.append('\n'.join(current_section).strip())
                    current_section = []
                    # Reconstruct header with consistent format
                    header = f"{match.group(1)} {match.group(2)}"
                    current_section.append(header)
                else:
                    current_section.append(line)
            
            # Add final section
            if current_section:
                sections.append('\n'.join(current_section).strip())
            
            return sections or ([content] if content else [])
            
        except Exception as e:
            raise ValueError(f"Could not read file {file_path}: {e}")