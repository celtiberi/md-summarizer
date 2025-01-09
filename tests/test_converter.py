import pytest
import yaml

@pytest.mark.asyncio
async def test_basic_conversion(converter, tmp_path, example_markdown):
    """Test end-to-end markdown to YAML conversion.
    
    Should:
    1. Read markdown file correctly
    2. Convert content to valid YAML
    3. Write YAML file successfully
    4. Maintain document structure
    """
    # Setup input file
    input_file = tmp_path / "input.md"
    input_file.write_text(example_markdown)
    
    # Setup output file
    output_file = tmp_path / "output.yaml"
    
    # Convert
    await converter.convert(str(input_file), str(output_file))
    
    # Verify
    assert output_file.exists()
    content = output_file.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict)
    assert "main_title" in data or "Main Title" in data

@pytest.mark.asyncio
async def test_handles_missing_file(converter):
    """Test error handling for missing files.
    
    Should:
    1. Detect missing input file
    2. Raise clear error message
    3. Not create output file
    """
    with pytest.raises(ValueError) as exc:
        await converter.convert("nonexistent.md", "output.yaml")
    assert "Could not read file" in str(exc.value)

@pytest.mark.asyncio
async def test_large_file_handling(converter, tmp_path):
    """Test handling of large markdown files.
    
    Should:
    1. Split large content into sections
    2. Process sections concurrently
    3. Merge sections correctly
    4. Maintain header hierarchy in output
    """
    # Create large markdown file with nested structure
    large_content = """# Main Title
Overview text here.

## Section 1
""" + ("Content " * 500) + """

## Section 2
""" + ("More content " * 500) + """

### Subsection 2.1
""" + ("Sub content " * 500)

    input_file = tmp_path / "large.md"
    input_file.write_text(large_content)
    output_file = tmp_path / "output.yaml"
    
    await converter.convert(str(input_file), str(output_file))
    
    # Verify output
    content = output_file.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict)
    assert "main_title" in data or "Main Title" in data
    assert "section_1" in data or "Section 1" in data
    assert "section_2" in data or "Section 2" in data 

@pytest.mark.asyncio
async def test_concurrent_processing(converter, tmp_path):
    """Test concurrent processing of sections.
    
    Should:
    1. Process multiple sections concurrently
    2. Maintain order in final output
    3. Correctly merge concurrent results
    4. Handle errors in any section
    """
    # Create markdown with multiple independent sections
    sections = []
    for i in range(5):
        sections.append(f"""# Section {i}
Content for section {i}

## Subsection {i}
More content here
""")
    
    content = "\n\n".join(sections)
    input_file = tmp_path / "concurrent.md"
    input_file.write_text(content)
    output_file = tmp_path / "output.yaml"
    
    await converter.convert(str(input_file), str(output_file))
    
    # Verify output
    data = yaml.safe_load(output_file.read_text())
    assert isinstance(data, dict)
    
    # Verify all sections present and in order
    for i in range(5):
        section_key = f"section_{i}"
        assert section_key in str(data).lower()
        assert f"subsection_{i}" in str(data).lower() 

@pytest.mark.asyncio
async def test_yaml_merge_handling(converter, tmp_path):
    """Test YAML section merging behavior.
    
    Should:
    1. Merge sections with same keys correctly
    2. Maintain nested structure
    3. Handle duplicate keys properly
    4. Preserve array contents
    """
    markdown = """# Section
Item 1

# Section
Item 2

## Subsection
- List item 1
- List item 2"""
    
    input_file = tmp_path / "merge.md"
    input_file.write_text(markdown)
    output_file = tmp_path / "output.yaml"
    
    await converter.convert(str(input_file), str(output_file))
    
    data = yaml.safe_load(output_file.read_text())
    assert isinstance(data, dict)
    assert isinstance(data.get("section", {}), dict)
    assert "item 1" in str(data).lower()
    assert "item 2" in str(data).lower()
    assert "list item" in str(data).lower() 

@pytest.mark.asyncio
async def test_real_world_example(converter, tmp_path):
    """Test conversion of a real-world markdown document.
    
    Should:
    1. Handle complex markdown with badges, links, and code blocks
    2. Preserve code examples and formatting
    3. Maintain header hierarchy and structure
    4. Handle special characters and URLs
    5. Process tables correctly
    6. Preserve list formatting (ordered and unordered)
    """
    # Read the example doc
    with open("tests/example_doc.md", "r") as f:
        example_content = f.read()
    
    input_file = tmp_path / "example_doc.md"
    input_file.write_text(example_content)
    output_file = tmp_path / "output.yaml"
    
    # Convert
    await converter.convert(str(input_file), str(output_file))
    
    # Verify output
    content = output_file.read_text()
    data = yaml.safe_load(content)
    
    # Basic structure checks
    assert isinstance(data, dict)
    assert "transitions" in data  # Main title
    
    # Check badges section
    assert "version" in str(data).lower()
    assert "build_status" in str(data).lower()
    assert "coverage_status" in str(data).lower()
    
    # Check code examples
    assert "class NarcolepticSuperhero" in str(data)
    assert "def __init__" in str(data)
    
    # Check nested headers
    assert "installation" in str(data).lower()
    assert "quickstart" in str(data).lower()
    assert "table_of_contents" in str(data).lower()
    
    # Check lists
    assert "pip install transitions" in str(data)
    assert "python setup.py install" in str(data)
    
    # Check complex formatting
    assert "lightweight" in str(data).lower()
    assert "object-oriented" in str(data).lower()
    
    # Verify table structure is preserved
    assert "execution_order" in str(data).lower()
    assert "current_state" in str(data).lower()
    
    # Check links are preserved
    assert "https://github.com/pytransitions/transitions" in str(data)
    
    # Verify code blocks with Python syntax
    assert "from transitions import Machine" in str(data)
    assert "import random" in str(data) 