import argparse
import asyncio
import os
import logging
from pathlib import Path
from src.config.settings import get_settings
from src.md_summarizer import MarkdownSummarizer
from src.document_agent import DocumentAgent, BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

async def main():
    """Convert markdown documentation to YAML format."""
    parser = argparse.ArgumentParser(description="Convert markdown to YAML")
    parser.add_argument("--input", "-i", help="Input markdown file")
    parser.add_argument("--output", "-o", help="Output YAML file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    args = parser.parse_args()

    # Load settings
    settings = get_settings()
    
    # Initialize client once with model
    agent = DocumentAgent()
    print(f"\nUsing model: {settings.openai_model}")
    
    
    # Require input/output for conversion
    if not args.input or not args.output:
        parser.error("--input and --output are required for conversion")
    
    # Initialize converter with same client
    converter = MarkdownSummarizer(agent)
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")
        
    input_content = input_path.read_text()
    
    # Count tokens with correct model
    input_tokens = BaseAgent.count_tokens(input_content)
    print(f"Input document tokens: {input_tokens}")
    
    # Convert content
    yaml_content = await converter.summarize(input_content)
    output_tokens = BaseAgent.count_tokens(yaml_content)
    print(f"Output document tokens: {output_tokens}")
    print(f"Token reduction: {((input_tokens - output_tokens) / input_tokens * 100):.1f}%\n")
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml_content)
    
    if args.verbose:
        print(f"Converted {args.input} to {args.output}")
        print(f"Total tokens used: {agent.usage.total_tokens}")

if __name__ == "__main__":
    asyncio.run(main()) 