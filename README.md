# Markdown Summarizer AI

A tool that intelligently summarizes technical documentation to reduce token count while preserving code blocks and structure. Designed to create concise versions of documentation that are optimized for AI consumption (e.g., as context for LLM prompts) while remaining human-readable.

## Features

- Reduces token count by 50-80% while maintaining key information
- Recursive section processing with parent-child relationships
- Maintains document hierarchy and structure
- Preserves code blocks in their original format
- Intelligently selects representative code examples
- Intelligent summarization of text content
- Intelligent header level management
- Environment-specific configurations
- Token limit handling

## Use Cases

- Prepare documentation for use as context in LLM prompts
- Reduce token usage when querying documentation with AI
- Create concise versions of technical documentation that preserve code examples
- Process large documentation files that would exceed token limits

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/md-summarizer-ai.git
cd md-summarizer-ai
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Unix
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment:
```bash
# Copy example environment file
cp .env.example .env

# Or use environment-specific files
cp .env.example .env.development
cp .env.example .env.production
cp .env.example .env.test
```

5. Configure your environment file:
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
LOG_LEVEL=INFO
```

## Usage

### Command Line

Summarize a markdown file:
```bash
python -m src.main --input docs/input.md --output dist/output.md --verbose
```

### Programmatic Usage

```python
from md_summarizer import MarkdownSummarizer
from md_summarizer.openai_client import OpenAIClient

async def summarize_docs():
    client = OpenAIClient(api_key="your-api-key")
    summarizer = MarkdownSummarizer(client)
    with open("input.md") as f:
        content = f.read()
    summary = await summarizer.summarize(content)
```

## Configuration

The converter supports multiple environment configurations:

1. Default: Uses `.env` file
2. Environment-specific: Uses `.env.{environment}` when ENV is set:
   - `ENV=development` → `.env.development`
   - `ENV=test` → `.env.test`
   - `ENV=production` → `.env.production`

Configuration options:
```env
# OpenAI Settings
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_REQUEST_TIMEOUT=30
OPENAI_MAX_TOKENS_PER_REQUEST=4000

# Markdown Parser Settings
DEFAULT_SECTION_SIZE=2000

# Output Settings
YAML_INDENT=2
```

## Project Structure

```
md-summarizer-ai/
├── src/
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   ├── md_summarizer.py # Main summarization logic
│   ├── openai_client.py # OpenAI API client
│   ├── prompts/         # Prompt templates
│   └── config/         
│       └── settings.py  # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_openai_client.py
│   └── utils/
│       └── output_formatter.py
├── requirements.txt
└── README.md
```

## How It Works

1. **Section Processing**:
   - Parses markdown into hierarchical sections
   - Maintains parent-child relationships
   - Handles section level management

2. **OpenAI Integration**:
   - Converts sections using OpenAI's API
   - Manages token limits automatically
   - Preserves formatting and structure

3. **Configuration Management**:
   - Environment-specific settings
   - Flexible configuration options
   - Cached settings for performance

## Development

### Testing

Run tests with pytest:
```bash
pytest
```

Run specific test:
```bash
pytest tests/test_openai_client.py::TestIntegration::test_with_child_summaries
```
### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
This means:
- You can use this software for personal and non-commercial purposes
- If you want to use this software commercially, you need to make your source code available
- Any modifications or derivative works must also be licensed under AGPL-3.0
- See the LICENSE file for full details

