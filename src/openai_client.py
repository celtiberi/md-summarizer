from typing import Optional, List, Dict, Any
import openai
import asyncio
from openai import AsyncOpenAI
import logging

class OpenAIClient:
    """Handles OpenAI API interactions."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def convert_to_yaml(self, markdown: str) -> str:
        """Convert markdown to YAML using OpenAI."""
        try:
            logger = logging.getLogger(__name__)
            logger.info(f"Converting markdown:\n{markdown}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """Convert markdown to YAML following these rules:
                    - Extract the header text and content
                    - Create a YAML object with two fields:
                      1. title: The header text in lowercase with underscores
                      2. content: The content text as a block scalar (|)
                    - Escape any special characters in the content
                    - Validate the YAML before returning
                    
                    Example 1 (Basic content):
                    # Main Title
                    This is some content.
                    
                    Output 1:
                    main_title:
                      content: |
                        This is some content.

                    Example 2 (Special characters):
                    ## Section 1
                    Content with special chars: & < > "
                    And a second line.
                    
                    Output 2:
                    section_1:
                      content: |
                        Content with special chars: & < > "
                        And a second line.

                    Example 3 (Code blocks):
                    ### Code Example
                    Here's some code:
                        def example():
                            return True
                    
                    Output 3:
                    code_example:
                      content: |
                        Here's some code:
                            def example():
                                return True

                    Example 4 (Lists):
                    ## Features
                    - Item 1
                    - Item 2
                      - Subitem
                    
                    Output 4:
                    features:
                      content: |
                        - Item 1
                        - Item 2
                          - Subitem
                    """},
                    {"role": "user", "content": markdown}
                ],
                temperature=0.0
            )
            yaml_str = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response:\n{yaml_str}")
            return yaml_str
        except Exception as e:
            logger.error(f"OpenAI conversion failed: {e}", exc_info=True)
            raise ValueError(f"Failed to get response from OpenAI: {e}") 