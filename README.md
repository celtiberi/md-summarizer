# Markdown to YAML Converter

A tool that converts technical documentation from Markdown to YAML format using OpenAI's API. Designed to handle large markdown files by intelligently splitting them into sections and processing them concurrently.

## Features

- Splits markdown files into manageable sections based on headers
- Preserves code blocks and formatting
- Processes sections concurrently for better performance
- Maintains document hierarchy in YAML structure
- Handles large files without hitting token limits
- Environment-specific configurations

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/md-to-yaml.git
cd md-to-yaml

2. Install dependencies:
pip install -r requirements.txt

3. Set up your environment:
# For development
cp .env.example .env.development

# For production
cp .env.example .env.production

4. Configure your environment file with required settings:
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=2000
LOG_LEVEL=INFO

## Usage

### Basic Usage

from src.converter import MarkdownToYamlConverter

async def convert_docs():
    converter = MarkdownToYamlConverter()
    await converter.convert("input.md", "output.yaml")

### Example Input/Output

Input markdown:
# Project Title

## Installation
Install using pip:
pip install myproject

## Usage
Basic usage example:
from myproject import MyClass
obj = MyClass()

Output YAML:
project:
  title: Project Title
  installation:
    instructions: Install using pip
    code: |
      pip install myproject
  usage:
    description: Basic usage example
    code: |
      from myproject import MyClass
      obj = MyClass()

## Configuration

The converter can be configured through environment variables:

# Environment
ENV=development  # or production, test

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

## How It Works

The converter works in three main steps:

1. Markdown Parsing (MarkdownParser):
   - Splits content based on markdown headers
   - Ensures sections don't exceed token limits
   - Preserves markdown structure

2. YAML Conversion (OpenAIClient):
   - Converts markdown sections to YAML using OpenAI's API
   - Handles retries and error recovery
   - Maintains consistent YAML structure

3. Section Merging (MarkdownToYamlConverter):
   - Processes sections concurrently
   - Merges YAML sections while maintaining hierarchy
   - Handles section relationships

## Project Structure

md-to-yaml/
├── src/
│   ├── __init__.py
│   ├── converter.py      # Main converter logic
│   ├── md_parser.py      # Markdown parsing
│   ├── openai_client.py  # OpenAI API interaction
│   └── config/
│       └── settings.py   # Configuration management
├── tests/
│   ├── __init__.py
│   └── test_converter.py
├── requirements.txt
└── README.md

## Error Handling

The converter provides clear error messages for common issues:
- File reading/writing errors
- OpenAI API errors
- YAML parsing errors
- Token limit exceeded

## Development

### Environment Types

The project supports three environment types:
- development: For local development
- test: For running tests
- production: For production use

Each environment can have its own configuration in .env.{environment} files.

### Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b feature/amazing-feature)
3. Follow the KISS principles in .cursorrules
4. Commit your changes (git commit -m 'Add amazing feature')
5. Push to the branch (git push origin feature/amazing-feature)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
