"""
Progress tracking models and enums.

This module defines the data structures used for tracking and reporting progress
during markdown summarization.
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ProgressStatus(str, Enum):
    """Status types for progress updates."""
    STARTING = "starting"
    SECTION_COMPLETE = "section_complete"
    COMPLETE = "complete"
    ERROR = "error"

class ProgressUpdate(BaseModel):
    """
    Progress update from the summarizer.

    Attributes:
        status: Current processing status
        content: Optional final content (for COMPLETE status)
        total_sections: Optional total number of sections
        error: Optional error message
        section_title: Optional section title for SECTION_COMPLETE
    """
    status: ProgressStatus
    total_sections: Optional[int] = None  # Only set for STARTING
    content: Optional[str] = None  # Only set for COMPLETE
    error: Optional[str] = None  # Only set for ERROR 
    section_title: Optional[str] = None  # Only set for SECTION_COMPLETE 