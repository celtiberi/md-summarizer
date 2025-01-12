import pytest
import logging
import yaml
from typing import Dict, Any
import re
from tiktoken import get_encoding
from src.summarizer import APIInfo, Class, Method, Parameter
from src.summarizer.utils import format_api_info
from .utils.output_formatter import format_section

# Fixtures
@pytest.fixture
def basic_api_info():
    """Basic API info for testing."""
    return APIInfo(
        classes=[
            Class(
                name="MarkdownParser",
                methods=[
                    Method(
                        name="parse",
                        params=[Parameter(name="text", type="str")],
                        returns="List[str]",
                        exceptions=[]
                    )
                ]
            )
        ],
        functions=[]
    )

@pytest.fixture
def complex_api_info():
    """Complex API info for testing."""
    return APIInfo(
        classes=[
            Class(
                name="BaseParser",
                methods=[Method(
                    name="parse",
                    params=[Parameter(name="text", type="str")],
                    returns="List[str]",
                    exceptions=["ParseError"]
                )]
            ),
            Class(
                name="AdvancedParser",
                methods=[Method(
                    name="parse_and_filter",
                    params=[
                        Parameter(name="text", type="str"),
                        Parameter(name="min_level", type="int", default="1")
                    ],
                    returns="List[str]",
                    exceptions=["ParseError", "FilterError"]
                )]
            )
        ],
        functions=[]
    )

@pytest.fixture
def verbose_content():
    """Verbose documentation content for testing."""
    return """### CLI Usage Guide
The Command Line Interface (CLI) provides a powerful and flexible way to convert markdown files
to YAML format. This comprehensive guide will walk you through all the available options and 
show you how to use them effectively in your workflow. The CLI tool is designed to be simple
yet powerful, making it easy to convert your documentation while maintaining full control over
the process.

Let's explore the various options and features that make this CLI tool so versatile and
user-friendly. Each option has been carefully designed to provide maximum flexibility while
maintaining ease of use.

Available Options:
Here's a complete list of all available command line options that you can use with the CLI:
| Option | Description |
|--------|-------------|
| --input | Input markdown file path |
| --output | Output YAML file path |
| --verbose | Enable detailed logging |
| --quiet | Suppress all output |
| --format | Output format (default: yaml) |

The --input and --output options are required for basic operation. The --verbose and --quiet
options help control the output level, while --format lets you specify the output format.

Basic Example:
Here's a simple example showing the most common usage pattern:
```bash
$ cli run --input in.md --output out.yaml
```

Advanced Usage:
For more complex scenarios, you can combine multiple options:
```bash
$ cli run --input docs/api.md --output dist/api.yaml --verbose
```

Python Integration:
The CLI tool can also be used programmatically in your Python code. Here are some examples:
```python
# Basic usage - this is the simplest way to use the CLI
cli = CLI()
cli.run('in.md', 'out.yaml')

# With error handling - recommended for production use
try:
    cli = CLI()
    cli.run('docs/api.md', 'dist/api.yaml')
except CLIError as e:
    print(f"Failed to convert: {e}")
```

Remember that proper error handling is important in production environments. The CLI tool
will raise CLIError if something goes wrong during conversion.

For more examples and detailed documentation, please refer to our online documentation.
You can find additional examples, best practices, and troubleshooting tips in the docs."""

# Helper Functions
def count_tokens(text: str) -> int:
    """Count tokens using OpenAI's tiktoken library."""
    encoding = get_encoding("cl100k_base")
    return len(encoding.encode(text))

def verify_summary_output(summary: str) -> Dict[str, Any]:
    """Verify summary structure."""
    return {
        "has_code": "```" in summary,
        "code_blocks": summary.count("```") // 2,
        "length_chars": len(summary),
        "has_tables": "|" in summary,
        "has_cli": "$" in summary,
        "has_error_handling": "try:" in summary and "except" in summary,
    }

# Add test categories
pytestmark = pytest.mark.asyncio

# Component Tests
class TestAPIAnalyzer:
    @pytest.mark.asyncio
    async def test_extraction(self, client):
        """Should extract API information from documentation."""
        content = """
        class MarkdownParser:
            def parse(text: str) -> List[str]:
                '''Parse markdown text.'''
                return sections
        """
        
        api_info = await client.analyzer.analyze(content)
        
        assert isinstance(api_info, APIInfo)
        assert len(api_info.classes) == 1
        assert api_info.classes[0].name == "MarkdownParser"
        assert len(api_info.classes[0].methods) == 1
        assert api_info.classes[0].methods[0].name == "parse"
        
    @pytest.mark.asyncio
    async def test_extraction_with_multiple_methods(self, client):
        """Should handle multiple methods in a class."""
        content = """
        class Parser:
            def parse(text: str) -> List[str]: pass
            def filter(sections: List[str]) -> List[str]: pass
        """
        api_info = await client.analyzer.analyze(content)
        assert len(api_info.classes[0].methods) == 2

class TestCodeSynthesizer:
    @pytest.mark.asyncio
    async def test_basic_synthesis(self, client, basic_api_info):
        """Should generate basic code examples."""
        content = """Example: parser.parse(text)"""
        examples = await client.synthesizer.synthesize(content, basic_api_info)
        
        formatter = OutputFormatter()
        
        # Show configuration
        formatter.format_section(OutputSection(
            title="CONFIGURATION",
            content={
                "API Info": format_api_info(basic_api_info),
                "Input Content": content
            }
        ))
        
        # Show output and stats
        formatter.format_section(OutputSection(
            title="GENERATED OUTPUT",
            content={
                "Examples": examples,
                "Python Blocks": examples.count('```python'),
                "Total Blocks": examples.count('```') // 2,
                "Individual Blocks": [
                    block.strip() for block in examples.split("```")[1::2]
                ]
            }
        ))
        
        assert "```python" in examples
        assert "MarkdownParser" in examples
        assert examples.count("```") == 6
    
    @pytest.mark.asyncio
    async def test_synthesis_with_complex_api(self, client, complex_api_info):
        """Should handle complex inheritance and multiple classes."""
        content = """Example inheritance usage"""
        examples = await client.synthesizer.synthesize(content, complex_api_info)
        
        formatter = OutputFormatter()
        
        # Show configuration
        formatter.format_section(OutputSection(
            title="CONFIGURATION",
            content={
                "API Info": format_api_info(complex_api_info),
                "Input Content": content
            }
        ))
        
        # Show output and stats
        formatter.format_section(OutputSection(
            title="GENERATED OUTPUT",
            content={
                "Examples": examples,
                "Python Blocks": examples.count('```python'),
                "Total Blocks": examples.count('```') // 2,
                "Individual Blocks": [
                    block.strip() for block in examples.split("```")[1::2]
                ]
            }
        ))
        
        assert "```python" in examples
        assert "BaseParser" in examples
        assert "AdvancedParser" in examples
        assert examples.count("```") == 6

class TestDocProcessor:
    @pytest.mark.asyncio
    async def test_basic_processing(self, client, basic_api_info):
        """Should process basic documentation."""
        content = """### MarkdownParser Documentation
The MarkdownParser class is a powerful and flexible tool for processing markdown documents.
It provides comprehensive functionality for parsing and processing markdown text into
manageable sections. The class supports various operations including section-based parsing,
token counting, and configurable processing options.

Key Features and Benefits:
- Section-based parsing for better organization
- Efficient token counting for length management
- Highly configurable processing options
- Easy to use API
- Extensible design
- Comprehensive error handling

Basic Example:
```python
# Create parser instance
parser = MarkdownParser()

# Parse markdown text
sections = parser.parse(markdown_text)

# Process sections
for section in sections:
    print(f"Section: {section}")
```

Advanced Configuration:
```python
# Configure parser with options
parser = MarkdownParser(
    max_tokens=1000,    # Limit token count
    min_level=2,        # Only sections level 2+
    default_level=1     # Default section level
)

# Parse and filter in one step
filtered = parser.parse_and_filter(markdown_text)
```

For more details about configuration options and advanced usage,
please refer to the API reference documentation below."""

        examples = """```python
# Basic usage
parser = MarkdownParser()
result = parser.parse(text)

# With configuration
parser = MarkdownParser(max_tokens=1000)
result = parser.parse(text)
```"""
        
        formatter = OutputFormatter()
        
        # Show input configuration
        formatter.format_section(OutputSection(
            title="CONFIGURATION",
            content={
                "API Info": format_api_info(basic_api_info),
                "Content": content,
                "Examples": examples
            }
        ))
        
        # Process content
        doc = await client.processor.process(content, basic_api_info, examples)
        
        # Show comparison
        formatter.format_comparison(content, doc)
        
        # Show verification
        formatter.format_section(OutputSection(
            title="VERIFICATION",
            content={
                "Has Headers": "### " in doc,
                "Has Code": "```python" in doc,
                "Has Class": "MarkdownParser" in doc,
                "Has Key Features": {
                    "Section Parsing": "section-based parsing" in doc.lower(),
                    "Token Counting": "token counting" in doc.lower()
                }
            }
        ))
        
        # Run assertions
        assert "### " in doc
        assert "```python" in doc
        assert "MarkdownParser" in doc
        assert "section-based parsing" in doc.lower()
        assert "token counting" in doc.lower()
    
    @pytest.mark.asyncio
    async def test_processing_with_tables(self, client):
        """Should preserve tables and CLI examples."""
        api_info = APIInfo(
            classes=[
                Class(
                    name="CLI",
                    methods=[
                        Method(
                            name="run",
                            params=[
                                Parameter(name="input", type="str"),
                                Parameter(name="output", type="str")
                            ],
                            returns="None",
                            exceptions=["CLIError"]
                        )
                    ]
                )
            ],
            functions=[]
        )
        
        content = """### CLI Usage Guide
The Command Line Interface (CLI) provides a powerful and flexible way to convert markdown files
to YAML format. This comprehensive guide will walk you through all the available options and 
show you how to use them effectively in your workflow. The CLI tool is designed to be simple
yet powerful, making it easy to convert your documentation while maintaining full control over
the process.

Let's explore the various options and features that make this CLI tool so versatile and
user-friendly. Each option has been carefully designed to provide maximum flexibility while
maintaining ease of use.

Available Options:
Here's a complete list of all available command line options that you can use with the CLI:
| Option | Description |
|--------|-------------|
| --input | Input markdown file path |
| --output | Output YAML file path |
| --verbose | Enable detailed logging |
| --quiet | Suppress all output |
| --format | Output format (default: yaml) |

The --input and --output options are required for basic operation. The --verbose and --quiet
options help control the output level, while --format lets you specify the output format.

Basic Example:
Here's a simple example showing the most common usage pattern:
```bash
$ cli run --input in.md --output out.yaml
```

Advanced Usage:
For more complex scenarios, you can combine multiple options:
```bash
$ cli run --input docs/api.md --output dist/api.yaml --verbose
```

Python Integration:
The CLI tool can also be used programmatically in your Python code. Here are some examples:
```python
# Basic usage - this is the simplest way to use the CLI
cli = CLI()
cli.run('in.md', 'out.yaml')

# With error handling - recommended for production use
try:
    cli = CLI()
    cli.run('docs/api.md', 'dist/api.yaml')
except CLIError as e:
    print(f"Failed to convert: {e}")
```

Remember that proper error handling is important in production environments. The CLI tool
will raise CLIError if something goes wrong during conversion.

For more examples and detailed documentation, please refer to our online documentation.
You can find additional examples, best practices, and troubleshooting tips in the docs."""

        examples = """```python
# Simple example - this shows basic usage
cli = CLI()
cli.run('in.md', 'out.yaml')

# Advanced usage with error handling - recommended for production
try:
    cli = CLI()
    cli.run('input.md', 'output.yaml')
except CLIError as e:
    print(f"Error: {e}")  # Handle any conversion errors
```"""
        
        print("\n" + "⭐️"*50)
        print("⭐️ TEST CONFIGURATION")
        print("⭐️"*50)
        print("\nAPI Info:")
        print("-"*20)
        print(format_api_info(api_info))
        
        print("\nContent:")
        print("-"*20)
        print(content)
        print(f"Content length: {len(content)}")
        
        print("\nExamples:")
        print("-"*20)
        print(examples)
        
        doc = await client.processor.process(content, api_info, examples)
        
        print("\n" + "⭐️"*50)
        print("⭐️ GENERATED OUTPUT")
        print("⭐️"*50)
        print("\nProcessed Doc:")
        print("-"*20)
        print(doc)
        print(f"Doc length: {len(doc)}")
        
        print("\n" + "⭐️"*50)
        print("⭐️ VERIFICATION")
        print("⭐️"*50)
        print(f"Has table markers: {'|' in doc}")
        print(f"Has CLI options: {'--input' in doc}")
        print(f"Has bash example: {'```bash' in doc}")
        print(f"Has Python code: {'```python' in doc}")
        print(f"Length reduction: {(1 - len(doc)/len(content))*100:.1f}%")
        
        assert "|" in doc  # Preserved table
        assert "--input" in doc  # Kept CLI options
        assert "```bash" in doc  # Kept bash example
        assert "```python" in doc  # Has Python code
        assert len(doc) < len(content)  # Is shorter

        # Content preservation checks
        assert "|" in doc  # Preserved table
        assert "--input" in doc  # Kept CLI options
        assert "```bash" in doc  # Kept bash example
        assert "```python" in doc  # Has Python code
        
        # Check token count instead of raw length
        original_tokens = count_tokens(content + examples)  # Include examples in original count
        processed_tokens = count_tokens(doc)
        print("\n" + "⭐️"*50)
        print("⭐️ TOKEN ANALYSIS")
        print("⭐️"*50)
        print(f"Original tokens: {original_tokens}")
        print(f"Processed tokens: {processed_tokens}")
        print(f"Token reduction: {(1 - processed_tokens/original_tokens)*100:.1f}%")
        assert processed_tokens < original_tokens  # Check token reduction

class TestUtils:
    def test_format_api_info_basic(self):
        """Test basic API info formatting."""
        api_info = APIInfo(
            classes=[
                Class(
                    name="TestClass",
                    description="A test class",
                    methods=[
                        Method(
                            name="test_method",
                            description="A test method",
                            params=[
                                Parameter(
                                    name="param1",
                                    type="str",
                                    default="'default'"
                                )
                            ],
                            returns="str",
                            exceptions=[]
                        )
                    ]
                )
            ],
            functions=[]
        )
        
        formatter = OutputFormatter()
        
        # Show input configuration
        formatter.format_section(OutputSection(
            title="CONFIGURATION",
            content={
                "API Info Structure": {
                    "Classes": len(api_info.classes),
                    "Class Details": [{
                        "Name": cls.name,
                        "Description": cls.description,
                        "Methods": [m.name for m in cls.methods]
                    } for cls in api_info.classes]
                }
            }
        ))
        
        # Format API info
        result = format_api_info(api_info)
        
        # Show verification
        formatter.format_section(OutputSection(
            title="VERIFICATION",
            content={
                "Has Class": "class TestClass:" in result,
                "Has Description": "# A test class" in result,
                "Has Method": "def test_method" in result,
                "Has Params": "param1: str = 'default'" in result,
                "Has Return": "-> str" in result
            }
        ))
        
        # Run assertions
        assert "class TestClass:" in result
        assert "# A test class" in result
        assert "def test_method" in result
        assert "param1: str = 'default'" in result
        assert "-> str" in result
    
    def test_format_api_info_none(self):
        """Test API info formatting with None."""
        with pytest.raises(ValueError) as exc:
            format_api_info(None)
        assert "api_info cannot be None" in str(exc.value)

# Integration Tests
class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline(self, client, complex_api_info, verbose_content):
        """Test complete processing pipeline."""
        formatter = OutputFormatter()
        
        # Process content
        result = await client.summarize_section(verbose_content, level=3)
        
        # Show input/output comparison
        formatter.format_comparison(verbose_content, result)
        
        # Show verification results
        formatter.format_section(OutputSection(
            title="VERIFICATION",
            content={
                "Has CLI Guide": "CLI Usage Guide" in result,
                "Has code blocks": "```" in result,
                "Has tables": "|" in result,
                "Structure preserved": all([
                    "### CLI Usage Guide" in result,
                    "```python" in result,
                    "```bash" in result
                ])
            }
        ))
        
        # Run assertions
        assert "### CLI Usage Guide" in result
        assert "```python" in result
        assert "```bash" in result
        assert "|" in result
        assert result.count("```") <= 6
    
    @pytest.mark.asyncio
    async def test_with_child_summaries(self, client, basic_api_info):
        """Test processing with child summaries."""
        content = """## Parent Section
Overview of functionality.
"""
        child_summaries = [
            "Child 1: Basic parsing",
            "Child 2: Advanced features"
        ]
        
        formatter = OutputFormatter()
        
        # Show input configuration
        formatter.format_section(OutputSection(
            title="CONFIGURATION",
            content={
                "Parent Content": content,
                "Child Summaries": child_summaries,
                "Level": 2,
                "Input Tokens": count_tokens(content)
            }
        ))
        
        # Process content
        result = await client.summarize_section(
            content, 
            level=2,
            child_summaries=child_summaries
        )
        
        # Show output and verification
        formatter.format_section(OutputSection(
            title="OUTPUT",
            content={
                "Result": result,
                "Output Tokens": count_tokens(result),
                "Has Parent": "## Parent Section" in result,
                "Has Child 1": "Basic parsing" in result,
                "Has Child 2": "Advanced features" in result,
                "Has Subsections Header": "Subsections:" in result
            }
        ))
        
        # Run assertions
        assert "## Parent Section" in result
        assert "Basic parsing" in result
        assert "Advanced features" in result
        assert "Subsections:" in result  # Verify section header
        
        # For small content, total tokens should be reasonable
        # Original content + child summaries + some formatting
        total_input_tokens = count_tokens(content) + sum(count_tokens(s) for s in child_summaries)
        result_tokens = count_tokens(result)
        assert result_tokens <= total_input_tokens + 15  # Allow a few tokens for formatting

# Error Handling Tests
class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_empty_content_error(self, client):
        """Test error handling for empty content."""
        with pytest.raises(ValueError) as exc:
            await client.summarize_section("", level=1)
        assert "content cannot be empty" in str(exc.value)        

# Add YAML conversion tests
class TestYAMLConversion:
    """Tests for YAML conversion functionality."""
    
    @pytest.mark.asyncio
    async def test_convert_simple_markdown(self, client):
        """Should convert basic markdown to YAML."""
        markdown = """# Title
Simple content"""
        result = await client.convert_to_yaml(markdown)
        assert "title:" in result.lower()
        assert "simple content" in result.lower()

    @pytest.mark.asyncio
    async def test_convert_with_code_block(self, client):
        """Should preserve code blocks in YAML conversion."""
        markdown = """# Title
Example code:
    def hello():
        print("world")
"""
        result = await client.convert_to_yaml(markdown)
        assert "def hello()" in result
        assert "print" in result

    @pytest.mark.asyncio
    async def test_convert_with_tables(self, client):
        """Should preserve table formatting in YAML."""
        markdown = """# Title
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |"""
        result = await client.convert_to_yaml(markdown)
        assert "|" in result
        assert "Header 1" in result

    @pytest.mark.asyncio
    async def test_convert_error_handling(self, client):
        """Should handle conversion errors gracefully."""
        client.model = "invalid-model"
        with pytest.raises(ValueError) as exc:
            await client.convert_to_yaml("# Test")
        assert "Failed to get response" in str(exc.value)

# Add token counting tests
class TestTokenCounting:
    def test_count_tokens(self):
        """Should accurately count tokens."""
        text = "Hello world, this is a test."
        tokens = count_tokens(text)
        assert tokens > 0
        assert tokens < len(text)  # Tokens should be fewer than chars

    def test_count_tokens_with_code(self):
        """Should handle code blocks in token counting."""
        text = """Some text
```python
def test():
    pass
```"""
        tokens = count_tokens(text)
        assert tokens > 0

# Add section filtering tests
class TestSectionFiltering:
    @pytest.mark.asyncio
    async def test_filter_by_level(self, client, verbose_content):
        """Should filter sections by level."""
        formatter = OutputFormatter()
        
        # Show input
        formatter.format_section(OutputSection(
            title="INPUT",
            content={
                "Content": verbose_content,
                "Target Level": 2,
                "Has Level 3": "###" in verbose_content,
                "Header Count": verbose_content.count("#"),
                "Section Count": verbose_content.count("###")
            }
        ))
        
        result = await client.summarize_section(verbose_content, level=2)
        
        # Show output
        formatter.format_section(OutputSection(
            title="OUTPUT",
            content={
                "Content": result,
                "Has Level 3": "###" in result,
                "Header Count": result.count("#"),
                "Section Count": result.count("###"),
                "Expected Level": "##" in result
            }
        ))
        
        # Content structure checks
        assert "###" not in result  # Should not include level 3
        assert "## CLI Usage Guide" in result  # Should convert to level 2
        assert "```bash" in result  # Should preserve code blocks
        assert "|" in result  # Should preserve tables
