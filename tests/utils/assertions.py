from md_summarizer import MarkdownSummarizer

def assert_tokens_reduced(summarizer: MarkdownSummarizer) -> bool:
    """Assert that the output uses at least 30% fewer tokens than input.
    
    Args:
        summarizer: The summarizer instance that processed the content
        
    Returns:
        bool: True if output tokens are at least 30% less than input tokens
        
    Raises:
        AssertionError: If output tokens are not reduced by at least 30%
    """
    request_tokens = summarizer.usage().request_tokens
    response_tokens = summarizer.usage().response_tokens
    
    # Calculate minimum required reduction (30%)
    min_reduction = request_tokens * 0.7  # 70% of original tokens
    
    assert response_tokens <= min_reduction, (
        f"Output should use at least 30% fewer tokens than input.\n"
        f"Input tokens: {request_tokens}\n" 
        f"Output tokens: {response_tokens}\n"
        f"Maximum allowed tokens: {min_reduction:.0f}"
    )
    return True