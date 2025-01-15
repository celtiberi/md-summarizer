"""
Progress reporting functionality.

This module handles sending progress updates during section processing.
"""
from ..common.signals import section_processing, section_complete
from .models import (
    ProgressStatus, ProgressUpdate,
    BASE_PROGRESS, DEPTH_FACTOR, PROGRESS_RANGE, SECTION_INCREMENT
)

class ProgressReporter:
    """
    Reports progress for section processing.

    Handles calculating and sending progress updates as sections
    are processed, taking into account nesting depth.
    """
    def __init__(self, sender) -> None:
        """Initialize reporter with sender object."""
        self.sender = sender
        self.sections_seen = set()  # Track unique sections
    
    def start_section(self, section: str, index: int, total: int, depth: int) -> None:
        """Signal the start of section processing."""
        self.sections_seen.add(section)
        progress = self.calculate_progress(depth, index, total)
        self.report_progress(section, progress)
    
    def complete_section(self, section: str, index: int, total: int, depth: int) -> None:
        """Signal the completion of section processing."""
        progress = self.calculate_progress(depth, index + 1, total)
        self.report_complete(section, progress)
    
    def calculate_progress(self, depth: int, section_num: int, total_sections: int) -> float:
        """Calculate progress percentage for a section."""
        # Base progress is 10-90%
        if depth == 0:
            # Top level sections get full range
            section_progress = (section_num / total_sections) * PROGRESS_RANGE
            return BASE_PROGRESS + section_progress
        else:
            # Subsections work within their parent's range
            parent_progress = BASE_PROGRESS + ((section_num - 1) / total_sections) * PROGRESS_RANGE
            next_parent = BASE_PROGRESS + (section_num / total_sections) * PROGRESS_RANGE
            subsection_range = next_parent - parent_progress
            return parent_progress + (subsection_range / 2)  # Split parent's range
    
    def report_progress(self, section: str, progress: float):
        """Report progress for a section."""
        section_processing.send(self.sender, section=section, progress=progress)
    
    def report_complete(self, section: str, progress: float):
        """Report section completion."""
        section_complete.send(self.sender, section=section, progress=progress) 