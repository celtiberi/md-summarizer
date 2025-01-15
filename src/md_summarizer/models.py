class Section:
    async def process(self, agent: DocumentAgent, progress_reporter: ProgressReporter, depth: int = 0) -> None:
        """Process section content recursively."""
        total = max(1, len(self.sections))  # Avoid division by zero
        
        if self.content:
            self.content = await agent.summarize_section(self.content)
        
        # Process subsections
        for i, section in enumerate(self.sections.values()):
            progress_reporter.start_section(section.title, i, total, depth)
            await section.process(agent, progress_reporter, depth + 1)
            progress_reporter.complete_section(section.title, i, total, depth) 