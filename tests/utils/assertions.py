from src.md_summarizer import MarkdownSummarizer

def assert_tokens_reduced(summarizer: MarkdownSummarizer) -> bool:
    """Assert that the output uses fewer tokens than input.
    
    Args:
        summarizer: The summarizer instance that processed the content
        
    Returns:
        bool: True if output tokens < input tokens
        
    Raises:
        AssertionError: If output tokens >= input tokens
    """
    request_tokens = summarizer.usage().request_tokens
    response_tokens = summarizer.usage().response_tokens
    
    assert response_tokens < request_tokens, (
        f"Output should use fewer tokens than input.\n"
        f"Input tokens: {request_tokens}\n"
        f"Output tokens: {response_tokens}"
    )
    return True 