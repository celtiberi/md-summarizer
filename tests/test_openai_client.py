import pytest
from src.openai_client import OpenAIClient
import yaml

@pytest.mark.asyncio
async def test_convert_simple_markdown(client):
    """Test basic markdown to YAML conversion.
    
    Should:
    1. Convert simple markdown to valid YAML
    2. Preserve header hierarchy
    3. Maintain content under headers
    """
    markdown = """# Title
Simple content"""
    
    result = await client.convert_to_yaml(markdown)
    assert "title:" in result.lower()
    assert "simple content" in result.lower()

@pytest.mark.asyncio
async def test_convert_with_code_block(client):
    """Test conversion with code blocks.
    
    Should:
    1. Preserve code block formatting
    2. Keep code indentation
    3. Maintain code block markers
    """
    markdown = """# Title
Example code:

    def hello():
        print("world")
"""
    result = await client.convert_to_yaml(markdown)
    assert "def hello()" in result
    assert "print" in result

@pytest.mark.asyncio
async def test_convert_error_handling(client):
    """Test API error handling.
    
    Should:
    1. Handle API errors gracefully
    2. Raise clear error messages
    """
    # Test with invalid model to trigger real API error
    client.model = "invalid-model"
    
    with pytest.raises(ValueError) as exc:
        await client.convert_to_yaml("# Test")
    assert "Failed to get response from OpenAI" in str(exc.value)

@pytest.mark.asyncio
async def test_retry_behavior(client):
    """Test OpenAI client retry behavior.
    
    Should:
    1. Handle API errors gracefully
    2. Return clear error messages
    """
    # Test with invalid API key to trigger auth error
    client.client.api_key = "invalid-key"
    
    with pytest.raises(ValueError) as exc:
        await client.convert_to_yaml("# Test\nContent")
    assert "Failed to get response from OpenAI" in str(exc.value)

@pytest.mark.asyncio
async def test_yaml_structure(client):
    """Test YAML output structure.
    
    Should:
    1. Produce valid YAML
    2. Maintain header hierarchy
    3. Preserve content relationships
    4. Handle special characters and lists
    """
    markdown = """# Title
Content with *formatting*

## Section 1
- List item 1
- List item 2

### Subsection
1. Numbered item
2. Another item"""
    
    result = await client.convert_to_yaml(markdown)
    data = yaml.safe_load(result)
    
    # Verify structure
    assert isinstance(data, dict)
    assert "title" in data or "Title" in data
    assert isinstance(data.get("section_1", {}), dict)
    assert "subsection" in str(data).lower()
    assert "list item" in str(data).lower()
    assert "numbered item" in str(data).lower() 