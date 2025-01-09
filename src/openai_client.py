from typing import Optional, List, Dict, Any
import openai
import asyncio
from openai import AsyncOpenAI

class OpenAIClient:
    """Handles OpenAI API interactions."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def convert_to_yaml(self, markdown: str) -> str:
        """Convert markdown to YAML using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Convert markdown to YAML."},
                    {"role": "user", "content": markdown}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise ValueError(f"Failed to get response from OpenAI: {e}") 