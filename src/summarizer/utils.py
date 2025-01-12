"""Utility functions for API documentation processing."""

from typing import List
from .types import APIInfo
import re
from tiktoken import encoding_for_model, get_encoding

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

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens using OpenAI's tiktoken library.
    
    Args:
        text: The text to count tokens for
        model: The model to use for counting tokens (default: gpt-3.5-turbo)
        
    Returns:
        Number of tokens in the text
    """
    try:
        # Try to get encoding for specific model
        encoding = encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base for unknown models
        encoding = get_encoding("cl100k_base")
    
    return len(encoding.encode(text)) 