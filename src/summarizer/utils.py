"""Utility functions for API documentation processing."""

from typing import List
from .types import APIInfo
import re

def format_api_info(api_info: APIInfo) -> str:
    """Format API info into a string."""
    if api_info is None:
        raise ValueError("api_info cannot be None")
        
    lines = []
    for cls in api_info.classes:
        lines.append(f"class {cls.name}:")
        if cls.description:
            lines.append(f"    # {cls.description}")
        
        for method in cls.methods:
            params = ", ".join([
                f"{p.name}: {p.type}" + (f" = {p.default}" if p.default else "")
                for p in method.params
            ])
            lines.append(f"    def {method.name}({params}) -> {method.returns}:")
            if method.description:
                lines.append(f"        # {method.description}")
    
    return "\n".join(lines) 

def normalize_header_levels(content: str, level: int) -> str:
    """Ensure all headers are at the specified level."""
    header_marker = '#' * level
    return re.sub(r'^#{1,6}\s', f'{header_marker} ', content, flags=re.MULTILINE) 