"""Prompts for YAML conversion."""

def get_yaml_conversion_prompt() -> str:
    """Get prompt for converting markdown to YAML."""
    return """Convert this markdown to YAML while:
    1. Preserving all content
    2. Maintaining proper YAML structure
    3. Converting headers to keys
    4. Preserving code blocks and formatting
    
    Example:
    Input:
    # Title
    Content here
    
    Output:
    title: Title
    content: Content here
    """

def get_yaml_system_prompt() -> str:
    """Get system prompt for YAML conversion."""
    return "Convert markdown to YAML format." 