"""Prompts for section processing and summarization."""

from typing import List

def get_summarization_prompt(level: int, child_summaries: List[str] = None) -> str:
    """Get the prompt for summarizing a section."""
    return """Summarize the following markdown section. Be very concise and focus on the key points.
Remove any redundant information but preserve all code blocks and examples.

Guidelines:
1. Keep ALL code blocks and examples
2. Combine similar code examples if possible
3. Focus on unique technical details
4. Omit obvious or standard information
5. Use shorter phrases where possible
6. Remove unnecessary text formatting
7. Keep only the most important points

The summary should be clear and technically accurate, but prioritize brevity over completeness.
Format code blocks exactly as they appear in the original."""

def get_api_system_prompt() -> str:
    """Get the system prompt for API documentation summarization."""
    return """You are a technical documentation summarizer focused on brevity and clarity.
Your goal is to create concise summaries that preserve essential information while reducing length.
Focus on key technical details and remove redundant or obvious information.
IMPORTANT: Always preserve code blocks and examples, but you may combine similar examples."""

def get_doc_processing_prompt(level: int = 3) -> str:
    """Get prompt for processing API documentation.
    
    Args:
        level: Header level to use (default: 3 for ###)
    """
    return f"""Process this documentation to create a clear, concise summary while:
    1. Preserving important information WITHOUT ANY DUPLICATION
    2. CRITICAL: Keep ALL tables in their original format - do not convert tables to text
    3. Maintaining original formatting (tables, code blocks) but showing each element EXACTLY ONCE
    4. IMPORTANT: Keep ALL code examples (bash, python, etc.) - do not drop any
    5. Keeping the structure organized as follows:
       
       {'#' * level} Title
       Brief overview
       
       {'#' * (level + 1)} API Signatures
       ```python
       # Show method signatures
       ```
       
       {'#' * (level + 1)} Usage Examples
       ```python
       # Python examples must be preserved
       ```
       
       {'#' * (level + 1)} Technical Notes
       - Additional details (if needed)""" 