import asyncio
import argparse
import logging
import os
from src.converter import MarkdownToYamlConverter
from src.config.settings import get_settings

async def convert_file(input_path: str, output_path: str) -> None:
    """Convert markdown file to YAML."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Force test environment
        os.environ['ENV'] = 'test'
        
        # Get settings
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in settings")
        
        # Initialize converter with API key
        converter = MarkdownToYamlConverter(api_key=settings.openai_api_key)
        
        # Convert file
        logger.info(f"Converting {input_path} to {output_path}")
        await converter.convert(input_path, output_path)
        logger.info("Conversion complete!")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        raise

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert markdown to YAML using AI')
    parser.add_argument('input', help='Input markdown file path')
    parser.add_argument(
        '-o', '--output',
        help='Output YAML file path (default: input_file.yaml)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Default output path if not specified
    output_path = args.output or f"{args.input.rsplit('.', 1)[0]}.yaml"
    
    # Run conversion
    asyncio.run(convert_file(args.input, output_path))

if __name__ == "__main__":
    main() 