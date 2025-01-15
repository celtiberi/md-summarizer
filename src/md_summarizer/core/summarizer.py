"""
Core module containing the main summarizer implementation.

This module provides the MarkdownSummarizer class which orchestrates
the markdown parsing, section processing, and progress tracking.
"""
from typing import Dict, List, Optional, AsyncGenerator
import logging
import asyncio
from pydantic_ai.usage import Usage

from ..agent import SummarizerAgent
from ..parser import MarkdownParser
from ..models import Section
from ..progress.models import ProgressStatus, ProgressUpdate
from ..common.signals import (
    section_complete, processing_complete,
)

logger = logging.getLogger(__name__)

class MarkdownSummarizer:
    """Summarizes markdown content by recursively processing sections."""
    
    def __init__(self, agent: Optional[SummarizerAgent] = None):
        """Initialize summarizer with AI agent.
        """
        self.agent = agent or SummarizerAgent()
        self.parser = MarkdownParser()

    def usage(self) -> Usage:
        """Return usage statistics."""
        return self.agent.usage
    
    async def summarize(self, content: str) -> str:
        """Summarize markdown content while preserving structure."""
        try:
            async for update in self.stream(content):
                if update.status == ProgressStatus.COMPLETE:
                    return update.content
        except Exception as e:
            logger.exception(f"Error during summarization: {e}")
            raise

    async def stream(self, content: str) -> AsyncGenerator[ProgressUpdate, None]:
        """Summarize markdown content while preserving structure."""
        try:
            sections = self.parser.parse(content)
            total_items = self._count_total_sections(sections)
            
            # Report total sections
            yield ProgressUpdate(
                status=ProgressStatus.STARTING,
                total_sections=total_items
            )
            
            # Create queue for section completion updates
            section_updates = asyncio.Queue()
            
            def on_section_complete(sender, section_title: str):
                section_updates.put_nowait(ProgressUpdate(
                    status=ProgressStatus.SECTION_COMPLETE,
                    section_title=section_title
                ))
            
            # Connect to section completion signal
            with section_complete.connected_to(on_section_complete):
                tasks = [
                    section.process(self.agent)
                    for section in sections.values()
                ]
            
                # Process sections and yield updates
                async with asyncio.TaskGroup() as tg:
                    processing = tg.create_task(self._process_sections(tasks, sections))
                    
                    # Yield section completion updates
                    for _ in range(total_items):
                        try:
                            update = await section_updates.get()
                            logger.info(f"Section completed: {update.section_title}")
                            yield update
                        except asyncio.CancelledError:
                            logger.info("Section processing cancelled")
                            raise
                    
                    # Get final result
                    final_content = await processing
                    
                    # Yield final update after all section updates
                    yield ProgressUpdate(
                        status=ProgressStatus.COMPLETE,
                        content=final_content
                    )
                    
        except Exception as e:
            logger.exception(f"Error during summarization: {e}")
            yield ProgressUpdate(
                status=ProgressStatus.ERROR,
                error=str(e)
            )
            raise

    def _combine_sections(self, sections: Dict[str, Section]) -> str:
        """Combine top-level sections into final document."""
        return '\n\n'.join(
            section.combine()
            for section in sections.values()
        )

    async def _process_sections(
        self,
        tasks: List[asyncio.Task],
        sections: Dict[str, Section]
    ) -> str:
        """Process sections concurrently."""
        await asyncio.gather(*tasks)
        final = self._combine_sections(sections)
        processing_complete.send(self, content=final)
        return final

    def _count_total_sections(self, sections: Dict[str, Section]) -> int:
        """Count total sections using recursive sum."""
        count = sum(1 + self._count_total_sections(section.sections) 
                  for section in sections.values())
        logger.debug(f"Counted {count} sections: {[s.title for s in sections.values()]}")
        return count

    @property
    def system_prompt(self) -> str:
        """The system prompt used by the agent."""
        return self.agent.system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        self.agent.system_prompt = value

    @property
    def user_prompt(self) -> str:
        """The user prompt template used by the agent."""
        return self.agent.user_prompt

    @user_prompt.setter
    def user_prompt(self, value: str) -> None:
        self.agent.user_prompt = value 