import pytest
from src.md_parser import MarkdownParser

@pytest.fixture
def parser():
    """Create a parser with default settings.
    
    Should:
    1. Create parser with default max_tokens
    2. Create parser with default min_section_level
    
    Returns:
        MarkdownParser: Default configuration
    """
    return MarkdownParser(max_tokens=2000)

@pytest.fixture
def small_parser():
    """Create a parser with small token limit.
    
    Should:
    1. Create parser with small max_tokens for testing splits
    2. Use default min_section_level
    
    Returns:
        MarkdownParser: Small token configuration
    """
    return MarkdownParser(max_tokens=50)

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
    assert "# First\nContent 1" in sections[0]
    assert "# Second\nContent 2" in sections[1]

def test_parser_preserves_code_blocks(parser, tmp_path):
    """Test preservation of code blocks within sections.
    
    Should:
    1. Keep markdown code blocks intact within their sections
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
    code_section = sections[0]
    assert "def example():" in code_section
    assert "print(test)" in code_section
    assert "End of section" in code_section

def test_parser_min_section_level(tmp_path):
    """Test minimum section level handling.
    
    Should:
    1. Only split on headers at or above min_section_level
    2. Keep lower level headers as part of their parent section
    3. Maintain header hierarchy in content
    """
    parser = MarkdownParser(max_tokens=2000, min_section_level=2)
    
    markdown = """# Top Level
Main content

## Section 1
Content 1

### Subsection
Should stay with Section 1

## Section 2
Content 2"""

    test_file = tmp_path / "sections.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 2  # Should only split on ## headers
    assert "## Section 1" in sections[0]
    assert "### Subsection" in sections[0]  # Should stay with parent
    assert "## Section 2" in sections[1]

def test_parser_token_estimation(small_parser, tmp_path):
    """Test token estimation and section splitting.
    
    Should:
    1. Accurately estimate tokens based on content length
    2. Split sections that exceed max_tokens
    3. Keep sections under token limit
    4. Not split in middle of words or lines
    """
    # Create content that should be ~100 tokens
    words = ["word"] * 100  # Each word ~1 token
    markdown = "# Section\n" + " ".join(words)
    
    test_file = tmp_path / "tokens.md"
    test_file.write_text(markdown)
    
    sections = small_parser.parse_file(str(test_file))
    
    # With max_tokens=50, should split into at least 2 sections
    assert len(sections) >= 2
    # Each section should be roughly under 50 tokens
    assert all(len(section.split()) <= 60 for section in sections)
    # First section should contain header
    assert "# Section" in sections[0]

def test_parser_handles_nested_headers(parser, tmp_path):
    """Test handling of nested header hierarchy.
    
    Should:
    1. Maintain header hierarchy in sections
    2. Create separate sections for each header level
    3. Keep content with its correct header
    4. Preserve header levels (##, ###, etc.)
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
    assert "# Main" in sections[0]
    assert "## Sub 1" in sections[1]
    assert "### Sub-sub" in sections[2]
    assert "## Sub 2" in sections[3]

def test_parser_handles_large_content(small_parser, tmp_path):
    """Test splitting of large content sections.
    
    Should:
    1. Split content that exceeds token limit
    2. Maintain content integrity when splitting
    3. Not split in the middle of words
    4. Keep each section under the token limit
    """
    markdown = "# Large Section\n" + "word " * 100

    test_file = tmp_path / "large.md"
    test_file.write_text(markdown)
    
    sections = small_parser.parse_file(str(test_file))
    
    assert len(sections) > 1
    assert all(len(section) <= 50 * 4 for section in sections)
    assert "# Large Section" in sections[0]

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
    assert "\n\n" in sections[0]

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

## First Sub
Sub content 1

# Second
Content 2

## Second Sub
Sub content 2"""
    
    test_file = tmp_path / "order.md"
    test_file.write_text(markdown)
    
    sections = parser.parse_file(str(test_file))
    
    assert len(sections) == 4
    assert "# First" in sections[0]
    assert "## First Sub" in sections[1]
    assert "# Second" in sections[2]
    assert "## Second Sub" in sections[3]
    assert "Content 1" in sections[0]
    assert "Sub content 1" in sections[1]
    assert "Content 2" in sections[2]
    assert "Sub content 2" in sections[3]
