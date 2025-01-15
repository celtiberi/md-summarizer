"""Central location for all signal definitions."""
from blinker import signal

# Progress signals
processing_started = signal('processing-started')
section_parsed = signal('section-parsed')
section_processing = signal('section-processing')
section_complete = signal('section-complete')
processing_complete = signal('processing-complete') 