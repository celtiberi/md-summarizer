# MD Summarizer

AI-powered Markdown document summarizer that preserves structure and code blocks.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PyPI version](https://badge.fury.io/py/md-summarizer.svg)](https://badge.fury.io/py/md-summarizer)
[![GitHub issues](https://img.shields.io/github/issues/celtiberi/md-summarizer)](https://github.com/celtiberi/md-summarizer/issues)

## Repository

- Source Code: [https://github.com/celtiberi/md-summarizer](https://github.com/celtiberi/md-summarizer)
- Issue Tracker: [https://github.com/celtiberi/md-summarizer/issues](https://github.com/celtiberi/md-summarizer/issues)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This means that:
- You can use this software for any purpose
- You can modify this software
- You can distribute this software
- You must include the license and copyright notice with each and every distribution
- You must include the source code of any derivative works you distribute
- Changes you make must be documented
- Changes you make must use the same license
- Changes you make must be made available when you distribute the software
- If you use this software in a network service, you must make the complete source code available to users of the service

## Features

- Maintains document structure and headings
- Preserves code blocks and examples
- Concurrent section processing
- Token usage tracking
- Multiple AI provider support

## Installation

```bash
pip install md-summarizer
```

## Usage

Simple usage:
```python
from md_summarizer import MarkdownSummarizer

# Initialize and summarize
summarizer = MarkdownSummarizer()
result = await summarizer.summarize(markdown_content)

# Get usage statistics
usage: pydantic_ai.usage.Usage = summarizer.usage()
print(f"Requests: {usage.requests}")
print(f"Input tokens: {usage.request_tokens}")
print(f"Output tokens: {usage.response_tokens}")
print(f"Total tokens: {usage.total_tokens}")
```

## Configuration

Set environment variables or use .env file:
```bash
# Required
OPENAI_API_KEY=your-api-key

# Optional
MODEL=gpt-3.5-turbo  # Default model
LOG_LEVEL=INFO       # Logging level
```

## Development

```bash
# Install development dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run specific test
make test-case TEST=test_name
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate.

Repository: [https://github.com/celtiberi/md-summarizer](https://github.com/celtiberi/md-summarizer)

