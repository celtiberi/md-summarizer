"""Test output formatting utilities."""
from md_summarizer.agent import SummarizerAgent

star_count = 30

def format_section(title: str, content: str) -> None:
    """Format a section of output with automatically generated stats."""
    # Section header
    
    print("\n" + "⭐️"*star_count)
    print(f"⭐️ {title}")
    print("⭐️"*star_count + "\n")
    
    # Content
    print(f"{content}\n")
    
def format_comparison(input_text: str, output_text: str, agent: SummarizerAgent) -> None:
    """Format input/output comparison with auto-generated stats."""
    # Show reductions
    input_tokens = agent.usage.request_tokens
    output_tokens = agent.usage.response_tokens

    print("\n" + "⭐️"*star_count)
    print("\nReductions:")
    print("-"*20)
    print(f"{'Input Tokens':<20}: {input_tokens}")
    print(f"{'Output Tokens':<20}: {output_tokens}")
    print(f"{'Tokens Reduction':<20}: {(1 - output_tokens/input_tokens):.1%}")