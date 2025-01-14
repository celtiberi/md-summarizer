"""
MD Summarizer - AI-powered Markdown summarizer that preserves structure and code blocks.
"""

from .summarizer import MarkdownSummarizer
from .agent.document_agent import DocumentAgent

__version__ = "0.1.31"

__all__ = ["MarkdownSummarizer", "DocumentAgent"] 