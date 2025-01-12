import pytest
from src.md_parser import MarkdownParser
import logging


def test_hierarchical_section_parsing():
    """Test parsing markdown into hierarchical sections."""
    content = """# Main Section
This is the main content.

## Sub Section 1
Some sub content.

### Deep Section
Deeper content with code:
```python
# This is a comment
def test():
    # More comments
    pass
```

## Sub Section 2
More sub content.

# Another Main
Second main section content."""

    parser = MarkdownParser()
    sections = parser.parse(content)
    
    # Show the structure
    def print_section(section, indent=0):
        print(f"{'  ' * indent}[{section.level}] {section.title}")
        for sub in section.sections.values():
            print_section(sub, indent + 1)
    
    print("\nSection Structure:")
    print("-----------------")
    for section in sections.values():
        print_section(section)
    
    # Verify structure
    assert len(sections) == 2  # Two level 1 sections
    
    # Check first main section
    main = sections['main_section']
    assert main.title == "Main Section"
    assert main.level == 1
    assert "This is the main content" in main.content
    assert len(main.sections) == 2  # Two subsections
    
    # Check first subsection
    sub1 = main.sections['sub_section_1']
    assert sub1.title == "Sub Section 1"
    assert sub1.level == 2
    assert "Some sub content" in sub1.content
    
    # Check deep section
    deep = sub1.sections['deep_section']
    assert deep.title == "Deep Section"
    assert deep.level == 3
    assert "```python" in deep.content
    assert "# This is a comment" in deep.content  # Code block preserved
    
    # Check second subsection
    sub2 = main.sections['sub_section_2']
    assert sub2.title == "Sub Section 2"
    assert sub2.level == 2
    assert "More sub content" in sub2.content
    
    # Check second main section
    another = sections['another_main']
    assert another.title == "Another Main"
    assert another.level == 1
    assert "Second main section" in another.content
    assert len(another.sections) == 0  # No subsections


def test_parsing_starts_at_level_2():
    """Test parsing when document starts at heading level 2."""
    content = """## First Main
This is level 2 content.

### Sub Section A
Level 3 content with code:
```python
def test():
    # This comment shouldn't be a heading
    pass
```

### Sub Section B
More level 3 content.

## Second Main
Another level 2 section.

### Deep Section
With level 3 content."""

    parser = MarkdownParser()
    sections = parser.parse(content)
    
    print("\nSection Structure:")
    print("-----------------")
    for section in sections.values():
        def print_section(section, indent=0):
            print(f"{'  ' * indent}[{section.level}] {section.title}")
            for sub in section.sections.values():
                print_section(sub, indent + 1)
        print_section(section)
    
    # Verify structure
    assert len(sections) == 2  # Two level 2 sections
    
    # Check first section
    first = sections['first_main']
    assert first.title == "First Main"
    assert first.level == 1  # Should be normalized to level 1
    assert "This is level 2 content" in first.content
    assert len(first.sections) == 2  # Two subsections
    
    # Check its subsections
    sub_a = first.sections['sub_section_a']
    assert sub_a.title == "Sub Section A"
    assert sub_a.level == 2  # Should be normalized to level 2
    assert "```python" in sub_a.content
    assert "# This comment" in sub_a.content  # Code block preserved
    
    sub_b = first.sections['sub_section_b']
    assert sub_b.title == "Sub Section B"
    assert sub_b.level == 2
    assert "More level 3 content" in sub_b.content
    
    # Check second main section
    second = sections['second_main']
    assert second.title == "Second Main"
    assert second.level == 1  # Should be normalized to level 1
    assert "Another level 2 section" in second.content
    
    # Check deep section
    deep = second.sections['deep_section']
    assert deep.title == "Deep Section"
    assert deep.level == 2  # Should be normalized to level 2
    assert "With level 3 content" in deep.content
