import pytest
from src.md_parser import MarkdownParser

def test_parser_basic_header_splitting(parser, tmp_path):
    """Test basic header-based section splitting.
    
    Should:
    1. Split content into sections based on headers
    2. Include the header in each section
    3. Maintain the content following each header
    """
    markdown = """# First
Content 1

# Second
Content 2"""
    
    test_file = tmp_path / "basic.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 2
    assert sections[0] == "# First\nContent 1"
    assert sections[1] == "# Second\nContent 2"

def test_parser_preserves_code_blocks(parser, tmp_path):
    """Test preservation of code blocks within sections.
    
    Should:
    1. Keep markdown code blocks intact
    2. Preserve code block markers (```)
    3. Not split sections within code blocks
    4. Maintain code indentation and formatting
    """
    markdown = """# Code Section
Here's some code:

    # Python code block
    def example():
        print("hello")
        return True

Here's a markdown code block:

    # This is a code block
    print("test")

End of section"""

    test_file = tmp_path / "code.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 1
    assert sections[0] == markdown  # Use exact match instead of partial matches

def test_parser_handles_nested_headers(parser, tmp_path):
    """Test handling of nested header hierarchy.
    
    Should:
    1. Split on all headers
    2. Keep content with its header
    3. Preserve header levels (##, ###, etc.)
    """
    markdown = """# Main
Main content

## Sub 1
Sub content 1

### Sub-sub
Deeper content

## Sub 2
Sub content 2"""

    test_file = tmp_path / "nested.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 4
    assert sections[0] == "# Main\nMain content"
    assert sections[1] == "## Sub 1\nSub content 1"
    assert sections[2] == "### Sub-sub\nDeeper content"
    assert sections[3] == "## Sub 2\nSub content 2"

def test_parser_handles_empty_and_whitespace(parser, tmp_path):
    """Test handling of empty and whitespace-only content.
    
    Should:
    1. Handle empty files gracefully
    2. Handle whitespace-only files
    3. Skip empty sections
    4. Preserve intentional empty lines between content
    """
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("")
    assert len(parser.parse_file(str(empty_file))) == 0
    
    whitespace_file = tmp_path / "whitespace.md"
    whitespace_file.write_text("   \n\n   \n")
    assert len(parser.parse_file(str(whitespace_file))) == 0
    
    content_file = tmp_path / "content.md"
    content_file.write_text("# Header\n\nContent\n\nMore content")
    sections = parser.parse_file(str(content_file))
    assert len(sections) == 1
    assert sections[0] == "# Header\n\nContent\n\nMore content"

def test_parser_error_handling(parser):
    """Test error handling for various failure cases.
    
    Should:
    1. Raise appropriate error for missing files
    2. Include helpful error messages
    3. Not raise errors for valid markdown variations
    """
    with pytest.raises(ValueError) as exc:
        parser.parse_file("nonexistent.md")
    assert "Could not read file" in str(exc.value)

def test_parser_preserves_section_order(parser, tmp_path):
    """Test that parser maintains the original order of markdown sections.
    
    Should:
    1. Preserve the exact order of sections as they appear in the markdown
    2. Keep the hierarchical relationship between sections
    3. Include all section content in the correct section
    """
    markdown = """# First
Content 1

# Second
Content 2

# Third
Content 3"""
    
    test_file = tmp_path / "order.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 3
    assert sections[0] == "# First\nContent 1"
    assert sections[1] == "# Second\nContent 2"
    assert sections[2] == "# Third\nContent 3"

def test_parser_preserves_fenced_code_blocks(parser, tmp_path):
    """Test preservation of fenced code blocks.
    
    Should:
    1. Keep fenced code blocks intact
    2. Preserve language specification
    3. Not split sections within code blocks
    4. Maintain code formatting
    """
    markdown = """# Code Section
Here's some code:

```python
def example():
    print("hello")
    return True
```

Here's another code block:

```
print("test")
```

End of section"""

    test_file = tmp_path / "fenced_code.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 1
    assert sections[0] == markdown  # Use exact match

def test_debug_section_content(parser, tmp_path):
    """Debug test to show exact content differences."""
    markdown = """# First
Content 1

# Second 
Content 2"""
    
    test_file = tmp_path / "debug.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    print("\nActual sections:")
    for i, section in enumerate(sections):
        print(f"\nSection {i}:")
        print(repr(section))
    
    print("\nExpected sections:")
    print(repr("# First\nContent 1"))
    print(repr("# Second\nContent 2"))
