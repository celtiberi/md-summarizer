"""Test output formatting utilities."""
from src.summarizer.utils import count_tokens
from src.config.settings import get_settings

star_count = 30

def format_section(title: str, content: str) -> None:
    """Format a section of output with automatically generated stats."""
    # Section header
    
    print("\n" + "⭐️"*star_count)
    print(f"⭐️ {title}")
    print("⭐️"*star_count + "\n")
    
    # Content
    print(f"{content}\n")
    
def print_stats(content: str) -> None:
    """Print statistics about the content."""
    print("Statistics:")
    print("-"*20)
    print(f"{'Length':<20}: {len(content)}")
    print(f"{'Tokens':<20}: {count_tokens(content)}")
    print(f"{'Model':<20}: {get_settings().openai_model}")

def format_comparison(input_text: str, output_text: str) -> None:
    """Format input/output comparison with auto-generated stats."""
    # Show input
    format_section("INPUT", input_text)
    
    # Show output with reduction stats
    format_section("OUTPUT", output_text)
    
    # Show reductions
    input_tokens = count_tokens(input_text)
    output_tokens = count_tokens(output_text)
    print("\n" + "⭐️"*star_count)
    print("\nReductions:")
    print("-"*20)
    print(f"{'Tokens':<20}: {(1 - output_tokens/input_tokens):.1%}")
    print(f"{'Length':<20}: {(1 - len(output_text)/len(input_text)):.1%}") 