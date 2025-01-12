from openai import AsyncOpenAI
from .types import APIInfo
from .utils import format_api_info
import logging

class CodeSynthesizer:
    """Synthesizes code examples from API information."""
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    async def synthesize(self, content: str, api_info: APIInfo) -> str:
        """Create comprehensive code examples."""
        prompt = """You MUST create exactly THREE separate code blocks. Each block MUST be wrapped in ```python and ```.

        Block 1 - API Interface:
        ```python
        # Show class/method signatures with type hints
        class ClassName:
            def method(param: type) -> return_type:
                '''Docstring'''
        ```

        Block 2 - Basic Usage:
        ```python
        # Show simple example
        instance = ClassName()
        result = instance.method(param)
        ```

        Block 3 - Advanced Usage:
        ```python
        # Show error handling
        try:
            instance = ClassName()
            result = instance.method(param)
        except Exception as e:
            handle_error(e)
        ```

        Rules:
        1. You MUST output exactly 3 code blocks
        2. Each block MUST start with ```python and end with ```
        3. Follow the structure shown above
        4. No text between blocks
        5. No additional blocks
        """
        
        # Convert API info to string representation
        api_str = self._format_api_info(api_info)
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code example generator. Always output exactly 3 code blocks."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"API Info:\n{api_str}\n\nOriginal Examples:\n{content}"}
            ],
            temperature=0.0,  # Use 0 temperature for consistent output
            max_tokens=1000   # Ensure enough tokens for 3 blocks
        )
        
        result = response.choices[0].message.content
        self.logger.debug(f"Raw response: {repr(result)}")
        
        # Clean up the response
        blocks = result.split("```")
        code_blocks = []
        
        # Process blocks between backticks
        for block in blocks[1::2]:  # Get content between backticks
            block = block.strip()
            # Remove python marker and any leading/trailing whitespace
            if block.startswith("python"):
                block = block[6:].lstrip()  # Remove "python" and any following whitespace
            code_blocks.append(block)
        
        # Reconstruct with proper formatting
        formatted_blocks = [
            f"```python\n{block}\n```"
            for block in code_blocks[:3]  # Take first 3 blocks
        ]
        
        return "\n\n".join(formatted_blocks)
    
    def _format_api_info(self, api_info: APIInfo) -> str:
        return format_api_info(api_info) 