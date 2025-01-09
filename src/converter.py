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

    async def convert(self, input_file: str, output_file: str) -> None:
        """Convert markdown file to YAML."""
        try:
            # Read and parse
            sections = self.md_parser.parse_file(input_file)
            
            # Convert sections
            yaml_sections = await asyncio.gather(
                *[self.openai_client.convert_to_yaml(section) for section in sections]
            )
            
            # Merge and write
            merged_yaml = self._merge_yaml_sections(yaml_sections)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(merged_yaml)
                
        except Exception as e:
            raise ValueError(f"Conversion failed: {e}")

    def _merge_yaml_sections(self, sections: List[str]) -> str:
        """Merge YAML sections into single document."""
        merged_data = {}
        for section in sections:
            try:
                section_data = yaml.safe_load(section)
                if section_data:
                    self._deep_merge(merged_data, section_data)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML received from OpenAI: {e}")
        
        return yaml.dump(merged_data, 
                        allow_unicode=True, 
                        default_flow_style=False,
                        indent=2)
    
    def _deep_merge(self, dict1: dict, dict2: dict) -> None:
        """
        Recursively merge dict2 into dict1
        
        Args:
            dict1: Base dictionary to merge into
            dict2: Dictionary whose contents will be merged into dict1
        """
        for key, value in dict2.items():
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                self._deep_merge(dict1[key], value)
            else:
                dict1[key] = value 