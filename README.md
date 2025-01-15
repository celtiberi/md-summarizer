# Markdown Summarizer

An AI-powered tool that reduces the token size of Markdown documents while preserving their essential structure, code blocks, and meaning. Designed to help fit documentation into AI context windows without losing critical information.

## Features

- **Token Reduction**: Intelligently reduces document size
- Preserves markdown heading hierarchy
- Protects code blocks and technical details
- Bottom-up concurrent processing
- Real-time progress updates
- Streaming API
- Multiple AI provider support

## Usage

```python
from md_summarizer import (
    MarkdownSummarizer, 
    ProgressStatus
)

# Basic usage
summarizer = MarkdownSummarizer()
result = await summarizer.summarize(content)

# Streaming updates
async for update in summarizer.stream(content):
    if update.status == ProgressStatus.STARTING:
        print(f"Processing {update.total_sections} sections...")
    elif update.status == ProgressStatus.SECTION_COMPLETE:
        print(f"Completed section: {update.section_title}")
    elif update.status == ProgressStatus.COMPLETE:
        print("Done!")
        print(update.content)

# Progress update types:
# - ProgressStatus.STARTING: total_sections count
# - ProgressStatus.SECTION_COMPLETE: section_title of completed section
# - ProgressStatus.COMPLETE: final content
# - ProgressStatus.ERROR: error details if something fails

# Customize prompts
summarizer.system_prompt = "Your custom system prompt"
summarizer.user_prompt = "Your custom user prompt"
```

Example output:
```
Status: ProgressStatus.STARTING, Total Sections: 4
Status: ProgressStatus.SECTION_COMPLETE, Section: Subsection 2.1
Status: ProgressStatus.SECTION_COMPLETE, Section: Section 1
Status: ProgressStatus.SECTION_COMPLETE, Section: Section 2
Status: ProgressStatus.SECTION_COMPLETE, Section: Test Document
Status: ProgressStatus.COMPLETE
```

## Installation

The module has not yet been published to PyPI. So you need to install it from the source code.

## Configuration

Set environment variables or use .env file:
```
OPENAI_API_KEY=your-key
MODEL=gpt-3.5-turbo
PROVIDER=openai
LOG_LEVEL=INFO
```

## How it Works

1. Parses markdown into hierarchical sections
2. Processes sections bottom-up (children before parents)
3. Preserves heading levels and structure
4. Provides real-time progress updates
5. Combines processed sections into final document

## Development

```bash
# Install development dependencies
pip install -e ".[test]"

# Run tests
make test
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
