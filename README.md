# Markdown to YAML Converter

A tool that converts technical documentation from Markdown to YAML format using OpenAI's API. Designed to handle large markdown files by intelligently splitting them into sections and processing them recursively.

## Features

- Recursive section processing with parent-child relationships
- Maintains document hierarchy and structure
- Preserves code blocks, tables, and formatting
- Intelligent header level management
- Environment-specific configurations
- Token limit handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/md-to-yaml-ai.git
cd md-to-yaml-ai
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
MAX_TOKENS=2000
LOG_LEVEL=INFO
```

## Usage

### Command Line

Convert a markdown file to YAML:
```bash
python -m src.main --input docs/input.md --output dist/output.yaml --verbose
```

### Programmatic Usage

```python
from src.converter import MarkdownToYamlConverter

async def convert_docs():
    converter = MarkdownToYamlConverter(api_key="your-api-key")
    await converter.convert("input.md", "output.yaml")
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
MAX_TOKENS=2000
OPENAI_REQUEST_TIMEOUT=30
OPENAI_MAX_TOKENS_PER_REQUEST=4000

# Markdown Parser Settings
DEFAULT_SECTION_SIZE=2000

# Output Settings
YAML_INDENT=2
```

## Project Structure

```
md-to-yaml-ai/
├── src/
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   ├── converter.py     # Main conversion logic
│   ├── openai_client.py # OpenAI API client
│   ├── prompts/         # Prompt templates
│   ├── summarizer/      # Section processing
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

This project is licensed under the MIT License - see the LICENSE file for details.

