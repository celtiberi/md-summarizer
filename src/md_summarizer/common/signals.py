"""Signal definitions for the application."""
from blinker import Signal

section_complete = Signal('section-complete')
processing_complete = Signal('processing-complete') 