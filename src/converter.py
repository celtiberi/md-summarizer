from typing import Dict, Any, List
from .md_parser import MarkdownParser
from .openai_client import OpenAIClient
from .config.settings import get_settings
import asyncio
import yaml
import time
import logging

class MarkdownToYamlConverter:
    """Converts markdown documents to YAML format."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.md_parser = MarkdownParser()
        self.openai_client = OpenAIClient(api_key=api_key, model=model)
        self.logger = logging.getLogger(__name__)

    def _prepare_section(self, section: str) -> str:
        """Prepare section for OpenAI by truncating if needed."""
        max_chars = 4000  # OpenAI's limit
        if len(section) > max_chars:
            # Keep header and first part of content
            lines = section.split('\n')
            header = lines[0]
            content = '\n'.join(lines[1:])
            # Take first 100 words of content
            words = content.split()[:100]
            truncated = ' '.join(words)
            return f"{header}\n{truncated}...(content truncated)"
        return section

    async def convert(self, input_file: str, output_file: str) -> None:
        """Convert markdown file to YAML."""
        try:
            # Log initial sections
            sections = self.md_parser.parse_file(input_file)
            self.logger.info(f"Parsed {len(sections)} sections:")
            for i, section in enumerate(sections):
                self.logger.info(f"Section {i}:\n{section}\n---")

            # Log prepared sections
            prepared_sections = [self._prepare_section(s) for s in sections]
            self.logger.info("Prepared sections for OpenAI:")
            for i, section in enumerate(prepared_sections):
                self.logger.info(f"Prepared {i}:\n{section}\n---")

            # Log OpenAI responses
            yaml_sections = await asyncio.gather(
                *[self.openai_client.convert_to_yaml(section) for section in prepared_sections]
            )
            self.logger.info("OpenAI responses:")
            for i, yaml_str in enumerate(yaml_sections):
                self.logger.info(f"YAML {i}:\n{yaml_str}\n---")

            # Log cleaned YAML
            self.logger.info("Cleaned YAML sections:")
            for i, section in enumerate(yaml_sections):
                cleaned = self._clean_yaml_response(section)
                self.logger.info(f"Cleaned {i}:\n{cleaned}\n---")

            # Log final merged result
            merged_yaml = self._merge_yaml_sections(yaml_sections)
            self.logger.info(f"Final merged YAML:\n{merged_yaml}")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(merged_yaml)

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}", exc_info=True)
            raise ValueError(f"Conversion failed: {e}")

    def _clean_yaml_response(self, yaml_str: str) -> str:
        """Clean YAML response from OpenAI by removing code fence markers."""
        # Remove code fence if present
        if yaml_str.startswith('```'):
            lines = yaml_str.split('\n')
            # Remove first and last lines if they're code fences
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            yaml_str = '\n'.join(lines)
        return yaml_str.strip()

    def _merge_yaml_sections(self, sections: List[str]) -> str:
        """Merge YAML sections into single document."""
        merged_data = {}
        
        for section in sections:
            try:
                # Clean up the section
                cleaned = self._clean_yaml_response(section)
                
                # Skip empty sections
                if not cleaned.strip():
                    continue
                    
                # Parse YAML content
                section_data = yaml.safe_load(cleaned)
                if section_data:
                    # Add to merged data
                    merged_data.update(section_data)
                    
            except yaml.YAMLError:
                # If parsing fails, add as raw content
                self.logger.warning(f"Could not parse section as YAML:\n{section}")
                continue
        
        # Format the final YAML nicely using block style for multiline strings
        class BlockStyleDumper(yaml.SafeDumper):
            def represent_scalar(self, tag, value, style=None):
                if isinstance(value, str) and '\n' in value:
                    style = '|'  # Use block style for multiline strings
                return super().represent_scalar(tag, value, style)
        
        result = yaml.dump(
            merged_data,
            Dumper=BlockStyleDumper,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
            width=80,  # Wrap long lines
            sort_keys=False  # Preserve section order
        )
        
        return result
    
    def _deep_merge(self, dict1: dict, dict2: dict) -> None:
        """Recursively merge dict2 into dict1"""
        self.logger.info(f"Deep merging:\ndict1: {dict1}\ndict2: {dict2}")
        
        # Convert title to key
        if 'title' in dict2:
            # Convert "Section 1" to "section_1"
            key = dict2['title'].lower().strip()
            key = key.replace(' ', '_')
            if key not in dict1:
                dict1[key] = {}
            # Move content under the title key
            if 'content' in dict2:
                dict1[key]['content'] = dict2['content']
        else:
            # If no title, merge normally
            for key, value in dict2.items():
                if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                    self._deep_merge(dict1[key], value)
                else:
                    dict1[key] = value
                
        self.logger.info(f"After deep merge: {dict1}") 