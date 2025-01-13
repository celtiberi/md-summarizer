"""Agent module for document summarization."""
from .document_agent import DocumentAgent
from .prompts import get_system_prompt, get_summarization_prompt

__all__ = ['DocumentAgent', 'get_system_prompt', 'get_summarization_prompt'] 